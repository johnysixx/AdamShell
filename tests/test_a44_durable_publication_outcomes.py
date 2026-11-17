"""A44 locally durable operation-outcome contracts.

The proposed local SQLite authority is a prototype, NOT a
production trust root. Anyone able to replace or roll back its
database can compromise its claims.

A production authority requires a separate authenticated trust
domain, durable atomic CAS, fencing and rollback protection.
"""

import shutil
import sqlite3
from contextlib import closing

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import dataclasses
import tempfile
import unittest

from pathlib import Path

from core.existence.history_receipt_proof import ReceiptKeyStatus
from core.existence.history_receipt_trust_floor import (
    _catalog_fingerprints,
)
from test_a44_current_trust_enforcement import lifecycle_pair
from test_a44_versioned_receipt_keys import SOURCE, ring


OPERATION = "provider-key-rotation-2"


def snapshot(lifecycle):
    return (
        lifecycle.revision,
        *_catalog_fingerprints(lifecycle),
    )


def bootstrap(path, committed):
    from core.existence.history_receipt_trust_operation_outcomes import (
        LocalDurablePublicationAuthority,
    )

    return LocalDurablePublicationAuthority.bootstrap(
        path,
        committed,
    )


def reopen(path):
    from core.existence.history_receipt_trust_operation_outcomes import (
        LocalDurablePublicationAuthority,
    )

    return LocalDurablePublicationAuthority.open(path)


def prepare(authority, old, new, operation_id=OPERATION):
    return authority.prepare(
        expected_committed=old,
        operation_id=operation_id,
        target=new,
    )


def finalize(authority, old, new, operation_id=OPERATION):
    return authority.finalize(
        expected_committed=old,
        operation_id=operation_id,
        target=new,
    )


class A44DurablePublicationOutcomesTests(unittest.TestCase):

    def test_bootstrap_has_committed_state_and_no_outcome(self):
        initial, _ = lifecycle_pair()
        old = snapshot(initial)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            self.assertEqual(
                authority.read_state(),
                (old, None),
            )
            self.assertIsNone(
                authority.query_operation(OPERATION)
            )

            reopened = reopen(path)

            self.assertEqual(
                reopened.read_state(),
                (old, None),
            )
            self.assertIsNone(
                reopened.query_operation(OPERATION)
            )

    def test_prepared_outcome_survives_reopen(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            self.assertTrue(prepare(authority, old, new))

            self.assertEqual(
                authority.read_state(),
                (old, (OPERATION, new)),
            )

            reopened = reopen(path)
            outcome = reopened.query_operation(OPERATION)

            self.assertIsNotNone(outcome)
            self.assertEqual(outcome.operation_id, OPERATION)
            self.assertEqual(outcome.expected_committed, old)
            self.assertEqual(outcome.target, new)
            self.assertEqual(outcome.status.value, "prepared")

            self.assertEqual(
                reopened.read_state(),
                (old, (OPERATION, new)),
            )

    def test_prepare_retry_is_exact_and_collision_is_rejected(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        alternate = initial.advance(
            {
                SOURCE: ring(
                    old=ReceiptKeyStatus.VERIFY_ONLY,
                )
            },
            revision=2,
        )
        different = snapshot(alternate)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            self.assertTrue(prepare(authority, old, new))
            self.assertFalse(prepare(authority, old, new))

            for operation_id, target in (
                (OPERATION, different),
                ("unrelated-operation", new),
            ):
                with self.subTest(
                    operation_id=operation_id
                ):
                    with self.assertRaises(ValueError):
                        prepare(
                            authority,
                            old,
                            target,
                            operation_id,
                        )

            self.assertEqual(
                authority.read_state(),
                (old, (OPERATION, new)),
            )

    def test_finalize_and_terminal_outcome_are_atomic(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            self.assertTrue(prepare(authority, old, new))
            self.assertTrue(finalize(authority, old, new))

            reopened = reopen(path)
            outcome = reopened.query_operation(OPERATION)

            self.assertEqual(
                reopened.read_state(),
                (new, None),
            )
            self.assertEqual(outcome.status.value, "committed")
            self.assertEqual(outcome.operation_id, OPERATION)
            self.assertEqual(outcome.expected_committed, old)
            self.assertEqual(outcome.target, new)

            # Exact duplicate FINALIZE is identifiable.
            self.assertFalse(
                finalize(reopened, old, new)
            )

            # A completed ID must not be used to start
            # a different publication.
            future = (
                3,
                new[1],
                "a" * 64,
            )

            with self.assertRaises(ValueError):
                prepare(
                    reopened,
                    new,
                    future,
                    operation_id=OPERATION,
                )

            self.assertEqual(
                reopened.read_state(),
                (new, None),
            )

    def test_lost_finalize_reply_is_resolved_by_query(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            prepare(authority, old, new)

            def finalize_then_lose_reply():
                finalize(authority, old, new)
                raise OSError("Injected lost FINALIZE reply")

            with self.assertRaises(OSError):
                finalize_then_lose_reply()

            reopened = reopen(path)
            outcome = reopened.query_operation(OPERATION)

            self.assertEqual(outcome.status.value, "committed")
            self.assertEqual(outcome.expected_committed, old)
            self.assertEqual(outcome.target, new)

            self.assertEqual(
                reopened.read_state(),
                (new, None),
            )

            # Outcome is tied to the operation, not merely
            # inferred from the current catalog revision.
            self.assertIsNone(
                reopened.query_operation("other-operation")
            )

    def test_finalize_rejects_wrong_identity_and_missing_prepare(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            with self.assertRaises(ValueError):
                finalize(authority, old, new)

            self.assertTrue(prepare(authority, old, new))

            wrong_old = (
                old[0],
                old[1],
                "0" * 64,
            )
            wrong_new = (
                new[0],
                new[1],
                "1" * 64,
            )

            for predecessor, target, operation_id in (
                (wrong_old, new, OPERATION),
                (old, wrong_new, OPERATION),
                (old, new, "other-operation"),
            ):
                with self.subTest(
                    operation_id=operation_id,
                    target_revision=target[0],
                ):
                    with self.assertRaises(ValueError):
                        finalize(
                            authority,
                            predecessor,
                            target,
                            operation_id,
                        )

            self.assertEqual(
                authority.read_state(),
                (old, (OPERATION, new)),
            )

            self.assertEqual(
                authority.query_operation(OPERATION).status.value,
                "prepared",
            )

    def test_invalid_identity_and_snapshots_do_not_mutate(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            for invalid_id in (
                None,
                "",
                " ",
                " padded ",
                True,
                7,
            ):
                with self.subTest(operation_id=repr(invalid_id)):
                    with self.assertRaises(ValueError):
                        prepare(
                            authority,
                            old,
                            new,
                            invalid_id,
                        )

            for invalid_target in (
                old,
                (True, new[1], new[2]),
                (2, "invalid", new[2]),
                (2, "0" * 64, new[2]),
                [new[0], new[1], new[2]],
            ):
                with self.subTest(
                    target=repr(invalid_target)
                ):
                    with self.assertRaises(ValueError):
                        prepare(
                            authority,
                            old,
                            invalid_target,
                        )

            self.assertEqual(
                authority.read_state(),
                (old, None),
            )
            self.assertIsNone(
                authority.query_operation(OPERATION)
            )

    def test_operation_query_returns_immutable_snapshot(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            authority = bootstrap(
                Path(folder) / "authority.sqlite3",
                old,
            )

            prepare(authority, old, new)
            record = authority.query_operation(OPERATION)

            self.assertTrue(dataclasses.is_dataclass(record))

            with self.assertRaises(
                (dataclasses.FrozenInstanceError, AttributeError)
            ):
                record.status = "committed"

            self.assertEqual(
                authority.query_operation(OPERATION).status.value,
                "prepared",
            )


    def test_missing_and_corrupt_database_fail_closed(self):
        initial, _ = lifecycle_pair()
        old = snapshot(initial)

        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)

            missing = folder / "missing.sqlite3"
            corrupt = folder / "corrupt.sqlite3"
            empty = folder / "empty.sqlite3"

            corrupt.write_bytes(b"not a sqlite database")
            empty.write_bytes(b"")

            for path in (missing, corrupt, empty):
                with self.subTest(database=path.name):
                    with self.assertRaises(ValueError):
                        reopen(path)

            self.assertFalse(missing.exists())

            valid = folder / "valid.sqlite3"
            authority = bootstrap(valid, old)

            self.assertEqual(
                authority.read_state(),
                (old, None),
            )

    def test_exclusive_bootstrap_preserves_existing_history(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"

            authority = bootstrap(path, old)
            prepare(authority, old, new)

            before = authority.read_state()
            outcome = authority.query_operation(OPERATION)

            with self.assertRaises(ValueError):
                bootstrap(path, new)

            reopened = reopen(path)

            self.assertEqual(reopened.read_state(), before)
            self.assertEqual(
                reopened.query_operation(OPERATION),
                outcome,
            )

    def test_finalize_second_write_failure_is_atomic(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            prepare(authority, old, new)

            # Inject a failure specifically at the second
            # persistent update in FINALIZE. The first UPDATE
            # has already modified authority_state inside
            # the same uncommitted SQLite transaction.
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute(
                    "CREATE TRIGGER fail_outcome_commit "
                    "BEFORE UPDATE OF status "
                    "ON publication_operations "
                    "WHEN NEW.status='committed' "
                    "BEGIN "
                    "SELECT RAISE(FAIL, "
                    "'injected outcome write failure'); "
                    "END"
                )

            try:
                with self.assertRaises(ValueError):
                    finalize(authority, old, new)

                reopened = reopen(path)

                # Both updates must have rolled back.
                self.assertEqual(
                    reopened.read_state(),
                    (old, (OPERATION, new)),
                )

                self.assertEqual(
                    reopened.query_operation(
                        OPERATION
                    ).status.value,
                    "prepared",
                )

            finally:
                with closing(sqlite3.connect(path)) as connection, connection:
                    connection.execute(
                        "DROP TRIGGER IF EXISTS "
                        "fail_outcome_commit"
                    )

            # Once the injected failure disappears,
            # the original operation can be completed.
            self.assertTrue(
                finalize(reopened, old, new)
            )

            self.assertEqual(
                reopen(path).read_state(),
                (new, None),
            )

    def test_competing_prepare_across_instances_has_one_winner(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"

            first = bootstrap(path, old)
            second = reopen(path)

            barrier = Barrier(2)

            def attempt(authority, operation_id):
                barrier.wait(timeout=10)

                try:
                    authority.prepare(
                        expected_committed=old,
                        operation_id=operation_id,
                        target=new,
                    )
                    return ("accepted", operation_id)

                except ValueError:
                    return ("rejected", operation_id)

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = (
                    pool.submit(first_operation)
                    if False else None
                )

                # Use independent authority objects sharing
                # one SQLite database, not one Python lock.
                a = pool.submit(
                    attempt, first, "operation-A"
                )
                b = pool.submit(
                    attempt, second, "operation-B"
                )

                results = (
                    a.result(timeout=20),
                    b.result(timeout=20),
                )

            self.assertEqual(
                sorted(item[0] for item in results),
                ["accepted", "rejected"],
            )

            winner = next(
                operation_id
                for outcome, operation_id in results
                if outcome == "accepted"
            )

            reopened = reopen(path)

            self.assertEqual(
                reopened.read_state(),
                (old, (winner, new)),
            )

            self.assertEqual(
                reopened.query_operation(
                    winner
                ).status.value,
                "prepared",
            )

    def test_concurrent_finalize_retry_has_one_commit(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"

            first = bootstrap(path, old)
            prepare(first, old, new)

            second = reopen(path)
            barrier = Barrier(2)

            def complete(authority):
                barrier.wait(timeout=10)

                return finalize(
                    authority, old, new
                )

            with ThreadPoolExecutor(max_workers=2) as pool:
                a = pool.submit(complete, first)
                b = pool.submit(complete, second)

                results = (
                    a.result(timeout=20),
                    b.result(timeout=20),
                )

            self.assertCountEqual(
                results,
                (True, False),
            )

            reopened = reopen(path)

            self.assertEqual(
                reopened.read_state(),
                (new, None),
            )

            self.assertEqual(
                reopened.query_operation(
                    OPERATION
                ).status.value,
                "committed",
            )

    def test_lost_prepare_reply_can_be_reconciled_after_reopen(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            def prepare_then_lose_reply():
                prepare(authority, old, new)
                raise OSError(
                    "Injected lost PREPARE acknowledgement."
                )

            with self.assertRaises(OSError):
                prepare_then_lose_reply()

            reopened = reopen(path)
            record = reopened.query_operation(OPERATION)

            self.assertEqual(record.status.value, "prepared")
            self.assertEqual(record.expected_committed, old)
            self.assertEqual(record.target, new)

            self.assertFalse(
                prepare(reopened, old, new)
            )

            self.assertTrue(
                finalize(reopened, old, new)
            )

            self.assertEqual(
                reopen(path).query_operation(
                    OPERATION
                ).status.value,
                "committed",
            )

    def test_tampered_pending_record_fails_closed(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"
            authority = bootstrap(path, old)

            prepare(authority, old, new)

            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute(
                    "UPDATE publication_operations "
                    "SET target_catalog_digest=? "
                    "WHERE operation_id=?",
                    ("invalid", OPERATION),
                )

            with self.assertRaises(ValueError):
                authority.read_state()

            with self.assertRaises(ValueError):
                authority.query_operation(OPERATION)

            with self.assertRaises(ValueError):
                reopen(path)

    def test_local_file_rollback_erases_operation_history(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)

            path = folder / "authority.sqlite3"
            backup = folder / "before-rotation.sqlite3"

            authority = bootstrap(path, old)

            shutil.copyfile(path, backup)

            prepare(authority, old, new)
            finalize(authority, old, new)

            self.assertEqual(
                reopen(path).query_operation(
                    OPERATION
                ).status.value,
                "committed",
            )

            # Deliberately restore the entire old SQLite
            # database. A local file is NOT a rollback-
            # resistant independent authority.
            shutil.copyfile(backup, path)

            restored = reopen(path)

            self.assertEqual(
                restored.read_state(),
                (old, None),
            )

            self.assertIsNone(
                restored.query_operation(OPERATION)
            )

            # This is a documented security limitation,
            # not a passing production anti-rollback test.


    def test_completed_digest_tamper_blocks_open(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"

            authority = bootstrap(path, old)
            prepare(authority, old, new)
            finalize(authority, old, new)

            replacement = (
                "f" * 64
                if new[2] != "f" * 64
                else "e" * 64
            )

            with closing(sqlite3.connect(path)) as connection:
                with connection:
                    connection.execute(
                        "UPDATE publication_operations "
                        "SET target_catalog_digest=? "
                        "WHERE operation_id=?",
                        (replacement, OPERATION),
                    )

            # An individually valid SHA256-shaped digest
            # must not silently change committed history.
            with self.assertRaises(ValueError):
                reopen(path)

            with self.assertRaises(ValueError):
                authority.read_state()

    def test_deleting_terminal_outcome_blocks_open(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"

            authority = bootstrap(path, old)
            prepare(authority, old, new)
            finalize(authority, old, new)

            with closing(sqlite3.connect(path)) as connection:
                with connection:
                    connection.execute(
                        "DELETE FROM publication_operations "
                        "WHERE operation_id=?",
                        (OPERATION,),
                    )

            # Keeping revision 2 while erasing the only
            # completed operation must be inconsistent.
            with self.assertRaises(ValueError):
                reopen(path)

    def test_deleting_intermediate_outcome_blocks_open(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        third = (
            new[0] + 1,
            new[1],
            (
                "a" * 64
                if new[2] != "a" * 64
                else "b" * 64
            ),
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"

            authority = bootstrap(path, old)

            prepare(
                authority,
                old,
                new,
                operation_id="first-publication",
            )
            finalize(
                authority,
                old,
                new,
                operation_id="first-publication",
            )

            prepare(
                authority,
                new,
                third,
                operation_id="second-publication",
            )
            finalize(
                authority,
                new,
                third,
                operation_id="second-publication",
            )

            self.assertEqual(
                reopen(path).read_state(),
                (third, None),
            )

            with closing(sqlite3.connect(path)) as connection:
                with connection:
                    connection.execute(
                        "DELETE FROM publication_operations "
                        "WHERE operation_id=?",
                        ("first-publication",),
                    )

            # The second publication cannot establish
            # an uninterrupted chain from bootstrap.
            with self.assertRaises(ValueError):
                reopen(path)

    def test_duplicate_committed_outcome_blocks_open(self):
        initial, revoked = lifecycle_pair()
        old, new = snapshot(initial), snapshot(revoked)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "authority.sqlite3"

            authority = bootstrap(path, old)
            prepare(authority, old, new)
            finalize(authority, old, new)

            with closing(sqlite3.connect(path)) as connection:
                with connection:
                    connection.execute(
                        "INSERT INTO publication_operations "
                        "(operation_id, "
                        "expected_revision, "
                        "expected_sources_digest, "
                        "expected_catalog_digest, "
                        "target_revision, "
                        "target_sources_digest, "
                        "target_catalog_digest, status) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            "duplicate-committed",
                            *old,
                            *new,
                            "committed",
                        ),
                    )

            # Two different operation IDs must not claim
            # the same committed transition.
            with self.assertRaises(ValueError):
                reopen(path)


if __name__ == "__main__":
    unittest.main()
