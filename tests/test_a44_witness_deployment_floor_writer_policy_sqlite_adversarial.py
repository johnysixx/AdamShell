"""A44 / 66.39D persistent writer policy adversarial regression.

Includes separate Python process verification using independently
opened policy and floor authorities.

All private keys, process signals, database snapshots and SQLite
mutations belong exclusively to temporary test fixtures.

Passing known-limit tests documents limitations; it does not establish
independent rollback protection or cross-database atomicity.
"""

import importlib
import json
import os
import sqlite3
import subprocess
import sys
import time
import unittest

from contextlib import closing, contextmanager
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_witness_deployment_floor_writer_policy_sqlite_contract as persistent


policy = persistent.policy
remote = policy.remote


WORKER_SOURCE = r"""
import importlib
import json
import os
import sys
import time

from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


config = json.loads(sys.stdin.read())

module = importlib.import_module(
    config["policy_module"]
)

floor_module = importlib.import_module(
    config["floor_module"]
)

floor_type = (
    floor_module.SQLiteReferenceSignedWitnessDeploymentFloorCASAuthority
)

backend = floor_type.open(
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

authority = module.SQLitePersistentWriterPolicyAuthority.open(
    path=config["policy_path"],
    backend=backend,
    expected_policy_id=config["policy_id"],
    expected_policy_public_key=bytes.fromhex(
        config["policy_root"]
    ),
    expected_genesis_sha256=config["genesis_sha"],
)

gateway = module.PersistentWriterPolicyGateway.from_authority(
    authority=authority
)


def signal(name):

    Path(config[name]).touch(
        exist_ok=False
    )


def wait_for(name):

    path = Path(config[name])

    deadline = time.monotonic() + 30

    while not path.exists():

        if time.monotonic() >= deadline:
            raise TimeoutError(
                "Worker signal timeout: " + name
            )

        time.sleep(0.02)


opening_reference = authority.current_policy_reference()

signal("ready")

wait_for("go")

signal("started")

result = {
    "pid": os.getpid(),
    "opening_reference": list(opening_reference),
}

operation = config["operation"]

if operation == "publish":

    pair = tuple(
        bytes.fromhex(part)
        for part in config["signed_policy"]
    )

    try:

        reference = authority.publish_policy(
            signed_policy=pair,
        )

        result["status"] = "published"
        result["reference"] = list(reference)

    except ValueError:

        result["status"] = "rejected"

elif operation in ("cas", "blocking_cas"):

    request = bytes.fromhex(
        config["request"]
    )

    if operation == "blocking_cas":

        original = floor_type.advance_if_current

        def blocking_cas(instance, **arguments):

            signal("entered")

            wait_for("release")

            return original(
                instance,
                **arguments,
            )

        with patch.object(
            floor_type,
            "advance_if_current",
            blocking_cas,
        ):

            response = gateway.exchange(request)

        result["status"] = "reply"
        result["response"] = response.hex()

    else:

        try:

            response = gateway.exchange(request)

            result["status"] = "reply"
            result["response"] = response.hex()

        except ValueError:

            result["status"] = "rejected"

else:

    raise RuntimeError(
        "Unexpected worker operation"
    )


print(
    json.dumps(result),
    flush=True,
)
"""


class A44PersistentWriterPolicyAdversarialTests(unittest.TestCase):

    def setUp(self):

        self.s = persistent.A44PersistentWriterPolicyContractTests(
            "test_01_create_persists_exact_signed_genesis"
        )

        self.addCleanup(
            self.s.doCleanups
        )

        self.s.setUp()

        self.p = self.s.p

    def unchanged(self):

        self.p.unchanged()

    def wait_signal(
        self,
        path,
        process,
        timeout=15,
    ):

        deadline = (
            time.monotonic() + timeout
        )

        while not path.exists():

            if process.poll() is not None:

                stdout, stderr = process.communicate()

                self.fail(
                    "Worker exited before signal: "
                    + str(path)
                    + "\nSTDOUT:\n"
                    + stdout
                    + "\nSTDERR:\n"
                    + stderr
                )

            if time.monotonic() >= deadline:

                self.fail(
                    "Worker signal timeout: "
                    + str(path)
                )

            time.sleep(0.02)

    @contextmanager
    def worker(
        self,
        tag,
        operation,
        *,
        request=None,
        signed_policy=None,
    ):

        backend = self.p.backend

        # Only the ephemeral test fixture signer is serialized.
        # It is passed through a private subprocess stdin pipe,
        # not through command-line arguments or persistent files.

        signer_bytes = backend.signer.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )

        signals = {
            name:
                self.s.directory / (tag + "-" + name)
            for name in (
                "ready",
                "go",
                "started",
                "entered",
                "release",
            )
        }

        config = {
            "operation": operation,
            "policy_module": persistent.MODULE,
            "floor_module": type(backend).__module__,
            "policy_path": str(self.s.path),
            "floor_path": str(backend._path),
            "floor_id": backend.floor_id,
            "subject_id": backend.subject_id,
            "authority_id": backend.authority_id,
            "authority_public_key":
                backend.authority_public_key.hex(),
            "witness_id": backend.witness_id,
            "witness_public_key":
                backend.witness_public_key.hex(),
            "floor_signer": signer_bytes.hex(),
            "policy_id": policy.POLICY_ID,
            "policy_root": self.p.root_key.hex(),
            "genesis_sha": self.s.genesis_sha,
            **{
                name: str(path)
                for name, path in signals.items()
            },
        }

        if request is not None:

            config["request"] = request.hex()

        if signed_policy is not None:

            config["signed_policy"] = [
                part.hex()
                for part in signed_policy
            ]

        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-c",
                WORKER_SOURCE,
            ],
            cwd=Path(__file__).resolve().parents[1],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        try:

            process.stdin.write(
                json.dumps(config)
            )

            process.stdin.close()

            # communicate() must not flush an already closed pipe.

            process.stdin = None

            self.wait_signal(
                signals["ready"],
                process,
            )

            yield process, signals

        finally:

            if process.poll() is None:

                process.kill()

            process.communicate(timeout=10)

            if process.stdout is not None:

                process.stdout.close()

            if process.stderr is not None:

                process.stderr.close()

    def finish_worker(
        self,
        process,
    ):

        stdout, stderr = process.communicate(
            timeout=40
        )

        self.assertEqual(
            process.returncode,
            0,
            stdout + "\n" + stderr,
        )

        lines = stdout.strip().splitlines()

        self.assertTrue(
            lines,
            "Missing subprocess result",
        )

        result = json.loads(
            lines[-1]
        )

        self.assertNotEqual(
            result["pid"],
            os.getpid(),
        )

        return result

    def assert_opening_genesis(
        self,
        result,
    ):

        self.assertEqual(
            result["opening_reference"],
            [
                1,
                self.s.genesis_sha,
            ],
        )

    def execute_many(
        self,
        statements,
    ):

        with closing(
            sqlite3.connect(
                str(self.s.path),
                timeout=5,
            )
        ) as connection:

            with connection:

                for statement, parameters in statements:

                    connection.execute(
                        statement,
                        parameters,
                    )

    def rewrite_second_policy(
        self,
        signed_policy,
    ):

        self.execute_many(
            (
                (
                    "UPDATE writer_policy_history "
                    "SET message = ?, signature = ? "
                    "WHERE policy_epoch = 2",
                    signed_policy,
                ),
                (
                    "UPDATE writer_policy_head "
                    "SET policy_sha256 = ?",
                    (
                        policy.digest(signed_policy),
                    ),
                ),
            )
        )

    def assert_policy_store_rejects(
        self,
        signed_policy,
    ):

        with self.assertRaises(ValueError):

            self.s.reopen()

        with self.assertRaises(ValueError):

            self.s.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.s.authority.retired_writer_keys()

        with self.assertRaises(ValueError):

            self.s.send(signed_policy)

        self.unchanged()

    def public_lookup(
        self,
        gateway=None,
    ):

        if gateway is None:

            gateway = self.s.gateway

        raw = gateway.exchange(
            self.p.f.request(
                "lookup",
                challenge=b"l" * 32,
            )
        )

        return self.p.f.response(
            raw,
            operation="lookup",
            challenge=b"l" * 32,
        )

    def test_01_stale_gateway_in_separate_process_observes_revocation(self):

        request = self.p.authorized()

        with self.worker(
            "stale-cas",
            "cas",
            request=request,
        ) as (process, signals):

            second = self.p.next_policy(
                revoked=("writer-alpha",),
            )

            self.s.publish(second)

            signals["go"].touch()

            result = self.finish_worker(
                process
            )

            self.assert_opening_genesis(
                result
            )

            self.assertEqual(
                result["status"],
                "rejected",
            )

        self.s.assert_reference(
            second,
            2,
        )

        self.s.assert_history(
            self.s.genesis,
            second,
        )

        self.unchanged()

        result = self.s.send(
            second,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

    def test_02_conflicting_publications_across_processes_have_one_winner(self):

        first = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        second = self.p.next_policy(
            revoked=("writer-beta",),
        )

        with self.worker(
            "publish-a",
            "publish",
            signed_policy=first,
        ) as (process_a, signals_a):

            with self.worker(
                "publish-b",
                "publish",
                signed_policy=second,
            ) as (process_b, signals_b):

                signals_a["go"].touch()
                signals_b["go"].touch()

                result_a = self.finish_worker(
                    process_a
                )

                result_b = self.finish_worker(
                    process_b
                )

        self.assert_opening_genesis(
            result_a
        )

        self.assert_opening_genesis(
            result_b
        )

        self.assertNotEqual(
            result_a["pid"],
            result_b["pid"],
        )

        self.assertCountEqual(
            [
                result_a["status"],
                result_b["status"],
            ],
            [
                "published",
                "rejected",
            ],
        )

        winner = (
            first
            if result_a["status"] == "published"
            else second
        )

        self.s.assert_reference(
            winner,
            2,
        )

        self.s.assert_history(
            self.s.genesis,
            winner,
        )

        self.unchanged()

    def test_03_cross_process_publication_cannot_overtake_authorized_cas(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        request = self.p.authorized()

        with self.worker(
            "revocation",
            "publish",
            signed_policy=second,
        ) as (publisher, pub_signals):

            with self.worker(
                "blocking-cas",
                "blocking_cas",
                request=request,
            ) as (cas, cas_signals):

                cas_signals["go"].touch()

                self.wait_signal(
                    cas_signals["entered"],
                    cas,
                )

                try:

                    # Independently verify the SQLite writer lock
                    # while CAS is paused inside another process.

                    with closing(
                        sqlite3.connect(
                            str(self.s.path),
                            timeout=0.1,
                            isolation_level=None,
                        )
                    ) as probe:

                        try:

                            with self.assertRaisesRegex(
                                sqlite3.OperationalError,
                                "locked|busy",
                            ):

                                probe.execute(
                                    "BEGIN IMMEDIATE"
                                )

                        finally:

                            if probe.in_transaction:

                                probe.rollback()

                    pub_signals["go"].touch()

                    self.wait_signal(
                        pub_signals["started"],
                        publisher,
                    )

                    time.sleep(0.25)

                    self.assertIsNone(
                        publisher.poll(),
                        "Revocation overtook an in-flight CAS",
                    )

                finally:

                    cas_signals["release"].touch()

                cas_result = self.finish_worker(
                    cas
                )

                publish_result = self.finish_worker(
                    publisher
                )

        self.assert_opening_genesis(
            cas_result
        )

        self.assert_opening_genesis(
            publish_result
        )

        self.assertNotEqual(
            cas_result["pid"],
            publish_result["pid"],
        )

        self.assertEqual(
            cas_result["status"],
            "reply",
        )

        response = self.p.f.response(
            bytes.fromhex(
                cas_result["response"]
            ),
            operation="cas",
            challenge=b"c" * 32,
        )

        self.assertEqual(
            (
                response["status"],
                response["epoch"],
            ),
            ("committed", 2),
        )

        self.assertEqual(
            publish_result["status"],
            "published",
        )

        self.s.assert_reference(
            second,
            2,
        )

        with self.assertRaises(ValueError):

            self.s.send(
                second,
                request=self.p.next_cas(),
            )

        result = self.s.send(
            second,
            writer_id="writer-beta",
            signer=self.p.f.bob,
            request=self.p.next_cas(),
        )

        self.assertEqual(
            (
                result["status"],
                result["epoch"],
            ),
            ("committed", 3),
        )

        self.assertEqual(
            self.s.operation_count(),
            2,
        )

    def test_04_corrupted_head_digest_rejected_by_live_and_reopened_authorities(self):

        second = self.p.next_policy()

        self.s.publish(second)

        self.s.execute_sql(
            "UPDATE writer_policy_head "
            "SET policy_sha256 = ?",
            ("ab" * 32,),
        )

        self.assert_policy_store_rejects(
            second
        )

    def test_05_head_epoch_without_matching_history_fails_closed(self):

        second = self.p.next_policy()

        self.s.publish(second)

        self.s.execute_sql(
            "UPDATE writer_policy_head "
            "SET policy_epoch = 3"
        )

        self.assert_policy_store_rejects(
            second
        )

    def test_06_missing_middle_history_row_fails_closed(self):

        second = self.p.next_policy()

        self.s.publish(second)

        third = self.p.next_policy(
            second
        )

        self.s.publish(third)

        self.s.execute_sql(
            "DELETE FROM writer_policy_history "
            "WHERE policy_epoch = 2"
        )

        self.assert_policy_store_rejects(
            third
        )

    def test_07_validly_signed_history_with_wrong_predecessor_rejected(self):

        second = self.p.next_policy()

        self.s.publish(second)

        invalid = self.p.policy(
            epoch=2,
            previous="ab" * 32,
        )

        # A valid root signature cannot substitute for
        # a valid authenticated history transition.

        self.rewrite_second_policy(
            invalid
        )

        self.assert_policy_store_rejects(
            invalid
        )

    def test_08_injected_signed_history_cannot_reactivate_retired_key(self):

        original_key = policy.public_key(
            self.p.f.alice
        )

        writers = dict(
            self.p.f.writer_keys
        )

        writers["writer-alpha"] = policy.public_key(
            self.p.f.attacker
        )

        second = self.p.next_policy(
            writers=writers,
        )

        self.s.publish(second)

        self.assertIn(
            original_key,
            self.s.authority.retired_writer_keys(),
        )

        writers["writer-charlie"] = original_key

        invalid = self.p.next_policy(
            second,
            writers=writers,
        )

        # Simulate direct tampering with a temporary history
        # database. Both documents have valid root signatures,
        # but the retirement invariant makes the chain invalid.

        self.execute_many(
            (
                (
                    "INSERT INTO writer_policy_history "
                    "(policy_epoch, message, signature) "
                    "VALUES (?, ?, ?)",
                    (
                        3,
                        invalid[0],
                        invalid[1],
                    ),
                ),
                (
                    "UPDATE writer_policy_head "
                    "SET policy_epoch = ?, policy_sha256 = ?",
                    (
                        3,
                        policy.digest(invalid),
                    ),
                ),
            )
        )

        self.assert_policy_store_rejects(
            invalid
        )

        with self.assertRaises(ValueError):

            self.s.send(
                invalid,
                writer_id="writer-charlie",
                signer=self.p.f.alice,
            )

    def test_09_opening_anchor_rejects_validly_signed_same_epoch_fork(self):

        first = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        alternative = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.s.publish(first)

        anchored = self.s.reopen(
            minimum_policy_epoch=2,
            expected_current_policy_sha256=policy.digest(
                first
            ),
        )

        self.s.assert_reference(
            first,
            2,
            authority=anchored,
        )

        self.rewrite_second_policy(
            alternative
        )

        with self.assertRaises(ValueError):

            anchored.current_policy_reference()

        with self.assertRaises(ValueError):

            anchored.retired_writer_keys()

        with self.assertRaises(ValueError):

            self.s.send(
                alternative,
                gateway=self.s.make_gateway(
                    anchored
                ),
            )

        with self.assertRaises(ValueError):

            self.s.reopen(
                expected_current_policy_sha256=policy.digest(
                    first
                ),
            )

        self.unchanged()

        # A fresh opener with only genesis trust cannot
        # distinguish two independently valid signed branches.

        unpinned = self.s.reopen()

        self.s.assert_reference(
            alternative,
            2,
            authority=unpinned,
        )

    def test_10_missing_policy_store_after_open_is_not_recreated(self):

        self.s.path.unlink()

        with self.assertRaises(ValueError):

            self.s.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.s.authority.retired_writer_keys()

        with self.assertRaises(ValueError):

            self.s.publish(
                self.p.next_policy()
            )

        with self.assertRaises(ValueError):

            self.s.send()

        self.assertFalse(
            self.s.path.exists()
        )

        self.unchanged()

    def test_11_floor_database_hardlink_alias_is_rejected(self):

        alias = (
            self.s.directory / "floor-hardlink.sqlite3"
        )

        floor_path = Path(
            self.p.backend._path
        )

        os.link(
            floor_path,
            alias,
        )

        try:

            self.assertTrue(
                os.path.samefile(
                    floor_path,
                    alias,
                )
            )

            with self.assertRaises(ValueError):

                self.s.reopen(
                    path=alias
                )

            with self.assertRaises(ValueError):

                self.s.create(
                    path=alias
                )

            self.unchanged()

            self.s.assert_history(
                self.s.genesis
            )

        finally:

            alias.unlink(
                missing_ok=True
            )

    def test_12_retirement_accumulates_across_rotations_and_removal(self):

        original_alpha = policy.public_key(
            self.p.f.alice
        )

        original_beta = policy.public_key(
            self.p.f.bob
        )

        replacement = policy.public_key(
            self.p.f.attacker
        )

        latest_signer = Ed25519PrivateKey.generate()

        latest_key = policy.public_key(
            latest_signer
        )

        writers = dict(
            self.p.f.writer_keys
        )

        writers["writer-alpha"] = replacement

        second = self.p.next_policy(
            writers=writers,
        )

        self.s.publish(second)

        writers["writer-alpha"] = latest_key

        del writers["writer-beta"]

        third = self.p.next_policy(
            second,
            writers=writers,
        )

        self.s.publish(third)

        reopened = self.s.reopen()

        self.assertEqual(
            reopened.retired_writer_keys(),
            tuple(sorted((
                original_alpha,
                original_beta,
                replacement,
            ))),
        )

        for old_key in (
            original_alpha,
            original_beta,
            replacement,
        ):

            with self.subTest(
                retired_key=old_key.hex()
            ):

                candidate = self.p.next_policy(
                    third,
                    writers={
                        **writers,
                        "writer-charlie": old_key,
                    },
                )

                with self.assertRaises(ValueError):

                    self.s.publish(
                        candidate,
                        authority=reopened,
                    )

                self.s.assert_history(
                    self.s.genesis,
                    second,
                    third,
                )

        self.unchanged()

        result = self.s.send(
            third,
            gateway=self.s.make_gateway(
                reopened
            ),
            signer=latest_signer,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

    def test_13_genesis_revocation_is_included_in_retirement_history(self):

        genesis = self.p.policy(
            revoked=("writer-alpha",),
        )

        path = (
            self.s.directory / "revoked-genesis.sqlite3"
        )

        authority = self.s.create(
            path=path,
            signed_genesis_policy=genesis,
            expected_genesis_sha256=policy.digest(
                genesis
            ),
        )

        original_key = policy.public_key(
            self.p.f.alice
        )

        self.assertEqual(
            authority.retired_writer_keys(),
            (original_key,),
        )

        reopened = self.s.reopen(
            path=path,
            expected_genesis_sha256=policy.digest(
                genesis
            ),
        )

        self.assertEqual(
            reopened.retired_writer_keys(),
            (original_key,),
        )

        gateway = self.s.make_gateway(
            reopened
        )

        with self.assertRaises(ValueError):

            self.s.send(
                genesis,
                gateway=gateway,
            )

        self.unchanged()

        result = self.s.send(
            genesis,
            gateway=gateway,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

    def test_14_rejected_persistent_requests_never_invoke_floor_cas(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.s.publish(second)

        invalid = (
            self.p.authorized(),
            self.p.authorized(
                policy=second,
            ),
            self.p.authorized(
                policy=second,
                writer_id="writer-beta",
                signer=self.p.f.attacker,
            ),
            self.p.f.request(),
            self.p.f.authorized(),
        )

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            side_effect=AssertionError(
                "Unexpected unauthorized backend call"
            ),
        ) as backend_cas:

            for request in invalid:

                with self.subTest(
                    request=request[:60]
                ):

                    with self.assertRaises(ValueError):

                        self.s.gateway.exchange(
                            request
                        )

            backend_cas.assert_not_called()

        self.s.assert_history(
            self.s.genesis,
            second,
        )

        self.unchanged()

    def test_15_precommit_failure_releases_persistent_policy_transaction(self):

        with patch.object(
            type(self.p.backend),
            "advance_if_current",
            side_effect=OSError(
                "Injected precommit failure"
            ),
        ):

            with self.assertRaises(ValueError):

                self.s.send()

        self.unchanged()

        self.s.assert_history(
            self.s.genesis
        )

        independent = self.s.reopen()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.s.publish(
            second,
            authority=independent,
        )

        self.s.assert_reference(
            second,
            2,
        )

        result = self.s.send(
            second,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

    def test_16_postcommit_reply_loss_survives_revocation_and_reopen(self):

        backend_type = type(
            self.p.backend
        )

        original = (
            backend_type.advance_if_current
        )

        request = self.p.authorized()

        def lost_reply(
            instance,
            **arguments,
        ):

            original(
                instance,
                **arguments,
            )

            raise OSError(
                "Injected postcommit reply loss"
            )

        with patch.object(
            backend_type,
            "advance_if_current",
            lost_reply,
        ):

            with self.assertRaises(ValueError):

                self.s.gateway.exchange(
                    request
                )

        self.assertEqual(
            self.s.operation_count(),
            1,
        )

        self.assertEqual(
            self.p.f.fixture.fixture.read()["epoch"],
            2,
        )

        independent = self.s.reopen()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.s.publish(
            second,
            authority=independent,
        )

        reopened = self.s.reopen()

        gateway = self.s.make_gateway(
            reopened
        )

        with self.assertRaises(ValueError):

            gateway.exchange(request)

        lookup = self.public_lookup(
            gateway
        )

        self.assertEqual(
            lookup["status"],
            "committed",
        )

        self.assertEqual(
            self.s.operation_count(),
            1,
        )

    def test_17_exact_cas_replay_remains_idempotent_after_reopen(self):

        request = self.p.authorized()

        for _ in range(3):

            reopened = self.s.reopen()

            result = self.p.send(
                request,
                gateway=self.s.make_gateway(
                    reopened
                ),
            )

            self.assertEqual(
                (
                    result["status"],
                    result["epoch"],
                ),
                ("committed", 2),
            )

            self.assertEqual(
                self.s.operation_count(),
                1,
            )

        self.s.assert_history(
            self.s.genesis
        )

    def test_18_corrupted_policy_blocks_writes_but_preserves_public_recovery(self):

        self.assertEqual(
            self.s.send()["status"],
            "committed",
        )

        second = self.p.next_policy()

        self.s.publish(second)

        self.s.execute_sql(
            "UPDATE writer_policy_history "
            "SET signature = zeroblob(64) "
            "WHERE policy_epoch = 1"
        )

        with self.assertRaises(ValueError):

            self.s.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.s.send(
                second,
                request=self.p.next_cas(),
            )

        lookup = self.public_lookup()

        self.assertEqual(
            lookup["status"],
            "committed",
        )

        client = self.p.f.fixture.make_client(
            transport=self.s.gateway,
        )

        self.assertEqual(
            self.p.f.fixture.read(client)["epoch"],
            2,
        )

        self.assertEqual(
            self.s.operation_count(),
            1,
        )

    def test_19_independent_policy_database_copy_is_not_fenced_known_limit(self):

        snapshot = (
            self.s.directory / "independent-policy.sqlite3"
        )

        self.s.backup(snapshot)

        independent = self.s.reopen(
            path=snapshot
        )

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.s.publish(second)

        with self.assertRaises(ValueError):

            self.s.send(second)

        self.unchanged()

        self.s.assert_reference(
            self.s.genesis,
            1,
            authority=independent,
        )

        # Known limit:
        # Distinct database files have distinct SQLite locks.
        # A separate valid historical store is not fenced.

        result = self.s.send(
            self.s.genesis,
            gateway=self.s.make_gateway(
                independent
            ),
        )

        self.assertEqual(
            (
                result["status"],
                result["epoch"],
            ),
            ("committed", 2),
        )

        self.assertEqual(
            self.s.operation_count(),
            1,
        )

        self.s.assert_reference(
            second,
            2,
        )

    def test_20_opening_anchor_is_not_live_high_water_known_limit(self):

        snapshot = (
            self.s.directory / "opening-policy.sqlite3"
        )

        self.s.backup(snapshot)

        original = self.s.authority

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.s.publish(second)

        self.s.assert_reference(
            second,
            2,
            authority=original,
        )

        later = self.s.reopen()

        self.s.assert_reference(
            second,
            2,
            authority=later,
        )

        self.s.restore_backup(snapshot)

        # The authority opened at epoch 2 retains that
        # authenticated opening anchor and detects rollback.

        with self.assertRaises(ValueError):

            later.current_policy_reference()

        with self.assertRaises(ValueError):

            later.retired_writer_keys()

        with self.assertRaises(ValueError):

            self.s.send(
                self.s.genesis,
                gateway=self.s.make_gateway(
                    later
                ),
            )

        # The original authority opened at genesis.
        # Merely observing epoch 2 did not advance its anchor.
        # This is an explicit existing reference limitation.

        self.s.assert_reference(
            self.s.genesis,
            1,
            authority=original,
        )

        self.s.assert_history(
            self.s.genesis
        )

        self.unchanged()

        result = self.s.send(
            self.s.genesis,
            gateway=self.s.make_gateway(
                original
            ),
        )

        self.assertEqual(
            (
                result["status"],
                result["epoch"],
            ),
            ("committed", 2),
        )

        self.assertEqual(
            self.s.operation_count(),
            1,
        )


if __name__ == "__main__":
    unittest.main()
