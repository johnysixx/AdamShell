"""A44 read-only consistency gate between signed SQLite authority and anchor.

SECURITY LIMITATIONS:
- The injected anchor is not independently authenticated or enrolled here.
- Equality of observations cannot prove rollback resistance or durability.
- The anchor must supply its own trustworthy monotonic storage and lease.
- No cross-store atomicity, checkpoint restore, or republication authority.
- Python objects and frozen dataclasses are not security boundaries.
"""

import hmac

from contextlib import contextmanager
from dataclasses import dataclass

from core.existence.history_receipt_trust_independent_authority_contract import (
    _require_identity,
)
from core.existence.history_receipt_trust_checkpoint_external_monotonic_authority import (
    SignedCheckpointExternalMonotonicAuthoritySource,
)

_MAX_COUNTER = (1 << 63) - 1


def _require_signed_source(source):
    if type(source) is not SignedCheckpointExternalMonotonicAuthoritySource:
        raise ValueError("Expected canonical signed authority source.")
    source.__post_init__()
    return source


def _require_anchor_source(source):
    if not callable(getattr(source, "hold", None)):
        raise ValueError("External anchor held read unavailable.")
    return source


def _require_key(value, name):
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(f"Invalid {name}.")
    return bytes(value)


def _require_counter(value, name):
    if type(value) is not int or not 0 <= value <= _MAX_COUNTER:
        raise ValueError(f"Invalid {name}.")
    return value


def _require_exact_key(actual, expected, name):
    key = _require_key(actual, name)
    if not hmac.compare_digest(key, _require_key(expected, name)):
        raise ValueError(f"{name} mismatch.")
    return key


def _validated_anchor(snapshot, source):
    if type(snapshot) is not tuple or len(snapshot) != 8:
        raise ValueError("Malformed external anchor snapshot.")

    (authority_id, authority_key, root_id, root_key,
     epoch, revision, generation, fence_token) = snapshot

    if _require_identity(authority_id, "anchor authority identity") != source.expected_authority_id:
        raise ValueError("External anchor authority identity mismatch.")

    _require_exact_key(
        authority_key,
        source.expected_authority_public_key,
        "anchor authority key",
    )

    if _require_identity(root_id, "anchor root identity") != source.expected_root_id:
        raise ValueError("External anchor root identity mismatch.")

    root_key = _require_exact_key(
        root_key,
        source.expected_root_public_key,
        "anchor root key",
    )

    epoch = _require_counter(epoch, "anchor enrollment epoch")
    revision = _require_counter(revision, "anchor revision")
    generation = _require_counter(generation, "anchor generation")
    fence_token = _require_counter(fence_token, "anchor fencing token")

    if epoch != source.expected_enrollment_epoch:
        raise ValueError("External anchor enrollment epoch mismatch.")

    return root_id, root_key, epoch, revision, generation, fence_token


def _validated_signed(snapshot, source):
    if type(snapshot) is not tuple or len(snapshot) != 6:
        raise ValueError("Malformed signed authority snapshot.")

    root_id, root_key, epoch, revision, generation, fence_token = snapshot

    if _require_identity(root_id, "signed root identity") != source.expected_root_id:
        raise ValueError("Signed root identity mismatch.")

    root_key = _require_exact_key(
        root_key,
        source.expected_root_public_key,
        "signed root key",
    )

    epoch = _require_counter(epoch, "signed enrollment epoch")
    revision = _require_counter(revision, "signed revision")
    generation = _require_counter(generation, "signed generation")
    fence_token = _require_counter(fence_token, "signed fencing token")

    if epoch != source.expected_enrollment_epoch:
        raise ValueError("Signed enrollment epoch mismatch.")

    return root_id, root_key, epoch, revision, generation, fence_token


@dataclass(frozen=True, slots=True)
class CheckpointExternalAnchorReadGate:
    """Read-only equality gate; does not authenticate the anchor."""

    signed_source: SignedCheckpointExternalMonotonicAuthoritySource
    anchor_source: object

    def __post_init__(self):
        _require_signed_source(self.signed_source)
        _require_anchor_source(self.anchor_source)

    @classmethod
    def from_sources(cls, *, signed_source, anchor_source):
        try:
            return cls(
                signed_source=signed_source,
                anchor_source=anchor_source,
            )
        except Exception as exc:
            raise ValueError("External anchor gate binding failed.") from exc

    @contextmanager
    def hold(self):
        caller_completed = False
        signed_released = False
        anchor_released = False

        try:
            self.__post_init__()

            with self.anchor_source.hold() as anchor_raw:
                anchored = _validated_anchor(
                    anchor_raw,
                    self.signed_source,
                )

                with self.signed_source.hold() as signed_raw:
                    signed = _validated_signed(
                        signed_raw,
                        self.signed_source,
                    )

                    if signed != anchored:
                        raise ValueError(
                            "Signed authority and external anchor diverged."
                        )

                    yield signed
                    caller_completed = True

                signed_released = True

            anchor_released = True

            if not (
                caller_completed
                and signed_released
                and anchor_released
            ):
                raise ValueError(
                    "External anchor verification scope incomplete."
                )

        except Exception as exc:
            raise ValueError(
                "External anchor held read failed."
            ) from exc
