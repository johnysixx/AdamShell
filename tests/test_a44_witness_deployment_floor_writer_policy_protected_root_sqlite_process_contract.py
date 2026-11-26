"""Real-process persistence and crash contract.

All root operations use independent Python processes where
required. File markers coordinate test workers without relying
solely on process startup timing.

Abrupt termination is not a physical power-loss simulation.

The pre-commit fault uses SQLite tracing at the actual root
state transaction COMMIT boundary.
"""

import json
import os
import subprocess
import signal
import sys
import time
import unittest

from pathlib import Path

import test_a44_witness_deployment_floor_writer_policy_protected_root_sqlite_contract as previous


WORKER = r"""
import importlib
import json
import os
import sqlite3
import sys
import time

from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "tests"))

import test_a44_witness_deployment_floor_writer_policy_protected_root_backend_contract as objects

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_sqlite_reference"
)

mode, raw_path, raw_marker = sys.argv[1:4]

path = Path(raw_path).resolve()
marker = Path(raw_marker)

ready = marker.with_suffix(".ready")
gate = marker.with_suffix(".gate")
attempt = marker.with_suffix(".attempt")
crash = marker.with_suffix(".crash")

identity_path = marker.with_suffix(".pid")
identity_temp = marker.with_suffix(".pid.tmp")

identity_temp.write_text(
    json.dumps({
        "pid": os.getpid(),
        "ppid": os.getppid(),
    }),
    encoding="utf-8",
)

identity_temp.replace(identity_path)


def wait_gate():

    deadline = time.monotonic() + 60

    while not gate.exists():

        if time.monotonic() >= deadline:
            raise TimeoutError("Worker gate timeout")

        time.sleep(0.02)

    attempt.touch()


def emit(status, reference):

    print(
        json.dumps({
            "pid": os.getpid(),
            "status": status,
            "revision": reference.revision,
            "sha256": reference.sha256,
        }),
        flush=True,
    )


fixture = objects.A44ProtectedRootBackendContractTests(
    "test_01_explicit_provisioning"
)

fixture.setUp()

module = importlib.import_module(MODULE)

armed = False

original_connect = sqlite3.connect


def traced_connect(*args, **kwargs):

    connection = original_connect(*args, **kwargs)

    rows = connection.execute(
        "PRAGMA database_list"
    ).fetchall()

    is_root = any(
        name == "main"
        and filename
        and Path(filename).resolve() == path
        for _, name, filename in rows
    )

    if is_root:

        def trace(statement):

            normalized = statement.strip().upper()

            if (
                armed
                and connection.total_changes > 0
                and normalized.startswith(("COMMIT", "END"))
            ):

                crash.touch()

                # Terminate before SQLite executes COMMIT.
                os._exit(79)

        connection.set_trace_callback(trace)

    return connection


if mode == "crash-before-commit":
    sqlite3.connect = traced_connect


backend = module.SQLiteProtectedRootBackend.open(
    path=path,
    expected_identity=fixture.identity,
)

initial = fixture.initial


def advance(old, new):

    return backend.compare_and_set(
        expected=old.reference(),
        replacement=new,
    )


try:

    if mode == "stable":

        emit(
            "committed",
            backend.provision(state=initial),
        )

    elif mode == "prepared":

        pending = fixture.pending()

        emit(
            "committed",
            advance(initial, pending),
        )

        os._exit(73)

    elif mode == "finalized":

        pending = fixture.pending()

        emit(
            "committed",
            advance(
                pending,
                fixture.finalized(pending),
            ),
        )

        os._exit(74)

    elif mode == "inspect":

        emit(
            "observed",
            backend.read().reference(),
        )

    elif mode in ("cas", "cas-a", "cas-b", "provision"):

        if mode == "cas":

            candidate = fixture.pending()

        elif mode in ("cas-a", "cas-b"):

            candidate = fixture.pending(
                fixture.prepared(
                    message=mode.encode("ascii")
                )
            )

        ready.touch()

        wait_gate()

        try:

            if mode == "provision":

                result = backend.provision(state=initial)

            else:

                result = advance(initial, candidate)

        except ValueError:

            emit(
                "rejected",
                backend.read().reference(),
            )

        else:

            emit("committed", result)

    elif mode in ("hold", "hold-prepared"):

        with backend.exclusive():

            if mode == "hold-prepared":

                pending = fixture.pending()

                emit(
                    "committed",
                    advance(initial, pending),
                )

            else:

                emit(
                    "holding",
                    backend.read().reference(),
                )

            ready.touch()

            wait_gate()

    elif mode == "crash-before-commit":

        pending = fixture.pending()

        armed = True

        advance(initial, pending)

        raise AssertionError(
            "Expected abrupt exit before root COMMIT"
        )

    elif mode == "recover":

        current = backend.read()

        if current.durable_state.prepared is not None:

            current = fixture.finalized(current)

            advance(
                backend.read(),
                current,
            )

        emit(
            "recovered",
            current.reference(),
        )

    else:

        raise AssertionError("Unknown worker mode: " + mode)

finally:

    fixture.doCleanups()
"""


class A44SQLiteProtectedRootProcessContractTests(unittest.TestCase):

    def setUp(self):

        self.f = previous.A44SQLiteProtectedRootContractTests(
            "test_01_explicit_create_and_unprovisioned_open"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.backend = self.f.backend
        self.initial = self.f.initial
        self.objects = self.f.f

    def start(self, mode, name):

        marker = self.f.directory / name

        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-c",
                WORKER,
                mode,
                str(self.f.path),
                str(marker),
            ],
            cwd=Path.cwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        self.addCleanup(self.stop, (process, marker))

        return process, marker

    def worker_pid(self, worker):

        process, marker = worker

        identity_path = marker.with_suffix(".pid")

        self.assertTrue(
            identity_path.is_file(),
            "Actual worker identity marker missing",
        )

        identity = json.loads(
            identity_path.read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(identity),
            {"pid", "ppid"},
        )

        pid = identity["pid"]
        ppid = identity["ppid"]

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
            "Worker is neither the launched process "
            "nor its verified direct child",
        )

        return pid

    def terminate_worker(self, worker):

        process, _ = worker

        self.assertIsNone(process.poll())

        pid = self.worker_pid(worker)

        if pid == process.pid:

            process.kill()

        else:

            # Terminate the actual Python child, not merely
            # the Windows virtualenv redirector.

            os.kill(pid, signal.SIGTERM)

    def stop(self, worker):

        process, marker = worker

        if process.poll() is None:

            if marker.with_suffix(".pid").is_file():

                try:
                    self.terminate_worker(worker)

                except OSError:
                    if process.poll() is None:
                        raise

            elif os.name == "nt":

                # Startup failed before identity publication.
                # Clean up only this test's launched process tree.

                result = subprocess.run(
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

                if (
                    result.returncode != 0
                    and process.poll() is None
                ):

                    raise RuntimeError(
                        "Worker process-tree cleanup failed"
                    )

            else:

                process.kill()

        process.communicate(timeout=15)

    def wait_marker(self, worker, suffix):

        process, marker = worker

        target = marker.with_suffix(suffix)

        deadline = time.monotonic() + 30

        while not target.exists():

            if process.poll() is not None:

                stdout, stderr = process.communicate()

                self.fail(
                    "Worker exited before marker: "
                    + str(target)
                    + "\n"
                    + stdout
                    + "\n"
                    + stderr
                )

            if time.monotonic() >= deadline:
                self.fail("Worker marker timeout: " + str(target))

            time.sleep(0.02)

    def release(self, worker):

        _, marker = worker

        marker.with_suffix(".gate").touch()

    def finish(self, worker, expected_exit=0):

        process, _ = worker

        stdout, stderr = process.communicate(timeout=45)

        self.assertEqual(
            process.returncode,
            expected_exit,
            stdout + "\n" + stderr,
        )

        lines = stdout.strip().splitlines()

        self.assertTrue(lines, stdout + "\n" + stderr)

        result = json.loads(lines[-1])

        self.assertEqual(result["pid"], self.worker_pid(worker))
        self.assertNotEqual(result["pid"], os.getpid())

        return result

    def run_worker(self, mode, name, expected_exit=0):

        return self.finish(
            self.start(mode, name),
            expected_exit=expected_exit,
        )

    def assert_result(self, result, expected, status):

        reference = expected.reference()

        self.assertEqual(result["status"], status)
        self.assertEqual(result["revision"], reference.revision)
        self.assertEqual(result["sha256"], reference.sha256)

    def assert_blocked(self, worker):

        process, _ = worker

        with self.assertRaises(subprocess.TimeoutExpired):
            process.wait(timeout=0.35)

    def kill_holder(self, worker):

        process, _ = worker

        self.assertIsNone(process.poll())

        self.terminate_worker(worker)

        stdout, stderr = process.communicate(timeout=15)

        self.assertNotEqual(
            process.returncode,
            0,
            stdout + "\n" + stderr,
        )

    def test_01_stable_survives_process_exit(self):

        result = self.run_worker("stable", "stable")

        self.assert_result(result, self.initial, "committed")

        self.f.assert_state(self.f.reopen(), self.initial)

        observed = self.run_worker("inspect", "stable-inspect")

        self.assert_result(observed, self.initial, "observed")

    def test_02_prepared_survives_abrupt_exit(self):

        self.f.provision()

        pending = self.objects.pending()

        result = self.run_worker(
            "prepared",
            "prepared-crash",
            expected_exit=73,
        )

        self.assert_result(result, pending, "committed")

        actual = self.f.assert_state(
            self.f.reopen(),
            pending,
        )

        self.assertEqual(
            actual.durable_state.prepared.signed_policy,
            pending.durable_state.prepared.signed_policy,
        )

        observed = self.run_worker("inspect", "pending-inspect")

        self.assert_result(observed, pending, "observed")

    def test_03_finalization_survives_abrupt_exit(self):

        self.f.provision()

        pending = self.objects.pending()
        final = self.objects.finalized(pending)

        self.f.advance(self.initial, pending)

        result = self.run_worker(
            "finalized",
            "final-crash",
            expected_exit=74,
        )

        self.assert_result(result, final, "committed")

        self.f.assert_state(self.f.reopen(), final)

        observed = self.run_worker("inspect", "final-inspect")

        self.assert_result(observed, final, "observed")

    def test_04_cross_process_fence_blocks_competing_cas(self):

        self.f.provision()

        pending = self.objects.pending()

        worker = self.start("cas", "competing-cas")

        self.wait_marker(worker, ".ready")

        with self.backend.exclusive():

            self.release(worker)

            self.wait_marker(worker, ".attempt")

            self.assert_blocked(worker)

            self.f.assert_state(self.backend, self.initial)

        result = self.finish(worker)

        self.assert_result(result, pending, "committed")

        self.f.assert_state(self.f.reopen(), pending)

    def test_05_terminated_holder_releases_fence(self):

        self.f.provision()

        pending = self.objects.pending()

        competitor = self.start("cas", "waiting-cas")

        self.wait_marker(competitor, ".ready")

        holder = self.start("hold", "fence-holder")

        self.wait_marker(holder, ".ready")

        self.release(competitor)

        self.wait_marker(competitor, ".attempt")

        self.assert_blocked(competitor)

        self.kill_holder(holder)

        result = self.finish(competitor)

        self.assert_result(result, pending, "committed")

        self.f.assert_state(self.f.reopen(), pending)

    def test_06_prepared_commit_survives_terminated_fence_holder(self):

        self.f.provision()

        pending = self.objects.pending()

        holder = self.start(
            "hold-prepared",
            "prepared-holder",
        )

        self.wait_marker(holder, ".ready")

        self.kill_holder(holder)

        actual = self.f.assert_state(
            self.f.reopen(),
            pending,
        )

        self.assertEqual(
            actual.durable_state.prepared.signed_policy,
            pending.durable_state.prepared.signed_policy,
        )

        final = self.objects.finalized(pending)

        result = self.run_worker("recover", "recover-holder")

        self.assert_result(result, final, "recovered")

        self.f.assert_state(self.f.reopen(), final)

    def test_07_concurrent_process_provisioning_has_one_winner(self):

        workers = [
            self.start("provision", "provision-a"),
            self.start("provision", "provision-b"),
        ]

        for worker in workers:
            self.wait_marker(worker, ".ready")

        for worker in workers:
            self.release(worker)

        results = [
            self.finish(worker)
            for worker in workers
        ]

        self.assertCountEqual(
            [result["status"] for result in results],
            ["committed", "rejected"],
        )

        for result in results:

            self.assert_result(
                result,
                self.initial,
                result["status"],
            )

        self.f.assert_state(self.f.reopen(), self.initial)

    def test_08_conflicting_process_cas_has_one_winner(self):

        self.f.provision()

        candidates = [
            self.objects.pending(
                self.objects.prepared(message=b"cas-a")
            ),
            self.objects.pending(
                self.objects.prepared(message=b"cas-b")
            ),
        ]

        workers = [
            self.start("cas-a", "conflict-a"),
            self.start("cas-b", "conflict-b"),
        ]

        for worker in workers:
            self.wait_marker(worker, ".ready")

        for worker in workers:
            self.release(worker)

        results = [
            self.finish(worker)
            for worker in workers
        ]

        self.assertCountEqual(
            [result["status"] for result in results],
            ["committed", "rejected"],
        )

        winner = next(
            index for index, result in enumerate(results)
            if result["status"] == "committed"
        )

        retained = candidates[winner]

        self.assert_result(
            results[winner],
            retained,
            "committed",
        )

        self.assert_result(
            results[1 - winner],
            retained,
            "rejected",
        )

        self.f.assert_state(self.f.reopen(), retained)

    def test_09_uncommitted_root_write_rolls_back_after_process_loss(self):

        self.f.provision()

        worker = self.start(
            "crash-before-commit",
            "before-commit",
        )

        process, marker = worker

        stdout, stderr = process.communicate(timeout=45)

        self.assertEqual(
            process.returncode,
            79,
            stdout + "\n" + stderr,
        )

        self.assertTrue(
            marker.with_suffix(".crash").is_file(),
            "Actual root COMMIT boundary was not reached",
        )

        self.f.assert_state(
            self.f.reopen(),
            self.initial,
        )

        pending = self.objects.pending()

        self.f.advance(
            self.initial,
            pending,
            backend=self.f.reopen(),
        )

        self.f.assert_state(self.f.reopen(), pending)

    def test_10_repeated_process_recovery_is_revision_idempotent(self):

        self.f.provision()

        pending = self.objects.pending()
        final = self.objects.finalized(pending)

        self.f.advance(self.initial, pending)

        first = self.run_worker("recover", "recover-first")

        self.assert_result(first, final, "recovered")

        second = self.run_worker("recover", "recover-second")

        self.assert_result(second, final, "recovered")

        third = self.run_worker("inspect", "recover-inspect")

        self.assert_result(third, final, "observed")

        self.f.assert_state(self.f.reopen(), final)


if __name__ == "__main__":
    unittest.main()
