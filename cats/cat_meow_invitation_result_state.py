from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatMeowInvitationNotOfferedResult:
    cat: str
    human: str | None
    reason: str
    current_tick: int | None = None
    suspended_until_tick: int | None = None
    name: str = field(default="cat_MEOW_not_offered", init=False)
    offered: bool = field(default=False, init=False)


@dataclass(slots=True, frozen=True)
class CatMeowInterpretationFailedResult:
    reason: str
    name: str = field(default="cat_MEOW_interpretation_failed", init=False)
    understood: bool = field(default=False, init=False)


@dataclass(slots=True, frozen=True)
class CatMeowInterpretationResult:
    invitation_id: str
    human: str
    understood: bool
    meaning: str | None

    @property
    def name(self):
        return "human_understood_MEOW" if self.understood else "human_heard_only_meow"
