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
class CatGroupRoleSuitabilityResult:
    role: str
    eligible: bool
    score: float
    reason: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "role",
            str(self.role),
        )

        object.__setattr__(
            self,
            "eligible",
            bool(self.eligible),
        )

        object.__setattr__(
            self,
            "score",
            float(self.score),
        )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(self.reason),
            )


@dataclass(slots=True, frozen=True)
class CatGroupRoleAssignmentDeniedResult:
    group_id: str
    cat: str
    role: str
    reason: str
    name: str = "cat_group_role_denied"
    assigned: bool = False

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


@dataclass(slots=True, frozen=True)
class CatGroupRoleSpecializationDeniedResult:
    group_id: str
    cat: str
    base_role: str
    specialization: str
    reason: str
    trait: str | None = None
    required: float | None = None
    actual: float | None = None
    name: str = "cat_role_specialization_denied"
    specialized: bool = False

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

        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

        if self.trait is not None:
            object.__setattr__(
                self,
                "trait",
                str(self.trait),
            )

        if self.required is not None:
            object.__setattr__(
                self,
                "required",
                float(self.required),
            )

        if self.actual is not None:
            object.__setattr__(
                self,
                "actual",
                float(self.actual),
            )


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
