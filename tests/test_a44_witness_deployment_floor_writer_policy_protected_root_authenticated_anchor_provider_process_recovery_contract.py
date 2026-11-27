"""Authenticated provider process recovery contracts.

P01-P09 exercise forced process termination at explicit
transaction and publication boundaries.

P10-P13 exercise independent process serialization,
replay rejection, fence recovery and competing CAS.

All keys and databases belong to temporary test fixtures.
These contracts do not establish power-loss resistance
or independent hardware-backed rollback protection.
"""

import hashlib
import importlib
import json
import os
import secrets
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

from contextlib import closing
from dataclasses import fields, is_dataclass
from pathlib import Path
from unittest.mock import patch

import cryptography
import pytest

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
)

import test_a44_witness_deployment_floor_writer_policy_protected_root_authenticated_anchor_provider_contract as base


ROOT = Path(__file__).resolve().parents[1]

PREFIX = (
    "core.existence.history_receipt_trust_checkpoint_"
    "protected_provisioning_witness_deployment_floor_"
    "writer_policy_protected_root"
)

provider_module = importlib.import_module(
    PREFIX + "_authenticated_anchor_provider"
)

sqlite_module = importlib.import_module(
    PREFIX + "_sqlite_reference"
)

Provider = (
    provider_module.AuthenticatedProtectedRootAnchorProvider
)

Backend = sqlite_module.SQLiteProtectedRootBackend


def runtime_identity():

    return {
        "version": list(sys.version_info[:3]),
        "pytest": pytest.__version__,
        "pytest_file": str(Path(pytest.__file__).resolve()),
        "cryptography": cryptography.__version__,
        "cryptography_file": str(
            Path(cryptography.__file__).resolve()
        ),
        "sqlite": sqlite3.sqlite_version,
    }


def encode(value):

    if value is None or type(value) in (
        str, int, bool, float
    ):
        return value

    if type(value) is bytes:
        return {
            "kind": "bytes",
            "value": value.hex(),
        }

    if type(value) is tuple:
        return {
            "kind": "tuple",
            "value": [encode(item) for item in value],
        }

    if is_dataclass(value) and not isinstance(value, type):

        cls = type(value)

        if not cls.__module__.startswith("core."):
            raise TypeError("Unexpected fixture module")

        return {
            "kind": "dataclass",
            "module": cls.__module__,
            "class": cls.__name__,
            "fields": {
                field.name: encode(
                    getattr(value, field.name)
                )
                for field in fields(value)
                if field.init
            },
        }

    raise TypeError(
        "Unsupported fixture type: "
        + type(value).__name__
    )


def decode(value):

    if value is None or type(value) in (
        str, int, bool, float
    ):
        return value

    kind = value["kind"]

    if kind == "bytes":
        return bytes.fromhex(value["value"])

    if kind == "tuple":
        return tuple(
            decode(item) for item in value["value"]
        )

    if kind == "dataclass":

        if not value["module"].startswith("core."):
            raise TypeError("Unexpected fixture module")

        cls = getattr(
            importlib.import_module(value["module"]),
            value["class"],
        )

        if not is_dataclass(cls):
            raise TypeError("Expected fixture dataclass")

        return cls(**{
            name: decode(item)
            for name, item in value["fields"].items()
        })

    raise TypeError("Unknown fixture encoding")


def publish_json(path, record):

    temporary = path.with_suffix(".tmp")

    with temporary.open("x", encoding="utf-8") as handle:

        json.dump(record, handle)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temporary, path)



def _read_signal_text(path, deadline):

    # Windows may temporarily deny access to an atomically
    # published signal file. Retry only file access errors.
    # Never extend the caller's original deadline.

    while True:

        if time.monotonic() >= deadline:
            raise TimeoutError(
                "Signal file read deadline exceeded: "
                + str(path)
            )

        try:
            return path.read_text(encoding="utf-8")

        except (PermissionError, FileNotFoundError) as exc:

            remaining = deadline - time.monotonic()

            if remaining <= 0:
                raise TimeoutError(
                    "Signal file unavailable: " + str(path)
                ) from exc

            time.sleep(min(0.05, remaining))


def worker_main(data):

    from contextlib import contextmanager

    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )

    directory = Path(data["directory"]).resolve()
    mode = data["mode"]

    def publish(name, payload=None):

        publish_json(
            directory / (name + ".json"),
            {
                "pid": os.getpid(),
                "ppid": os.getppid(),
                "token": data["token"],
                "event": name,
                "payload": payload,
            },
        )

    def wait_command(name, timeout=90):

        target = directory / (name + ".json")
        deadline = time.monotonic() + timeout

        while not target.is_file():

            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Worker command timeout: " + name
                )

            time.sleep(0.05)

        record = json.loads(
            _read_signal_text(target, deadline)
        )

        if record != {
            "pid": os.getpid(),
            "token": data["token"],
        }:
            raise RuntimeError(
                "Invalid command identity"
            )

    publish("ready", runtime_identity())
    wait_command("authorize", timeout=30)

    initial = decode(data["initial"])
    pending = decode(data["pending"])
    enrollment = decode(data["enrollment"])

    signer = Ed25519PrivateKey.from_private_bytes(
        bytes.fromhex(data["test_private_key"])
    )

    path = Path(data["database"]).resolve()
    session = bytes.fromhex(data["session"])

    if path.is_relative_to(ROOT):
        raise RuntimeError("Non-temporary database")

    if not path.is_relative_to(
        Path(tempfile.gettempdir()).resolve()
    ):
        raise RuntimeError("Database outside temporary storage")

    registry = importlib.import_module(
        PREFIX + "_anchor_session_registry"
    )

    storage = importlib.import_module(
        PREFIX + "_sqlite_storage"
    )

    original_exclusive = Backend.exclusive
    fence_observed = False

    @contextmanager
    def observe_exclusive(instance):

        nonlocal fence_observed

        if not fence_observed:
            fence_observed = True
            publish("fence_attempt")

        with original_exclusive(instance):
            yield

    with patch.object(
        Backend,
        "exclusive",
        new=observe_exclusive,
    ):

        backend = Backend.open(
            path=path,
            expected_identity=initial.identity,
        )

        provider = Provider.from_backend(
            backend=backend,
            enrollment=enrollment,
            signer=signer,
        )

        original_reserve = provider_module.reserve_session
        original_registry_reserve = registry._reserve_in_transaction
        original_signed = Provider._signed
        original_cas = Backend.compare_and_set
        original_transaction = storage._transaction

        signed_operations = []
        cas_active = False
        entered = False
        cas_committed = False
        cas_rejected = False
        rejection = None

        def checkpoint(label, details=None):

            if label != mode:
                raise RuntimeError("Unexpected crash checkpoint")

            key = backend._storage.fence_path

            if key not in sqlite_module._active_leases():
                raise RuntimeError("Missing active fence")

            if key not in provider_module._active_provider_owners():
                raise RuntimeError("Missing provider ownership")

            publish(
                "checkpoint",
                {
                    "scenario": label,
                    "database": str(path),
                    "session": session.hex(),
                    "signed_operations": list(signed_operations),
                    "details": details,
                },
            )

            # No command is issued for a crash checkpoint.
            # The verified worker must be forcibly terminated.

            wait_command("continue_crash")

            raise RuntimeError(
                "Crash checkpoint returned unexpectedly"
            )

        def reserve(**kwargs):

            if mode == "P01":
                checkpoint("P01")

            return original_reserve(**kwargs)

        def reserve_transaction(connection, binding, nonce):

            original_registry_reserve(
                connection,
                binding,
                nonce,
            )

            if mode == "P02":

                if not connection.in_transaction:
                    raise RuntimeError(
                        "Reservation transaction inactive"
                    )

                if connection.execute(
                    "SELECT session FROM consumed_sessions "
                    "WHERE session = ?",
                    (nonce,),
                ).fetchone() != (nonce,):

                    raise RuntimeError(
                        "Uncommitted reservation missing"
                    )

                checkpoint(
                    "P02",
                    {"transaction_active": True},
                )

        def sign(instance, **kwargs):

            operation = kwargs["operation"]

            if mode == "P03" and operation == "hold":
                checkpoint("P03")

            if mode == "P06" and operation == "cas":
                checkpoint("P06")

            response = original_signed(instance, **kwargs)

            signed_operations.append(operation)

            return response

        def dispatch_cas(instance, **kwargs):

            nonlocal cas_active

            if mode == "P05":
                checkpoint("P05")

            cas_active = True

            try:
                return original_cas(instance, **kwargs)
            finally:
                cas_active = False

        @contextmanager
        def observe_transaction(db_path, *args, **kwargs):

            with original_transaction(
                db_path, *args, **kwargs
            ) as connection:

                yield connection

                if (
                    mode == "P09"
                    and cas_active
                    and Path(db_path).resolve() == path
                    and kwargs.get("write") is True
                ):

                    if not connection.in_transaction:
                        raise RuntimeError(
                            "CAS transaction already ended"
                        )

                    state = storage._read_state(
                        connection,
                        backend._storage,
                    )

                    if state != pending:
                        raise RuntimeError(
                            "Uncommitted replacement missing"
                        )

                    checkpoint(
                        "P09",
                        {
                            "revision": state.revision,
                            "transaction_active": True,
                        },
                    )

        with (
            patch.object(
                provider_module,
                "reserve_session",
                new=reserve,
            ),
            patch.object(
                registry,
                "_reserve_in_transaction",
                new=reserve_transaction,
            ),
            patch.object(
                Provider,
                "_signed",
                new=sign,
            ),
            patch.object(
                Backend,
                "compare_and_set",
                new=dispatch_cas,
            ),
            patch.object(
                storage,
                "_transaction",
                new=observe_transaction,
            ),
        ):

            try:

                with provider.hold(
                    session=session,
                ) as response:

                    entered = True
                    held = response[0]

                    if held not in (initial, pending):
                        raise RuntimeError("Unexpected HOLD state")

                    publish(
                        "hold_entered",
                        {"revision": held.revision},
                    )

                    if mode == "P04":
                        checkpoint("P04")

                    if mode in {"owner", "owner_cas"}:
                        wait_command("release")

                    if mode in {
                        "P05", "P06", "P07", "P09",
                        "owner_cas", "contender_cas",
                    }:

                        try:

                            response = provider.compare_and_set(
                                session=session,
                                challenge=b"c" * 32,
                                expected=initial.reference(),
                                replacement=pending,
                            )

                        except ValueError:

                            if mode != "contender_cas":
                                raise

                            cas_rejected = True
                            raise

                        else:

                            if response[0] != pending:
                                raise RuntimeError(
                                    "Unexpected CAS replacement"
                                )

                            held = response[0]
                            cas_committed = True

                            if mode == "P07":
                                checkpoint("P07")

                    response = provider.finish(
                        session=session,
                        challenge=b"f" * 32,
                        expected=held.reference(),
                    )

                    if response[0] != held:
                        raise RuntimeError("Unexpected FINISH state")

                    if mode == "P08":
                        checkpoint("P08")

            except ValueError as exc:

                if mode not in {"read", "contender_cas"}:
                    raise

                rejection = str(exc)

        if mode.startswith("P"):
            raise RuntimeError(
                "Crash worker exited without termination"
            )

        if provider._held.phase != "idle":
            raise RuntimeError("Provider state leaked")

        if provider_module._active_provider_owners():
            raise RuntimeError("Provider ownership leaked")

        if sqlite_module._active_leases():
            raise RuntimeError("Backend lease leaked")

        current = backend.read()

        publish(
            "result",
            {
                "entered": entered,
                "cas_committed": cas_committed,
                "cas_rejected": cas_rejected,
                "rejection": rejection,
                "revision": current.revision,
                "signed_operations": signed_operations,
            },
        )


# Minimal bootstrap using the verified direct interpreter.
# The production fixture module is imported only after
# explicit virtual-environment paths have been restored.

WORKER_BOOTSTRAP = """
import importlib.util
import json
import sys

from pathlib import Path

data = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

sys.path[:] = data["runtime_paths"]

spec = importlib.util.spec_from_file_location(
    "_a44_process_recovery_worker_contract",
    data["contract_file"],
)

module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
module.worker_main(data)
"""


class Worker:

    def __init__(self, case, label, mode, session):

        self.case = case
        self.label = label
        self.mode = mode
        self.session = session
        self.token = secrets.token_hex(32)

        self.directory = case.directory / label
        self.directory.mkdir()

        self.script = self.directory / "worker.py"
        self.manifest = self.directory / "manifest.json"
        self.stdout = self.directory / "stdout.txt"
        self.stderr = self.directory / "stderr.txt"

        self.proc = None
        self.verified = False
        self.authorized = False

        case.addCleanup(self.close)

        self.script.write_text(
            WORKER_BOOTSTRAP,
            encoding="utf-8",
        )

        private_key = case.f.signer.private_bytes(
            Encoding.Raw,
            PrivateFormat.Raw,
            NoEncryption(),
        )

        case.assertEqual(len(private_key), 32)

        paths = [
            str(ROOT),
            str(ROOT / "tests"),
            *sys.path,
        ]

        self.manifest.write_text(
            json.dumps({
                "contract_file": str(Path(__file__).resolve()),
                "directory": str(self.directory),
                "database": str(case.path),
                "runtime_paths": paths,
                "token": self.token,
                "mode": mode,
                "session": session.hex(),
                "initial": encode(case.initial),
                "pending": encode(case.pending),
                "enrollment": encode(case.f.pin),
                "test_private_key": private_key.hex(),
            }),
            encoding="utf-8",
        )

    def start(self):

        with (
            self.stdout.open("wb") as stdout,
            self.stderr.open("wb") as stderr,
        ):

            self.proc = subprocess.Popen(
                [
                    self.case.direct,
                    "-B",
                    "-u",
                    str(self.script),
                    str(self.manifest),
                ],
                cwd=str(ROOT),
                stdout=stdout,
                stderr=stderr,
            )

        ready = self.wait("ready", timeout=20)

        self.case.assertEqual(
            ready,
            runtime_identity(),
        )

        self.case.assertIsNone(self.proc.poll())

        self.verified = True

        self.command("authorize")
        self.authorized = True

        print(
            "VERIFIED WORKER:",
            self.label,
            "PID:",
            self.proc.pid,
            flush=True,
        )

        return self

    def exists(self, name):

        return (
            self.directory / (name + ".json")
        ).is_file()

    def wait(self, name, timeout=40):

        target = self.directory / (name + ".json")
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            if target.is_file():

                record = json.loads(
                    _read_signal_text(target, deadline)
                )

                self.case.assertEqual(
                    record,
                    {
                        "pid": self.proc.pid,
                        "ppid": os.getpid(),
                        "token": self.token,
                        "event": name,
                        "payload": record["payload"],
                    },
                )

                return record["payload"]

            if self.proc.poll() is not None:

                if not target.is_file():
                    break

                continue

            time.sleep(0.05)

        self.case.fail(
            self.label
            + " did not publish "
            + name
            + "\n"
            + self.stderr.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )

    def command(self, name):

        self.case.assertTrue(self.verified)

        publish_json(
            self.directory / (name + ".json"),
            {
                "pid": self.proc.pid,
                "token": self.token,
            },
        )

    def result(self):

        payload = self.wait("result")

        self.case.assertEqual(
            self.proc.wait(timeout=15),
            0,
            self.stderr.read_text(
                encoding="utf-8",
                errors="replace",
            ),
        )

        return payload

    def kill(self):

        self.case.assertTrue(self.verified)
        self.case.assertTrue(self.authorized)
        self.case.assertIsNone(self.proc.poll())

        self.proc.kill()

        code = self.proc.wait(timeout=15)

        self.case.assertNotEqual(code, 0)

        print(
            "PROCESS TERMINATED:",
            self.label,
            "PID:",
            self.proc.pid,
            "EXIT:",
            code,
            flush=True,
        )

    def close(self):

        try:

            if self.proc is not None and self.proc.poll() is None:

                if self.verified:

                    self.proc.kill()
                    self.proc.wait(timeout=15)

                else:

                    self.case.assertFalse(self.authorized)

                    # An unverified worker is not authorized
                    # to open a production backend.

                    try:
                        self.proc.wait(timeout=40)

                    except subprocess.TimeoutExpired:
                        self.proc.kill()
                        self.proc.wait(timeout=15)

        finally:

            self.manifest.unlink(missing_ok=True)


class A44AuthenticatedAnchorProviderProcessRecoveryTests(
    unittest.TestCase
):

    def setUp(self):

        self.f = (
            base.A44AuthenticatedAnchorProviderContractTests(
                "test_01_canonical_immutable_provider_configuration"
            )
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.initial = self.f.initial
        self.pending = self.f.pending

        self.path = self.f.path.resolve()
        self.fence = self.f.backend._storage.fence_path

        self.assertFalse(
            self.path.is_relative_to(ROOT)
        )

        self.assertTrue(
            self.path.is_relative_to(
                Path(tempfile.gettempdir()).resolve()
            )
        )

        temporary = tempfile.TemporaryDirectory(
            prefix="a44-permanent-process-"
        )

        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name).resolve()

        self.assertFalse(
            self.directory.is_relative_to(ROOT)
        )

        self.direct = getattr(
            sys,
            "_base_executable",
            sys.executable,
        )

        self.assertTrue(
            Path(self.direct).is_file()
        )

        self.sa = b"a" * 32
        self.sb = b"b" * 32
        self.sc = b"c" * 32

        self.assertEqual(
            self.f.backend.read(),
            self.initial,
        )

        self.assertEqual(self.history(), set())

        for value in (
            self.initial,
            self.pending,
            self.f.pin,
        ):

            reconstructed = decode(
                json.loads(json.dumps(encode(value)))
            )

            self.assertIs(
                type(reconstructed),
                type(value),
            )

            self.assertEqual(reconstructed, value)

        self.assertEqual(
            decode(
                encode(self.f.pin)
            ).fingerprint(),
            self.f.pin.fingerprint(),
        )

    def query(self, sql):

        with closing(
            sqlite3.connect(
                self.path.as_uri() + "?mode=ro",
                uri=True,
                timeout=5,
            )
        ) as connection:

            return connection.execute(sql).fetchall()

    def history(self):

        with closing(
            sqlite3.connect(
                self.path.as_uri() + "?mode=ro",
                uri=True,
                timeout=5,
                isolation_level=None,
            )
        ) as connection:

            connection.execute("BEGIN")

            sessions = [
                row[0]
                for row in connection.execute(
                    "SELECT session FROM consumed_sessions "
                    "ORDER BY session"
                )
            ]

            stored = connection.execute(
                "SELECT history_digest FROM session_metadata"
            ).fetchall()

            version = connection.execute(
                "PRAGMA user_version"
            ).fetchone()

            connection.execute("COMMIT")

        self.assertTrue(
            all(
                type(item) is bytes and len(item) == 32
                for item in sessions
            )
        )

        expected = hashlib.sha256(
            b"AdamShell/A44/protected-root-session-history/v2"
            + b"\x00"
            + b"".join(sessions)
            + len(sessions).to_bytes(8, "big")
        ).hexdigest()

        self.assertEqual(stored, [(expected,)])
        self.assertEqual(version, (2,))

        return set(sessions)

    def reopen(self):

        return Backend.open(
            path=self.path,
            expected_identity=self.initial.identity,
        )

    def assert_fence_locked(self):

        with closing(
            sqlite3.connect(
                self.fence.as_uri() + "?mode=rw",
                uri=True,
                timeout=0.2,
                isolation_level=None,
            )
        ) as connection:

            try:
                connection.execute("BEGIN IMMEDIATE")

            except sqlite3.OperationalError as exc:

                self.assertIn(
                    getattr(exc, "sqlite_errorcode", None),
                    {
                        sqlite3.SQLITE_BUSY,
                        sqlite3.SQLITE_LOCKED,
                    },
                )

            else:

                connection.execute("ROLLBACK")

                self.fail("Expected held SQLite fence")

    def assert_waiting(self, worker):

        worker.wait("fence_attempt")

        self.assert_fence_locked()

        deadline = time.monotonic() + 0.75

        while time.monotonic() < deadline:

            self.assertFalse(
                worker.exists("hold_entered")
            )

            self.assertFalse(
                worker.exists("result")
            )

            self.assertIsNone(worker.proc.poll())

            time.sleep(0.05)

    def assert_replay_rejected(self, provider, session):

        before = self.history()

        signed = []
        entered = []

        original = Provider._signed

        def observe(instance, **kwargs):

            signed.append(kwargs["operation"])

            return original(instance, **kwargs)

        with patch.object(
            Provider,
            "_signed",
            new=observe,
        ):

            with self.assertRaisesRegex(
                ValueError,
                "Protected provider session replay",
            ):

                with provider.hold(session=session):

                    entered.append(True)

        self.assertEqual(entered, [])
        self.assertEqual(signed, [])
        self.assertEqual(self.history(), before)
        self.assertEqual(provider._held.phase, "idle")

    def complete(self, provider, session, expected):

        with provider.hold(
            session=session,
        ) as response:

            self.f.assert_signed_response(
                response,
                expected,
            )

            response = provider.read(
                session=session,
                challenge=b"r" * 32,
            )

            self.f.assert_signed_response(
                response,
                expected,
            )

            response = provider.finish(
                session=session,
                challenge=b"f" * 32,
                expected=expected.reference(),
            )

            self.f.assert_signed_response(
                response,
                expected,
            )

        self.assertEqual(provider._held.phase, "idle")

    def recover(
        self,
        expected,
        consumed,
        reusable=None,
    ):

        backend = self.reopen()

        self.assertEqual(
            backend.read(),
            expected,
        )

        self.assertEqual(self.history(), consumed)

        provider = self.f.make_provider(
            backend=backend,
        )

        for session in sorted(consumed):

            self.assert_replay_rejected(
                provider,
                session,
            )

        final_sessions = set(consumed)

        if reusable is not None:

            self.assertNotIn(
                reusable,
                final_sessions,
            )

            self.complete(
                provider,
                reusable,
                expected,
            )

            final_sessions.add(reusable)

        self.complete(
            provider,
            self.sc,
            expected,
        )

        final_sessions.add(self.sc)

        self.assertEqual(
            self.history(),
            final_sessions,
        )

        self.assertEqual(
            self.reopen().read(),
            expected,
        )

        self.assertEqual(
            provider_module._active_provider_owners(),
            {},
        )

        self.assertEqual(
            sqlite_module._active_leases(),
            {},
        )

        self.assertFalse(
            self.path.with_name(
                self.path.name + ".sessions.sqlite3"
            ).exists()
        )

    def crash(
        self,
        scenario,
        *,
        consumed,
        advanced,
        signed,
        details=None,
    ):

        original_rows = self.query(
            "SELECT * FROM root_state"
        )

        worker = Worker(
            self,
            scenario,
            scenario,
            self.sa,
        ).start()

        checkpoint = worker.wait("checkpoint")

        self.assertEqual(
            checkpoint,
            {
                "scenario": scenario,
                "database": str(self.path),
                "session": self.sa.hex(),
                "signed_operations": signed,
                "details": details,
            },
        )

        self.assert_fence_locked()

        self.assertEqual(
            self.history(),
            {self.sa} if consumed else set(),
        )

        current_rows = self.query(
            "SELECT * FROM root_state"
        )

        if advanced:

            self.assertNotEqual(
                current_rows,
                original_rows,
            )

        else:

            self.assertEqual(
                current_rows,
                original_rows,
            )

        worker.kill()

        expected = (
            self.pending
            if advanced
            else self.initial
        )

        self.recover(
            expected,
            {self.sa} if consumed else set(),
            reusable=None if consumed else self.sa,
        )

        self.assertEqual(
            self.query("SELECT * FROM root_state"),
            current_rows,
        )

    def test_01_crash_before_reservation(self):

        self.crash(
            "P01",
            consumed=False,
            advanced=False,
            signed=[],
        )

    def test_02_crash_before_reservation_commit(self):

        self.crash(
            "P02",
            consumed=False,
            advanced=False,
            signed=[],
            details={"transaction_active": True},
        )

    def test_03_crash_after_reservation_commit(self):

        self.crash(
            "P03",
            consumed=True,
            advanced=False,
            signed=[],
        )

    def test_04_crash_after_hold_response(self):

        self.crash(
            "P04",
            consumed=True,
            advanced=False,
            signed=["hold"],
        )

    def test_05_crash_before_cas_dispatch(self):

        self.crash(
            "P05",
            consumed=True,
            advanced=False,
            signed=["hold"],
        )

    def test_06_crash_after_cas_commit_before_signature(self):

        self.crash(
            "P06",
            consumed=True,
            advanced=True,
            signed=["hold"],
        )

    def test_07_crash_after_cas_response(self):

        self.crash(
            "P07",
            consumed=True,
            advanced=True,
            signed=["hold", "cas"],
        )

    def test_08_crash_after_finish_before_release(self):

        self.crash(
            "P08",
            consumed=True,
            advanced=False,
            signed=["hold", "finish"],
        )

    def test_09_crash_inside_cas_transaction(self):

        self.crash(
            "P09",
            consumed=True,
            advanced=False,
            signed=["hold"],
            details={
                "revision": self.pending.revision,
                "transaction_active": True,
            },
        )

    def start_pair(
        self,
        label,
        *,
        owner_mode="owner",
        contender_mode="read",
        same_session=False,
    ):

        owner = Worker(
            self,
            label + "-owner",
            owner_mode,
            self.sa,
        ).start()

        self.assertEqual(
            owner.wait("hold_entered"),
            {"revision": self.initial.revision},
        )

        contender = Worker(
            self,
            label + "-contender",
            contender_mode,
            self.sa if same_session else self.sb,
        ).start()

        self.assertNotEqual(
            owner.proc.pid,
            contender.proc.pid,
        )

        self.assert_waiting(contender)

        self.assertEqual(
            self.history(),
            {self.sa},
        )

        return owner, contender

    def assert_success(
        self,
        result,
        revision,
        signed,
        committed=False,
    ):

        self.assertEqual(
            result,
            {
                "entered": True,
                "cas_committed": committed,
                "cas_rejected": False,
                "rejection": None,
                "revision": revision,
                "signed_operations": signed,
            },
        )

    def test_10_distinct_sessions_serialize(self):

        owner, contender = self.start_pair("P10")

        owner.command("release")

        for result in (
            owner.result(),
            contender.result(),
        ):

            self.assert_success(
                result,
                self.initial.revision,
                ["hold", "finish"],
            )

        self.recover(
            self.initial,
            {self.sa, self.sb},
        )

    def test_11_identical_session_rejected(self):

        owner, contender = self.start_pair(
            "P11",
            same_session=True,
        )

        owner.command("release")

        self.assert_success(
            owner.result(),
            self.initial.revision,
            ["hold", "finish"],
        )

        self.assertEqual(
            contender.result(),
            {
                "entered": False,
                "cas_committed": False,
                "cas_rejected": False,
                "rejection": "Protected provider session replay.",
                "revision": self.initial.revision,
                "signed_operations": [],
            },
        )

        self.assertFalse(
            contender.exists("hold_entered")
        )

        self.recover(
            self.initial,
            {self.sa},
        )

    def test_12_owner_termination_releases_waiter(self):

        owner, contender = self.start_pair("P12")

        owner.kill()

        self.assert_success(
            contender.result(),
            self.initial.revision,
            ["hold", "finish"],
        )

        self.recover(
            self.initial,
            {self.sa, self.sb},
        )

    def test_13_competing_cas_commits_exactly_once(self):

        owner, contender = self.start_pair(
            "P13",
            owner_mode="owner_cas",
            contender_mode="contender_cas",
        )

        owner.command("release")

        self.assert_success(
            owner.result(),
            self.pending.revision,
            ["hold", "cas", "finish"],
            committed=True,
        )

        self.assertEqual(
            contender.wait("hold_entered"),
            {"revision": self.pending.revision},
        )

        self.assertEqual(
            contender.result(),
            {
                "entered": True,
                "cas_committed": False,
                "cas_rejected": True,
                "rejection": "Stale protected provider CAS reference.",
                "revision": self.pending.revision,
                "signed_operations": ["hold"],
            },
        )

        self.recover(
            self.pending,
            {self.sa, self.sb},
        )


if __name__ == "__main__":
    unittest.main()
