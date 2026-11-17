"""Read-only A44 trust publication state classification.

Classification never authenticates an anchor, grants authority,
publishes trust, modifies SQLite, or performs recovery.

Even MATCHED_COMMITTED is informational only.
"""

import hmac
import re

from dataclasses import dataclass
from enum import Enum


_HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class TrustPublicationFinding(str, Enum):
    MATCHED_COMMITTED = "matched_committed"

    HOLD_SQLITE_BEHIND = "hold_sqlite_behind"
    HOLD_SQLITE_AHEAD = "hold_sqlite_ahead"

    HOLD_CATALOG_CONFLICT = "hold_catalog_conflict"
    HOLD_PENDING_PUBLICATION = "hold_pending_publication"

    HOLD_ANCHOR_UNAVAILABLE = "hold_anchor_unavailable"
    HOLD_INVALID_SNAPSHOT = "hold_invalid_snapshot"


@dataclass(frozen=True, slots=True)
class TrustPublicationStateReport:
    """Classification result without execution authority."""

    finding: TrustPublicationFinding

    @property
    def authorizes_verification(self):
        return False

    @property
    def retry_allowed(self):
        return False

    @property
    def mutation_allowed(self):
        return False


def _valid_snapshot(snapshot):
    """Validate canonical revision and catalog fingerprints."""

    if (
        type(snapshot) is not tuple
        or len(snapshot) != 3
    ):
        return False

    revision, sources_digest, catalog_digest = snapshot

    return (
        type(revision) is int
        and revision >= 1
        and type(sources_digest) is str
        and _HEX_SHA256.fullmatch(sources_digest) is not None
        and type(catalog_digest) is str
        and _HEX_SHA256.fullmatch(catalog_digest) is not None
    )


def _report(finding):
    return TrustPublicationStateReport(finding=finding)


def classify_publication_state(
    *,
    sqlite_snapshot,
    committed_anchor_snapshot,
    pending_anchor_snapshot=None,
    anchor_available=True,
):
    """Classify supplied snapshots without side effects.

    The caller must separately establish the provenance and
    consistency of the snapshots. A matching report does not
    authorize signature verification or trust publication.
    """

    if (
        type(anchor_available) is not bool
        or not anchor_available
        or committed_anchor_snapshot is None
    ):
        return _report(
            TrustPublicationFinding.HOLD_ANCHOR_UNAVAILABLE
        )

    if (
        not _valid_snapshot(sqlite_snapshot)
        or not _valid_snapshot(committed_anchor_snapshot)
    ):
        return _report(
            TrustPublicationFinding.HOLD_INVALID_SNAPSHOT
        )

    sqlite_revision, sqlite_sources, sqlite_catalog = (
        sqlite_snapshot
    )

    anchor_revision, anchor_sources, anchor_catalog = (
        committed_anchor_snapshot
    )

    if pending_anchor_snapshot is not None:
        if not _valid_snapshot(pending_anchor_snapshot):
            return _report(
                TrustPublicationFinding.HOLD_INVALID_SNAPSHOT
            )

        pending_revision, pending_sources, _ = (
            pending_anchor_snapshot
        )

        if (
            pending_revision <= anchor_revision
            or not hmac.compare_digest(
                pending_sources,
                anchor_sources,
            )
        ):
            return _report(
                TrustPublicationFinding.HOLD_INVALID_SNAPSHOT
            )

        return _report(
            TrustPublicationFinding.HOLD_PENDING_PUBLICATION
        )

    if not hmac.compare_digest(
        sqlite_sources,
        anchor_sources,
    ):
        return _report(
            TrustPublicationFinding.HOLD_CATALOG_CONFLICT
        )

    if sqlite_revision < anchor_revision:
        return _report(
            TrustPublicationFinding.HOLD_SQLITE_BEHIND
        )

    if sqlite_revision > anchor_revision:
        return _report(
            TrustPublicationFinding.HOLD_SQLITE_AHEAD
        )

    if not hmac.compare_digest(
        sqlite_catalog,
        anchor_catalog,
    ):
        return _report(
            TrustPublicationFinding.HOLD_CATALOG_CONFLICT
        )

    return _report(
        TrustPublicationFinding.MATCHED_COMMITTED
    )
