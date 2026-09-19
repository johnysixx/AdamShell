from dataclasses import dataclass


@dataclass(slots=True)
class CatGroupRoleState:
    group_id: str | None = None
    score: float | None = None
    base_role: str | None = None
    specialized: bool = False

    def assign_base(
        self,
        group_id,
        score,
    ):
        self.group_id = group_id
        self.score = float(score)
        self.base_role = None
        self.specialized = False

        return self

    def assign_specialization(
        self,
        group_id,
        base_role,
    ):
        self.group_id = group_id
        self.score = None
        self.base_role = base_role
        self.specialized = True

        return self
