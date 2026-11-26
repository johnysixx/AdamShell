"""Actual signed policy publication process-crash regression.

All subprocesses operate exclusively on ephemeral test databases
and ephemeral fixture signing keys.

The actual worker calls os._exit() at the requested transaction
boundary. No ordinary Python cleanup or context manager exit
is allowed to run after that boundary is reached.

The test does not depend on the Windows virtualenv launcher PID
being identical to the actual Python process PID.

No SQLite journal is manually deleted or repaired.

Process termination does not establish physical power-loss
durability or hardware-backed rollback resistance.
"""

import json
import os
import secrets
import subprocess
import sys
import unittest

from pathlib import Path

from cryptography.hazmat.primitives import serialization

import test_a44_witness_deployment_floor_writer_policy_protected_root_sqlite_authority_contract as previous


CRASH_CODES = {
    "before_prepare_commit": 81,
    "after_prepare_commit": 82,
    "before_policy_commit": 83,
    "after_policy_commit": 84,
    "before_finalize_commit": 85,
    "after_finalize_commit": 86,
}


WORKER = r"""
import importlib
import json
import os
import sys

from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


config = json.loads(sys.stdin.read())

module = importlib.import_module(
    config["authority_module"]
)

root_module = importlib.import_module(
    config["root_module"]
)

floor_module = importlib.import_module(
    config["floor_module"]
)

storage = root_module.storage

root_path = Path(
    config["root_path"]
).resolve()

identity = storage.root.ProtectedDeploymentIdentity(
    deployment_id=config["deployment_id"],
    configuration_sha256=config["configuration_sha256"],
    provisioning_nonce=bytes.fromhex(
        config["provisioning_nonce"]
    ),
)

floor_type = (
    floor_module
    .SQLiteReferenceSignedWitnessDeploymentFloorCASAuthority
)

floor = floor_type.open(
    path=config["floor_path"],
    signer=Ed25519PrivateKey.from_private_bytes(
        bytes.fromhex(config["floor_signer"])
    ),
    expected_floor_id=config["floor_id"],
    expected_subject_id=config["subject_id"],
    expected_authority_id=config["authority_id"],
    expected_authority_public_key=bytes.fromhex(
        config["authority_public_key"]
    ),
    expected_witness_id=config["witness_id"],
    expected_witness_public_key=bytes.fromhex(
        config["witness_public_key"]
    ),
)

root_backend = root_module.SQLiteProtectedRootBackend.open(
    path=root_path,
    expected_identity=identity,
)

authority = module.ProtectedDurableWriterPolicyAuthority.open(
    path=config["policy_path"],
    backend=floor,
    root_backend=root_backend,
    expected_identity=identity,
    expected_policy_id=config["policy_id"],
    expected_policy_public_key=bytes.fromhex(
        config["policy_public_key"]
    ),
    expected_genesis_sha256=config["genesis_sha"],
)

operation = config["operation"]

phase = config.get("phase")

signed_policy = tuple(
    bytes.fromhex(part)
    for part in config["signed_policy"]
)

expected_reference = (
    2,
    config["candidate_sha"],
)

descriptor = root_backend._storage

original_storage_transaction = storage._transaction

original_policy_transaction = (
    module.durable.persistent._transaction
)


def emit(status, **fields):

    print(
        json.dumps({
            "status": status,
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "token": config["token"],
            **fields,
        }),
        flush=True,
    )


def stop_at_boundary(name, state):

    if phase != name:
        return

    emit(
        "crashed",
        boundary=name,
        revision=state.revision,
        anchor_epoch=state.durable_state.anchor.epoch,
        prepared=state.durable_state.prepared is not None,
        root_digest=state.reference().sha256,
    )

    # Real abrupt process termination.
    # No Python finally blocks or cleanup handlers execute.

    os._exit(config["exit_code"])


def require_candidate(state):

    prepared = state.durable_state.prepared

    if prepared is None:
        raise AssertionError("Expected retained PREPARED candidate")

    if prepared.candidate.pair() != expected_reference:
        raise AssertionError("Unexpected prepared reference")

    if prepared.signed_policy != signed_policy:
        raise AssertionError("Prepared signed bytes changed")


@contextmanager
def watched_storage_transaction(path, **arguments):

    transition = None
    recorded = None

    with original_storage_transaction(
        path,
        **arguments,
    ) as connection:

        yield connection

        if (
            Path(path).resolve() == root_path
            and arguments.get("write", False)
        ):

            if not connection.in_transaction:
                raise AssertionError("Missing active root transaction")

            recorded = storage._read_state(
                connection,
                descriptor,
            )

            if (
                recorded.revision == 2
                and recorded.durable_state.prepared is not None
            ):

                require_candidate(recorded)

                transition = "prepare"

            elif (
                recorded.revision == 3
                and recorded.durable_state.prepared is None
            ):

                if (
                    recorded.durable_state.anchor.pair()
                    != expected_reference
                ):
                    raise AssertionError(
                        "Incorrect finalization reference"
                    )

                transition = "finalize"

            else:

                raise AssertionError(
                    "Unexpected root publication transition"
                )

            stop_at_boundary(
                "before_" + transition + "_commit",
                recorded,
            )

    # This point is reached only after the original SQLite
    # transaction has successfully completed its COMMIT.

    if transition is not None:

        stop_at_boundary(
            "after_" + transition + "_commit",
            recorded,
        )


@contextmanager
def watched_policy_transaction(pins, **arguments):

    written = False
    retained = None

    with original_policy_transaction(
        pins,
        **arguments,
    ) as connection:

        yield connection

        row = connection.execute(
            "SELECT policy_epoch FROM writer_policy_head"
        ).fetchone()

        written = row == (2,)

        if written:

            if not connection.in_transaction:
                raise AssertionError(
                    "Missing active policy transaction"
                )

            actual = connection.execute(
                "SELECT message, signature "
                "FROM writer_policy_history "
                "WHERE policy_epoch = 2"
            ).fetchall()

            if actual != [signed_policy]:
                raise AssertionError(
                    "Exact signed policy was not retained"
                )

            retained = root_backend.read()

            require_candidate(retained)

            stop_at_boundary(
                "before_policy_commit",
                retained,
            )

    # The policy transaction has actually committed.

    if written:

        stop_at_boundary(
            "after_policy_commit",
            retained,
        )


if operation == "crash_publish":

    if authority.root_state().revision != 1:

        raise AssertionError(
            "Crash publication must start at root revision one"
        )

    with patch.object(
        storage,
        "_transaction",
        watched_storage_transaction,
    ), patch.object(
        module.durable.persistent,
        "_transaction",
        watched_policy_transaction,
    ):

        authority.publish_policy(
            signed_policy=signed_policy,
        )

    raise AssertionError(
        "Requested process-crash boundary was not reached"
    )

elif operation == "recover":

    reference = authority.recover_publication()

    current = authority.root_state()

    emit(
        "recovered",
        reference=list(reference),
        revision=current.revision,
        root_digest=current.reference().sha256,
        prepared=current.durable_state.prepared is not None,
    )

else:

    raise AssertionError(
        "Unknown subprocess operation: " + operation
    )
"""


class A44SQLiteProtectedRootPublicationAdversarialTests(
    unittest.TestCase
):

    def setUp(self):

        self.f = (
            previous.A44SQLiteProtectedRootAuthorityContractTests(
                "test_01_existing_authority_bootstrap_and_fresh_root_open"
            )
        )

        self.addCleanup(self.f.doCleanups)

        self.f.setUp()

        self.d = self.f.d
        self.p = self.f.p
        self.s = self.f.s

        self.genesis = self.f.genesis

        self.root = self.f.root

        self.authority = self.f.authority

        self.identity = self.f.identity

        self.candidate = self.f.f.candidate()

        self.initial = self.root.read()

        self.assertEqual(self.initial.revision, 1)

    def config(self, operation, phase=None):

        backend = self.p.backend

        # This is only the temporary fixture's private key.
        # It is transferred through the subprocess stdin pipe.
        # No signing key is written into a command line or file.

        signer = backend.signer.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )

        parameters = self.f.f.parameters()

        return {
            "operation": operation,
            "phase": phase,
            "exit_code": CRASH_CODES.get(phase, 0),
            "token": secrets.token_hex(32),

            "authority_module": type(
                self.authority
            ).__module__,

            "root_module": type(
                self.root
            ).__module__,

            "floor_module": type(
                backend
            ).__module__,

            "root_path": str(self.f.path),
            "policy_path": str(self.s.path),

            "deployment_id": self.identity.deployment_id,

            "configuration_sha256":
                self.identity.configuration_sha256,

            "provisioning_nonce":
                self.identity.provisioning_nonce.hex(),

            "floor_path": str(backend._path),

            "floor_signer": signer.hex(),

            "floor_id": backend.floor_id,
            "subject_id": backend.subject_id,

            "authority_id": backend.authority_id,

            "authority_public_key":
                backend.authority_public_key.hex(),

            "witness_id": backend.witness_id,

            "witness_public_key":
                backend.witness_public_key.hex(),

            "policy_id": parameters["expected_policy_id"],

            "policy_public_key":
                parameters["expected_policy_public_key"].hex(),

            "genesis_sha":
                parameters["expected_genesis_sha256"],

            "signed_policy": [
                part.hex()
                for part in self.candidate
            ],

            "candidate_sha":
                self.d.ref(self.candidate, 2).sha256,
        }

    def run_worker(self, operation, phase=None):

        config = self.config(operation, phase)

        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-c",
                WORKER,
            ],
            cwd=Path(__file__).resolve().parents[1],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        try:

            stdout, stderr = process.communicate(
                input=json.dumps(config),
                timeout=120,
            )

        except subprocess.TimeoutExpired:

            if process.poll() is None:

                if os.name == "nt":

                    subprocess.run(
                        [
                            "taskkill",
                            "/PID",
                            str(process.pid),
                            "/T",
                            "/F",
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=15,
                    )

                else:

                    process.kill()

            process.communicate(timeout=30)

            raise

        self.assertEqual(
            process.returncode,
            config["exit_code"],
            stdout + "\n" + stderr,
        )

        lines = stdout.strip().splitlines()

        self.assertTrue(
            lines,
            "Missing actual worker result",
        )

        result = json.loads(lines[-1])

        self.assertEqual(
            result["token"],
            config["token"],
        )

        pid = result["pid"]
        ppid = result["ppid"]

        self.assertIs(type(pid), int)
        self.assertIs(type(ppid), int)

        self.assertGreater(pid, 0)
        self.assertGreater(ppid, 0)

        self.assertNotEqual(pid, os.getpid())

        direct = (
            pid == process.pid
            and ppid == os.getpid()
        )

        redirected = (
            pid != process.pid
            and ppid == process.pid
        )

        self.assertTrue(
            direct or redirected,
            "Unexpected independent worker relationship",
        )

        return result

    def crash(self, phase, attempted_revision):

        result = self.run_worker(
            "crash_publish",
            phase,
        )

        self.assertEqual(
            result["status"],
            "crashed",
        )

        self.assertEqual(
            result["boundary"],
            phase,
        )

        self.assertEqual(
            result["revision"],
            attempted_revision,
        )

        self.assertEqual(
            result["prepared"],
            attempted_revision == 2,
        )

        self.assertEqual(
            result["anchor_epoch"],
            1 if attempted_revision == 2 else 2,
        )

        self.d.assert_floor(1, 0)

        return result

    def assert_history(self, *signed_policies):

        persistent = self.f.f.m.durable.persistent

        with persistent._transaction(
            self.authority._pins
        ) as connection:

            history = persistent._load_history(
                connection,
                self.authority._pins,
            )

            rows = connection.execute(
                "SELECT policy_epoch, message, signature "
                "FROM writer_policy_history "
                "ORDER BY policy_epoch"
            ).fetchall()

            expected = [
                (epoch, pair[0], pair[1])
                for epoch, pair in enumerate(
                    signed_policies,
                    start=1,
                )
            ]

            self.assertEqual(rows, expected)

            self.assertEqual(
                history.current.epoch,
                len(signed_policies),
            )

            self.assertEqual(
                history.current.sha256,
                self.d.ref(
                    signed_policies[-1],
                    len(signed_policies),
                ).sha256,
            )

    def assert_pending(self):

        retained = self.f.pending(self.candidate)

        fresh = self.f.reopen()

        self.assertEqual(
            fresh.root_state(),
            retained,
        )

        with self.assertRaises(ValueError):
            fresh.current_policy_reference()

        with self.assertRaises(ValueError):
            fresh.retired_writer_keys()

        self.f.f.blocked(
            gateway=self.f.f.make_gateway(fresh),
        )

        alternative = self.p.next_policy(
            revoked=("writer-beta",),
        )

        with self.assertRaises(ValueError):

            fresh.publish_policy(
                signed_policy=alternative,
            )

        self.assertEqual(
            fresh.root_state(),
            retained,
        )

        self.d.assert_floor(1, 0)

        return retained

    def assert_finalized(self):

        retained = self.f.stable(
            self.candidate,
            2,
            3,
        )

        fresh = self.f.reopen()

        self.assertEqual(
            fresh.root_state(),
            retained,
        )

        self.assertEqual(
            fresh.current_policy_reference(),
            self.d.pair(self.candidate, 2),
        )

        self.assert_history(
            self.genesis,
            self.candidate,
        )

        self.f.f.blocked(
            signed_policy=self.candidate,
            gateway=self.f.f.make_gateway(fresh),
        )

        self.d.assert_floor(1, 0)

        return retained

    def recover(self):

        fresh = self.f.reopen()

        self.assertEqual(
            fresh.recover_publication(),
            self.d.pair(self.candidate, 2),
        )

        retained = self.assert_finalized()

        reopened = self.f.reopen()

        self.assertEqual(
            reopened.recover_publication(),
            self.d.pair(self.candidate, 2),
        )

        self.assertEqual(
            reopened.root_state(),
            retained,
        )

        return retained

    def test_01_crash_before_prepare_commit(self):

        crashed = self.crash(
            "before_prepare_commit",
            2,
        )

        retained = self.f.stable(
            self.genesis,
            1,
            1,
        )

        self.assertEqual(retained, self.initial)

        self.assertNotEqual(
            crashed["root_digest"],
            retained.reference().sha256,
        )

        self.assert_history(self.genesis)

        fresh = self.f.reopen()

        self.assertEqual(
            fresh.publish_policy(
                signed_policy=self.candidate,
            ),
            self.d.pair(self.candidate, 2),
        )

        self.assert_finalized()

    def test_02_crash_after_prepare_commit(self):

        crashed = self.crash(
            "after_prepare_commit",
            2,
        )

        retained = self.assert_pending()

        self.assertEqual(
            crashed["root_digest"],
            retained.reference().sha256,
        )

        self.assert_history(self.genesis)

        self.recover()

    def test_03_crash_before_policy_commit(self):

        crashed = self.crash(
            "before_policy_commit",
            2,
        )

        retained = self.assert_pending()

        self.assertEqual(
            crashed["root_digest"],
            retained.reference().sha256,
        )

        self.assert_history(self.genesis)

        self.recover()

    def test_04_crash_after_policy_commit(self):

        crashed = self.crash(
            "after_policy_commit",
            2,
        )

        retained = self.assert_pending()

        self.assertEqual(
            crashed["root_digest"],
            retained.reference().sha256,
        )

        self.assert_history(
            self.genesis,
            self.candidate,
        )

        self.recover()

    def test_05_crash_before_finalize_commit(self):

        crashed = self.crash(
            "before_finalize_commit",
            3,
        )

        retained = self.assert_pending()

        self.assertNotEqual(
            crashed["root_digest"],
            retained.reference().sha256,
        )

        self.assert_history(
            self.genesis,
            self.candidate,
        )

        finalized = self.recover()

        self.assertEqual(
            crashed["root_digest"],
            finalized.reference().sha256,
        )

    def test_06_crash_after_finalize_commit(self):

        crashed = self.crash(
            "after_finalize_commit",
            3,
        )

        retained = self.assert_finalized()

        self.assertEqual(
            crashed["root_digest"],
            retained.reference().sha256,
        )

        self.assertEqual(
            self.recover(),
            retained,
        )

    def test_07_independent_process_recovery_after_policy_rollback(self):

        old = self.d.snapshot(
            "publication-crash-genesis.sqlite3"
        )

        crashed = self.crash(
            "after_policy_commit",
            2,
        )

        self.assert_history(
            self.genesis,
            self.candidate,
        )

        retained = self.assert_pending()

        self.assertEqual(
            retained.reference().sha256,
            crashed["root_digest"],
        )

        self.d.restore(old)

        self.assert_history(self.genesis)

        self.assertEqual(
            self.assert_pending(),
            retained,
        )

        result = self.run_worker("recover")

        self.assertEqual(
            result["status"],
            "recovered",
        )

        self.assertEqual(
            result["reference"],
            list(
                self.d.pair(self.candidate, 2)
            ),
        )

        self.assertEqual(result["revision"], 3)
        self.assertFalse(result["prepared"])

        finalized = self.assert_finalized()

        self.assertEqual(
            result["root_digest"],
            finalized.reference().sha256,
        )

        second = self.run_worker("recover")

        self.assertEqual(
            second["root_digest"],
            result["root_digest"],
        )

        self.assertEqual(
            second["revision"],
            3,
        )

        self.assertEqual(
            second["reference"],
            result["reference"],
        )

        self.assertFalse(second["prepared"])

        self.assertEqual(
            self.assert_finalized(),
            finalized,
        )

    def test_08_finalized_root_rejects_policy_rollback_after_crash(self):

        old = self.d.snapshot(
            "finalized-crash-genesis.sqlite3"
        )

        crashed = self.crash(
            "after_finalize_commit",
            3,
        )

        retained = self.assert_finalized()

        self.assertEqual(
            crashed["root_digest"],
            retained.reference().sha256,
        )

        committed = self.d.snapshot(
            "finalized-crash-policy.sqlite3"
        )

        self.d.restore(old)

        self.assert_history(self.genesis)

        self.assertEqual(
            self.f.open_root().read(),
            retained,
        )

        with self.assertRaises(ValueError):
            self.f.reopen()

        with self.assertRaises(ValueError):
            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):
            self.authority.recover_publication()

        self.f.f.blocked()

        self.d.assert_floor(1, 0)

        self.assertEqual(
            self.f.open_root().read(),
            retained,
        )

        self.d.restore(committed)

        fresh = self.f.reopen()

        self.assertEqual(
            fresh.root_state(),
            retained,
        )

        self.f.f.blocked(
            signed_policy=self.candidate,
        )

        self.d.assert_committed(
            self.f.f.send(
                self.candidate,
                gateway=self.f.f.make_gateway(fresh),
                writer_id="writer-beta",
                signer=self.p.f.bob,
            ),
            2,
        )

        self.d.assert_floor(2, 1)

        self.assertEqual(
            self.f.open_root().read(),
            retained,
        )

        self.assert_history(
            self.genesis,
            self.candidate,
        )


if __name__ == "__main__":
    unittest.main()
