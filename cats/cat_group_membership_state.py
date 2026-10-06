from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupCandidateEvaluation:
    group_id: str
    candidate: str
    accepted: bool
    reason: str
    score: float
    hostile_members: int | None = None
    member_count: int | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "group_id",
            str(self.group_id),
        )
        object.__setattr__(
            self,
            "candidate",
            str(self.candidate),
        )
        object.__setattr__(
            self,
            "accepted",
            bool(self.accepted),
        )
        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )
        object.__setattr__(
            self,
            "score",
            float(self.score),
        )

        if self.hostile_members is not None:
            object.__setattr__(
                self,
                "hostile_members",
                int(self.hostile_members),
            )

        if self.member_count is not None:
            object.__setattr__(
                self,
                "member_count",
                int(self.member_count),
            )


@dataclass(slots=True, frozen=True)
class CatGroupJoinDeniedResult:
    group_id: str
    candidate: str
    reason: str
    score: float
    hostile_members: int | None = None
    member_count: int | None = None

    name: str = field(
        default="cat_group_join_denied",
        init=False,
    )

    joined: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupJoinSkippedResult:
    group_id: str
    cat: str
    reason: str = "already_member"

    name: str = field(
        default="cat_group_join_skipped",
        init=False,
    )

    joined: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatJoinedGroupEvent:
    group_id: str
    cat: str
    member_count: int

    name: str = field(
        default="cat_joined_group",
        init=False,
    )

    joined: bool = field(
        default=True,
        init=False,
    )
