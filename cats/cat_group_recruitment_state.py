from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupRecruitmentVote:
    member: str
    yes: bool
    score: float
    weight: float

    def __post_init__(self):
        object.__setattr__(
            self,
            "yes",
            bool(self.yes),
        )

        object.__setattr__(
            self,
            "score",
            float(self.score),
        )

        object.__setattr__(
            self,
            "weight",
            float(self.weight),
        )


@dataclass(slots=True, frozen=True)
class CatGroupRecruitmentVoteEvent:
    group_id: str
    candidate: str
    sponsor: str | None
    votes: tuple[
        CatGroupRecruitmentVote,
        ...
    ]
    weighted_yes: float
    weighted_no: float
    vetoes: tuple[str, ...]
    accepted: bool

    name: str = field(
        default="cat_group_recruitment_vote",
        init=False,
    )

    def __post_init__(self):
        votes = tuple(
            self.votes
        )

        for vote in votes:
            if not isinstance(
                vote,
                CatGroupRecruitmentVote,
            ):
                raise TypeError(
                    "Cat group recruitment votes "
                    "must contain "
                    "CatGroupRecruitmentVote objects."
                )

        object.__setattr__(
            self,
            "votes",
            votes,
        )

        object.__setattr__(
            self,
            "vetoes",
            tuple(self.vetoes),
        )

        object.__setattr__(
            self,
            "weighted_yes",
            float(self.weighted_yes),
        )

        object.__setattr__(
            self,
            "weighted_no",
            float(self.weighted_no),
        )

        object.__setattr__(
            self,
            "accepted",
            bool(self.accepted),
        )


@dataclass(slots=True, frozen=True)
class CatGroupRecruitmentFailedResult:
    group_id: str
    candidate: str
    vote: CatGroupRecruitmentVoteEvent

    name: str = field(
        default="cat_group_recruitment_failed",
        init=False,
    )

    joined: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.vote,
            CatGroupRecruitmentVoteEvent,
        ):
            raise TypeError(
                "Cat group recruitment failure "
                "must contain "
                "CatGroupRecruitmentVoteEvent."
            )


@dataclass(slots=True, frozen=True)
class CatGroupRecruitmentCompletedResult:
    group_id: str
    candidate: str
    vote: CatGroupRecruitmentVoteEvent
    join_result: object
    joined: bool

    name: str = field(
        default="cat_group_recruitment_completed",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.vote,
            CatGroupRecruitmentVoteEvent,
        ):
            raise TypeError(
                "Cat group recruitment result "
                "must contain "
                "CatGroupRecruitmentVoteEvent."
            )

        object.__setattr__(
            self,
            "joined",
            bool(self.joined),
        )
