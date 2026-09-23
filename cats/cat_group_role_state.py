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


@dataclass(slots=True, frozen=True)
class CatGroupRoleAssignedEvent:
    group_id: str
    cat: str
    role: str
    score: float
    name: str = "cat_group_role_assigned"
    assigned: bool = True

    def __post_init__(self):
        object.__setattr__(
            self,
            "group_id",
            str(self.group_id),
        )
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )
        object.__setattr__(
            self,
            "role",
            str(self.role),
        )
        object.__setattr__(
            self,
            "score",
            float(self.score),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "group_id": self.group_id,
            "cat": self.cat,
            "role": self.role,
            "score": self.score,
            "assigned": self.assigned,
        }


@dataclass(slots=True, frozen=True)
class CatGroupRoleReleasedEvent:
    group_id: str
    cat: str
    role: str
    reason: str
    name: str = "cat_group_role_released"
    released: bool = True

    def __post_init__(self):
        object.__setattr__(
            self,
            "group_id",
            str(self.group_id),
        )
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )
        object.__setattr__(
            self,
            "role",
            str(self.role),
        )
        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "group_id": self.group_id,
            "cat": self.cat,
            "role": self.role,
            "reason": self.reason,
            "released": self.released,
        }


@dataclass(slots=True, frozen=True)
class CatGroupRoleSpecializedEvent:
    group_id: str
    cat: str
    base_role: str
    specialization: str
    name: str = "cat_group_role_specialized"
    specialized: bool = True

    def __post_init__(self):
        object.__setattr__(
            self,
            "group_id",
            str(self.group_id),
        )
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )
        object.__setattr__(
            self,
            "base_role",
            str(self.base_role),
        )
        object.__setattr__(
            self,
            "specialization",
            str(self.specialization),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "group_id": self.group_id,
            "cat": self.cat,
            "base_role": self.base_role,
            "specialization": self.specialization,
            "specialized": self.specialized,
        }
