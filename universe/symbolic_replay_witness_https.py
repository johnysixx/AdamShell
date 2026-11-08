"""HTTPS transport for an independently deployed signed witness authority.

The client verifies server TLS certificates with Python's SSLContext, never
allows an HTTP URL, and never follows redirects. A33's pinned Ed25519 public
key remains necessary to authenticate the signed revision separately.

The reference TLS server is intentionally small; expose it only behind
appropriate firewall/rate limits, or a hardened TLS reverse proxy.
"""
import hmac
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from universe.symbolic_replay_authenticated_witness import (
    SignedSymbolicReplayWitnessSource,
)
from universe.symbolic_replay_witness_wire import (
    dumps_canonical,
    loads_strict,
    signed_from_wire,
    signed_to_wire,
    witness_from_wire,
    witness_to_wire,
)

_MAX_BODY = 65536


class HttpsSignedWitnessSource(SignedSymbolicReplayWitnessSource):
    """External TLS client; no local checkpoint fallback."""

    def __init__(
        self, base_url, *, token=None, ssl_context=None, timeout=10,
    ):
        if type(base_url) is not str:
            raise TypeError("Witness authority URL must be text.")
        parsed = urllib.parse.urlsplit(base_url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or parsed.path not in ("", "/")
        ):
            raise ValueError("Witness authority requires a clean HTTPS URL.")
        if type(timeout) not in (float, int) or timeout <= 0:
            raise ValueError("Witness timeout must be positive.")
        if ssl_context is not None and not isinstance(
            ssl_context, ssl.SSLContext
        ):
            raise TypeError("TLS context must be SSLContext.")
        if token is not None and (type(token) is not str or not token):
            raise ValueError("Witness write token must be nonempty.")

        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.context = (
            ssl.create_default_context()
            if ssl_context is None else ssl_context
        )
        if (
            self.context.verify_mode != ssl.CERT_REQUIRED
            or not self.context.check_hostname
        ):
            raise ValueError("Witness TLS certificate verification is required.")

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, url):
                return None

        self._opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=self.context),
            NoRedirect(),
        )

    def _request(self, route, data, *, authenticated=False):
        if authenticated and self.token is None:
            raise PermissionError("Witness authority write token missing.")

        headers = {"Content-Type": "application/json"}
        if authenticated:
            headers["Authorization"] = "Bearer " + self.token

        request = urllib.request.Request(
            self.base_url + route,
            data=dumps_canonical(data),
            headers=headers,
            method="POST",
        )
        try:
            with self._opener.open(
                request, timeout=self.timeout,
            ) as response:
                raw = response.read(_MAX_BODY + 1)
                if len(raw) > _MAX_BODY:
                    raise ValueError("Witness response too large.")
        except urllib.error.HTTPError as error:
            if error.code == 401:
                raise PermissionError(
                    "Witness authority rejected write token."
                ) from error
            if error.code == 404:
                raise KeyError(
                    "Witness authority scope not provisioned."
                ) from error
            if error.code == 409:
                raise RuntimeError(
                    "Stale witness authority revision."
                ) from error
            if error.code == 400:
                raise ValueError(
                    "Witness authority rejected request."
                ) from error
            raise ConnectionError(
                "Witness authority HTTP request failed."
            ) from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise ConnectionError(
                "Witness authority transport unavailable."
            ) from error

        return signed_from_wire(loads_strict(raw))

    def read_current(self, *, universe_id, batch_sha256):
        return self._request(
            "/v1/read",
            {"universe_id": universe_id, "batch_sha256": batch_sha256},
        )

    def publish(self, witness, *, expected_revision):
        return self._request(
            "/v1/publish",
            {
                "witness": witness_to_wire(witness),
                "expected_revision": expected_revision,
            },
            authenticated=True,
        )


class _WitnessRequestHandler(BaseHTTPRequestHandler):
    """Minimal JSON API. All scope provisioning remains offline."""

    def log_message(self, *_args):
        # Avoid URLs and authorization secrets in default access logs.
        return

    def _reply(self, status, document):
        body = dumps_canonical(document)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        if self.headers.get_content_type() != "application/json":
            raise ValueError("JSON content type required.")
        header = self.headers.get("Content-Length")
        if not header or not header.isdecimal():
            raise ValueError("Content-Length required.")
        length = int(header)
        if length <= 0 or length > _MAX_BODY:
            raise ValueError("Invalid request length.")
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise ValueError("Incomplete request body.")
        return loads_strict(raw)

    def do_POST(self):
        if self.path not in ("/v1/read", "/v1/publish"):
            return self._reply(404, {"error": "not_found"})

        if self.path == "/v1/publish":
            authorization = self.headers.get("Authorization", "")
            expected = "Bearer " + self.server.write_token
            if not hmac.compare_digest(authorization, expected):
                return self._reply(401, {"error": "unauthorized"})

        try:
            data = self._body()
            if self.path == "/v1/read":
                if type(data) is not dict or set(data) != {
                    "universe_id", "batch_sha256",
                }:
                    raise ValueError("Invalid read request.")
                signed = self.server.ledger.read_current(
                    universe_id=data["universe_id"],
                    batch_sha256=data["batch_sha256"],
                )
            else:
                if type(data) is not dict or set(data) != {
                    "witness", "expected_revision",
                }:
                    raise ValueError("Invalid publish request.")
                signed = self.server.ledger.publish(
                    witness_from_wire(data["witness"]),
                    expected_revision=data["expected_revision"],
                )
            return self._reply(200, signed_to_wire(signed))
        except KeyError:
            return self._reply(404, {"error": "scope_not_found"})
        except RuntimeError:
            return self._reply(409, {"error": "stale_revision"})
        except (TypeError, ValueError, UnicodeError, json.JSONDecodeError):
            return self._reply(400, {"error": "invalid_request"})
        except Exception:
            # Do not leak internal database contents or exception details.
            return self._reply(503, {"error": "authority_unavailable"})

    def do_GET(self):
        return self._reply(405, {"error": "method_not_allowed"})


def make_https_witness_server(
    *, host, port, ledger, write_token, certfile, keyfile,
):
    """Build a TLS server. Caller owns serve_forever() and shutdown()."""
    if type(write_token) is not str or len(write_token) < 32:
        raise ValueError("Use a random witness token of at least 32 characters.")
    if not hasattr(ledger, "read_current") or not hasattr(ledger, "publish"):
        raise TypeError("Witness server requires a ledger.")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    server = ThreadingHTTPServer(
        (host, port), _WitnessRequestHandler,
    )
    server.daemon_threads = True
    server.ledger = ledger
    server.write_token = write_token
    server.socket = context.wrap_socket(
        server.socket, server_side=True,
    )
    return server
