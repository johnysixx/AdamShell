"""Cooperative cross-process locking for durable inboxes.

Windows: msvcrt byte-range lock.
POSIX: fcntl flock.

A process-local mutex additionally serializes threads.
The stable .lock file must never be unlinked during use.
"""

import errno
import math
import os
import threading
import time
from contextlib import contextmanager
from pathlib import Path


_REGISTRY_GUARD = threading.Lock()
_LOCAL_LOCKS = {}


def _local_lock(path):
    identity = str(path.resolve())

    with _REGISTRY_GUARD:
        if identity not in _LOCAL_LOCKS:
            _LOCAL_LOCKS[identity] = threading.Lock()

        return _LOCAL_LOCKS[identity]


@contextmanager
def exclusive_inbox_lock(path, *, timeout=5.0):
    """Hold a stable local and OS file lock.

    The lock protects a complete read-check-write cycle.
    Timeout is bounded; exceptions release both locks.
    """

    if (
        type(timeout) not in (int, float)
        or not math.isfinite(timeout)
        or timeout < 0
    ):
        raise ValueError(
            "Inbox lock timeout must be finite and nonnegative."
        )

    inbox_path = Path(path).resolve()

    if not inbox_path.parent.is_dir():
        raise FileNotFoundError(
            "Inbox lock directory does not exist."
        )

    lock_path = inbox_path.with_name(
        inbox_path.name + ".lock"
    )

    local = _local_lock(lock_path)
    deadline = time.monotonic() + timeout

    if not local.acquire(timeout=timeout):
        raise TimeoutError(
            "Timed out waiting for local inbox lock."
        )

    try:
        with lock_path.open("a+b") as stream:
            # msvcrt locks a byte range. Ensure byte zero
            # exists even for an initially empty lock file.
            if stream.seek(0, os.SEEK_END) == 0:
                stream.write(b"0")
                stream.flush()

            acquired = False

            try:
                while True:
                    stream.seek(0)

                    try:
                        if os.name == "nt":
                            import msvcrt

                            msvcrt.locking(
                                stream.fileno(),
                                msvcrt.LK_NBLCK,
                                1,
                            )
                        else:
                            import fcntl

                            fcntl.flock(
                                stream.fileno(),
                                fcntl.LOCK_EX
                                | fcntl.LOCK_NB,
                            )

                        acquired = True
                        break

                    except OSError as error:
                        if error.errno not in (
                            errno.EACCES,
                            errno.EAGAIN,
                            errno.EDEADLK,
                        ):
                            raise

                        remaining = (
                            deadline - time.monotonic()
                        )

                        if remaining <= 0:
                            raise TimeoutError(
                                "Timed out waiting for "
                                "cross-process inbox lock."
                            ) from error

                        time.sleep(
                            min(0.025, remaining)
                        )

                yield

            finally:
                if acquired:
                    stream.seek(0)

                    if os.name == "nt":
                        import msvcrt

                        msvcrt.locking(
                            stream.fileno(),
                            msvcrt.LK_UNLCK,
                            1,
                        )
                    else:
                        import fcntl

                        fcntl.flock(
                            stream.fileno(),
                            fcntl.LOCK_UN,
                        )

    finally:
        local.release()
