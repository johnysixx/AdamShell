from dataclasses import dataclass, field

from cats.cat_distribution_status import CatDistributionStatus


@dataclass(slots=True, frozen=True)
class CatDistributionSkippedResult:
    cat: str
    reason: str
    name: str = field(default="cat_distribution_skipped", init=False)
    distributed: bool = field(default=False, init=False)


@dataclass(slots=True, frozen=True)
class CatAssignedToRecipientEvent:
    cat: str
    recipient: str
    status: CatDistributionStatus
    name: str = field(default="cat_assigned_to_recipient", init=False)
    distributed: bool = field(default=True, init=False)


@dataclass(slots=True, frozen=True)
class CatDistributionSuggestedResult:
    cat: str
    status: CatDistributionStatus
    suggested_layer: str
    name: str = field(default="cat_distribution_suggested", init=False)
    distributed: bool = field(default=False, init=False)
