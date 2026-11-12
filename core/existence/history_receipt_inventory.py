"""Read-only inventory of independently verified receipt observations.

One receipt observed repeatedly is not multiple executions.
Multiple authentic receipts do not establish multiple executions.
This inventory is stateless and never authorizes or records consumption.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum

from .history_receipt_proof import verify_signed_receipt
from .history_reconciliation_proposal import (
    EvidenceVerdict,
    ExternalEvidence,
)


class ReceiptInventoryFinding(str, Enum):
    SINGLE_RECEIPT = "single_receipt"
    REOBSERVED_RECEIPT = "reobserved_receipt"
    MULTIPLE_RECEIPTS = "multiple_receipts"


class ReceiptRejectionReason(str, Enum):
    MALFORMED_OBSERVATION = "malformed_observation"
    NOT_CONFIRMED = "not_confirmed"
    UNVERIFIED_RECEIPT = "unverified_receipt"


@dataclass(frozen=True, slots=True)
class ReceiptInventoryGroup:
    source_id: str
    cycle_id: str
    branch_id: str
    effect_id: str
    receipt_ids: tuple[str, ...]
    observation_count: int
    reobservation_count: int
    finding: ReceiptInventoryFinding

    @property
    def distinct_receipt_count(self):
        return len(self.receipt_ids)


@dataclass(frozen=True, slots=True)
class ReceiptInventoryRejection:
    observation_index: int
    reason: ReceiptRejectionReason


@dataclass(frozen=True, slots=True)
class ReceiptInventoryReport:
    groups: tuple[ReceiptInventoryGroup, ...]
    rejected: tuple[ReceiptInventoryRejection, ...]
    total_observations: int
    accepted_observations: int

    @property
    def retry_allowed(self):
        return False

    @property
    def mutation_allowed(self):
        return False

    @property
    def independent_executions_proven(self):
        return False


def _valid_claims(evidence):
    if type(evidence) is not ExternalEvidence:
        return False

    if type(evidence.verdict) is not EvidenceVerdict:
        return False

    fields = (
        evidence.source_id,
        evidence.cycle_id,
        evidence.branch_id,
        evidence.effect_id,
        evidence.receipt_id,
    )

    return all(
        type(value) is str
        and 0 < len(value) <= 1024
        for value in fields
    )


def inventory_receipt_observations(
    observations,
    *,
    trusted_provider_keys,
):
    """Classify signed observations without consulting or modifying history.

    The caller controls the trusted key mapping. Untrusted or missing
    keys cannot authenticate evidence. All inputs are observations,
    not execution or consumption records.

    A repeated receipt remains a repeated observation, never a second
    execution. Multiple signed receipts require human investigation.
    """

    groups = defaultdict(Counter)
    rejected = []
    total = 0
    accepted = 0

    for index, evidence in enumerate(observations):
        total += 1

        if not _valid_claims(evidence):
            rejected.append(
                ReceiptInventoryRejection(
                    index,
                    ReceiptRejectionReason.MALFORMED_OBSERVATION,
                )
            )
            continue

        if evidence.verdict is not EvidenceVerdict.CONFIRMED:
            rejected.append(
                ReceiptInventoryRejection(
                    index,
                    ReceiptRejectionReason.NOT_CONFIRMED,
                )
            )
            continue

        try:
            authenticated = verify_signed_receipt(
                evidence.signed_receipt,
                cycle_id=evidence.cycle_id,
                branch_id=evidence.branch_id,
                effect_id=evidence.effect_id,
                expected_source_id=evidence.source_id,
                receipt_id=evidence.receipt_id,
                trusted_provider_keys=trusted_provider_keys,
            )
        except Exception:
            authenticated = False

        if not authenticated:
            rejected.append(
                ReceiptInventoryRejection(
                    index,
                    ReceiptRejectionReason.UNVERIFIED_RECEIPT,
                )
            )
            continue

        identity = (
            evidence.source_id,
            evidence.cycle_id,
            evidence.branch_id,
            evidence.effect_id,
        )

        groups[identity][evidence.receipt_id] += 1
        accepted += 1

    result_groups = []

    for identity, counts in sorted(groups.items()):
        receipt_ids = tuple(sorted(counts))
        observations_in_group = sum(counts.values())
        distinct_count = len(receipt_ids)

        if distinct_count > 1:
            finding = ReceiptInventoryFinding.MULTIPLE_RECEIPTS
        elif observations_in_group > 1:
            finding = ReceiptInventoryFinding.REOBSERVED_RECEIPT
        else:
            finding = ReceiptInventoryFinding.SINGLE_RECEIPT

        result_groups.append(
            ReceiptInventoryGroup(
                source_id=identity[0],
                cycle_id=identity[1],
                branch_id=identity[2],
                effect_id=identity[3],
                receipt_ids=receipt_ids,
                observation_count=observations_in_group,
                reobservation_count=(
                    observations_in_group - distinct_count
                ),
                finding=finding,
            )
        )

    return ReceiptInventoryReport(
        groups=tuple(result_groups),
        rejected=tuple(rejected),
        total_observations=total,
        accepted_observations=accepted,
    )
