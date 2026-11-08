"""Operator CLI for a separately deployed signed witness authority.

Commands:
  generate-key --private KEY.pem --public PUBLIC.raw --token-file TOKEN.txt
  provision --db authority.sqlite --universe-id ID --batch-sha256 DIGEST
  export-floor --db authority.sqlite --signing-key KEY.pem --universe-id ID --batch-sha256 DIGEST
  serve --db authority.sqlite --signing-key KEY.pem --token-file TOKEN.txt
        --tls-cert certificate.pem --tls-key tls.key --host HOST --port PORT

Keep all secrets outside the repository and outside local checkpoint rollback.
"""
import argparse
import os
import secrets
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from universe.symbolic_replay_witness_https import (
    make_https_witness_server,
)
from universe.symbolic_replay_witness_sqlite_authority import (
    SQLiteWitnessAuthority,
)
from universe.symbolic_replay_witness_wire import (
    dumps_canonical,
    signed_to_wire,
)


def _read_signer(path):
    payload = Path(path).read_bytes()
    signer = serialization.load_pem_private_key(
        payload, password=None,
    )
    if not isinstance(signer, Ed25519PrivateKey):
        raise TypeError("Authority signing key must be Ed25519.")
    return signer


def _create_secret_file(path, payload):
    path = Path(path)
    if not path.parent.is_dir():
        raise FileNotFoundError("Key output directory missing.")
    fd = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _add_scope_arguments(parser):
    parser.add_argument("--universe-id", required=True)
    parser.add_argument("--batch-sha256", required=True)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Independent symbolic replay witness signer."
    )
    sub = parser.add_subparsers(dest="operation", required=True)

    generate = sub.add_parser("generate-key")
    generate.add_argument("--private", required=True)
    generate.add_argument("--public", required=True)
    generate.add_argument("--token-file", required=True)

    provision = sub.add_parser("provision")
    provision.add_argument("--db", required=True)
    _add_scope_arguments(provision)

    export = sub.add_parser("export-floor")
    export.add_argument("--db", required=True)
    export.add_argument("--signing-key", required=True)
    _add_scope_arguments(export)

    serve = sub.add_parser("serve")
    serve.add_argument("--db", required=True)
    serve.add_argument("--signing-key", required=True)
    serve.add_argument("--token-file", required=True)
    serve.add_argument("--tls-cert", required=True)
    serve.add_argument("--tls-key", required=True)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8443)

    args = parser.parse_args(argv)

    if args.operation == "generate-key":
        outputs = (
            Path(args.private),
            Path(args.public),
            Path(args.token_file),
        )
        if len({path.resolve() for path in outputs}) != 3:
            raise ValueError("Secret output paths must differ.")
        if any(path.exists() for path in outputs):
            raise FileExistsError("Secret output files must be new.")

        signer = Ed25519PrivateKey.generate()
        _create_secret_file(
            args.private,
            signer.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ),
        )
        _create_secret_file(
            args.public,
            signer.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ),
        )
        _create_secret_file(
            args.token_file,
            (secrets.token_urlsafe(48) + "\n").encode("ascii"),
        )
        print(
            "Keys generated. Keep the private key and write token "
            "on the authority host only."
        )

    elif args.operation == "provision":
        SQLiteWitnessAuthority.provision(
            database_path=args.db,
            universe_id=args.universe_id,
            batch_sha256=args.batch_sha256,
        )
        print("New witness scope provisioned at revision 0.")

    elif args.operation == "export-floor":
        ledger = SQLiteWitnessAuthority(
            database_path=args.db,
            signing_key=_read_signer(args.signing_key),
        )
        signed = ledger.read_current(
            universe_id=args.universe_id,
            batch_sha256=args.batch_sha256,
        )
        sys.stdout.buffer.write(
            dumps_canonical(signed_to_wire(signed)) + b"\n"
        )

    elif args.operation == "serve":
        ledger = SQLiteWitnessAuthority(
            database_path=args.db,
            signing_key=_read_signer(args.signing_key),
        )
        token = Path(args.token_file).read_text(
            encoding="ascii"
        ).strip()
        server = make_https_witness_server(
            host=args.host,
            port=args.port,
            ledger=ledger,
            write_token=token,
            certfile=args.tls_cert,
            keyfile=args.tls_key,
        )
        print(
            f"Signed witness HTTPS authority ready at "
            f"{args.host}:{server.server_address[1]}",
            flush=True,
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
