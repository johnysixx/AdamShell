"""Fail-closed, data-only reconciliation proposals.

The provider adapter is responsible for authenticating external evidence.
This module validates correlation, checks audit freshness, and never
authorizes retry, modifies reservations, or executes external actions.
"""

from dataclasses import dataclass
from enum import Enum

from .history_reconciliation_audit import (
    ReconciliationFinding,
    audit_history_database,
)


class EvidenceVerdict(str, Enum):
    CONFIRMED = "confirmed"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"


class ProposalDecision(str, Enum):
    HOLD_MISSING_ATTEMPT = "hold_missing_attempt"
    HOLD_INVALID_HISTORY = "hold_invalid_history"
    HOLD_NO_VERIFIER = "hold_no_verifier"
    HOLD_VERIFIER_ERROR = "hold_verifier_error"
    HOLD_INVALID_EVIDENCE = "hold_invalid_evidence"
    HOLD_IDENTITY_MISMATCH = "hold_identity_mismatch"
    HOLD_NO_RECEIPT = "hold_no_receipt"
    HOLD_UNCONFIRMED = "hold_unconfirmed"
    HOLD_STALE = "hold_stale"
    REVIEW_EFFECT_CONFIRMED = "review_effect_confirmed"
    REVIEW_ARCHIVED_COMPLETED = "review_archived_completed"


@dataclass(frozen=True, slots=True)
class ExternalEvidence:
    cycle_id: str
    branch_id: str
    effect_id: str
    source_id: str
    verdict: EvidenceVerdict
    receipt_id: str | None = None


@dataclass(frozen=True, slots=True)
class ReconciliationProposal:
    cycle_id: str
    branch_id: str
    effect_id: str
    journal_status: str | None
    audit_finding: ReconciliationFinding | None
    decision: ProposalDecision
    receipt_id: str | None = None
    snapshot_sha256: str | None = None

    @property
    def retry_allowed(self):
        return False

    @property
    def mutation_allowed(self):
        return False


def _nonempty_string(value, name):
    if type(value) is not str or not value:
        raise TypeError(
            f"{name} must be a non-empty string."
        )


def _find_entry(entries, cycle_id, branch_id):
    matched = [
        entry
        for entry in entries
        if (
            entry.cycle_id == cycle_id
            and entry.branch_id == branch_id
        )
    ]

    if len(matched) > 1:
        raise RuntimeError(
            "Duplicate reconciliation audit identities."
        )

    return matched[0] if matched else None


def _classify_evidence(
    evidence,
    cycle_id,
    branch_id,
    effect_id,
    expected_source_id,
    audit_entry,
):
    if type(evidence) is not ExternalEvidence:
        return ProposalDecision.HOLD_INVALID_EVIDENCE, None

    if type(evidence.verdict) is not EvidenceVerdict:
        return ProposalDecision.HOLD_INVALID_EVIDENCE, None

    if (
        evidence.cycle_id != cycle_id
        or evidence.branch_id != branch_id
        or evidence.effect_id != effect_id
        or evidence.source_id != expected_source_id
    ):
        return ProposalDecision.HOLD_IDENTITY_MISMATCH, None

    if evidence.verdict is EvidenceVerdict.CONFIRMED:
        if (
            type(evidence.receipt_id) is not str
            or not evidence.receipt_id
        ):
            return ProposalDecision.HOLD_INVALID_EVIDENCE, None

        if (
            audit_entry.finding
            is ReconciliationFinding.ARCHIVED_COMPLETED
        ):
            decision = ProposalDecision.REVIEW_ARCHIVED_COMPLETED
        else:
            decision = ProposalDecision.REVIEW_EFFECT_CONFIRMED

        return decision, evidence.receipt_id

    if evidence.receipt_id is not None:
        return ProposalDecision.HOLD_INVALID_EVIDENCE, None

    if evidence.verdict is EvidenceVerdict.NOT_FOUND:
        return ProposalDecision.HOLD_NO_RECEIPT, None

    return ProposalDecision.HOLD_UNCONFIRMED, None


def propose_reconciliation(
    history_database,
    *,
    cycle_id,
    branch_id="root",
    effect_id,
    expected_source_id,
    verifier=None,
):
    """Return an immutable recommendation, never a write authority.

    verifier.verify(cycle_id=..., branch_id=..., effect_id=...)
    must validate a receipt with the real external provider and return
    ExternalEvidence. The string source_id alone is not authentication.
    One confirmed effect does not prove that a full cycle completed.
    """

    for name, value in (
        ("cycle_id", cycle_id),
        ("branch_id", branch_id),
        ("effect_id", effect_id),
        ("expected_source_id", expected_source_id),
    ):
        _nonempty_string(value, name)

    before = audit_history_database(history_database)
    entry = _find_entry(before, cycle_id, branch_id)

    receipt_id = None

    if entry is None:
        decision = ProposalDecision.HOLD_MISSING_ATTEMPT

    elif entry.finding not in (
        ReconciliationFinding.HOLD_UNKNOWN_OUTCOME,
        ReconciliationFinding.ARCHIVED_COMPLETED,
    ):
        decision = ProposalDecision.HOLD_INVALID_HISTORY

    elif verifier is None:
        decision = ProposalDecision.HOLD_NO_VERIFIER

    else:
        try:
            evidence = verifier.verify(
                cycle_id=cycle_id,
                branch_id=branch_id,
                effect_id=effect_id,
            )
        except Exception:
            decision = ProposalDecision.HOLD_VERIFIER_ERROR
        else:
            decision, receipt_id = _classify_evidence(
                evidence,
                cycle_id,
                branch_id,
                effect_id,
                expected_source_id,
                entry,
            )

    # A verifier may have changed the journal while consulting
    # the external system. Recheck the complete audit, not only
    # the requested entry, before returning a proposal.
    after = audit_history_database(history_database)

    if after != before:
        decision = ProposalDecision.HOLD_STALE
        receipt_id = None

    current = _find_entry(after, cycle_id, branch_id)

    return ReconciliationProposal(
        cycle_id=cycle_id,
        branch_id=branch_id,
        effect_id=effect_id,
        journal_status=(
            current.journal_status if current else None
        ),
        audit_finding=(
            current.finding if current else None
        ),
        decision=decision,
        receipt_id=receipt_id,
        snapshot_sha256=(
            current.snapshot_sha256 if current else None
        ),
    )
