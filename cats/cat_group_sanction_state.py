from dataclasses import dataclass, field

from cats.cat_culture_objects import CatViolation


@dataclass(slots=True, frozen=True)
class CatGroupSanctionEvent:
    group_id: str
    cat: str
    sanction: str
    severity: float
    source_violation: CatViolation
    name: str = field(default="cat_group_sanction", init=False)
