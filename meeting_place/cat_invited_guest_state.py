from dataclasses import dataclass, field


@dataclass(slots=True)
class CatInvitedGuestState:
    human: str
    inviting_cat: str
    invitation_id: str
    cat_present: bool = True
    entered_together: bool = True
    permanent_access: bool = False


@dataclass(slots=True, frozen=True)
class CatInvitedHumanEntryDeniedResult:
    human: str | None
    cat: str | None
    reason: str

    name: str = field(
        default="cat_invited_human_entry_denied",
        init=False,
    )

    entered: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if self.human is not None:
            object.__setattr__(
                self,
                "human",
                str(self.human),
            )

        if self.cat is not None:
            object.__setattr__(
                self,
                "cat",
                str(self.cat),
            )

        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "human": self.human,
            "cat": self.cat,
            "reason": self.reason,
            "entered": self.entered,
        }


@dataclass(slots=True, frozen=True)
class CatInvitedGuestArrivedEvent:
    human: str
    inviting_cat: str
    invitation_id: str
    cat_present: bool
    entered_together: bool
    permanent_access: bool

    name: str = field(
        default="cat_invited_guest_arrived",
        init=False,
    )

    @classmethod
    def from_state(
        cls,
        state,
    ):
        if not isinstance(
            state,
            CatInvitedGuestState,
        ):
            raise TypeError(
                "Invited guest arrival requires "
                "CatInvitedGuestState."
            )

        return cls(
            human=state.human,
            inviting_cat=state.inviting_cat,
            invitation_id=state.invitation_id,
            cat_present=state.cat_present,
            entered_together=(
                state.entered_together
            ),
            permanent_access=(
                state.permanent_access
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "human": self.human,
            "inviting_cat": self.inviting_cat,
            "invitation_id": self.invitation_id,
            "cat_present": self.cat_present,
            "entered_together":
                self.entered_together,
            "permanent_access":
                self.permanent_access,
        }


@dataclass(slots=True, frozen=True)
class CatInvitedHumanEnteredEvent:
    human: str
    inviting_cat: str
    invitation_id: str
    cat_present: bool
    entered_together: bool
    permanent_access: bool

    name: str = field(
        default="cat_invited_human_entered",
        init=False,
    )

    entered: bool = field(
        default=True,
        init=False,
    )

    @classmethod
    def from_state(
        cls,
        state,
    ):
        if not isinstance(
            state,
            CatInvitedGuestState,
        ):
            raise TypeError(
                "Invited human entry requires "
                "CatInvitedGuestState."
            )

        return cls(
            human=state.human,
            inviting_cat=state.inviting_cat,
            invitation_id=state.invitation_id,
            cat_present=state.cat_present,
            entered_together=(
                state.entered_together
            ),
            permanent_access=(
                state.permanent_access
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "human": self.human,
            "inviting_cat": self.inviting_cat,
            "invitation_id": self.invitation_id,
            "cat_present": self.cat_present,
            "entered_together":
                self.entered_together,
            "permanent_access":
                self.permanent_access,
            "entered": self.entered,
        }


@dataclass(slots=True, frozen=True)
class CatGuestIncidentNotAttributedResult:
    human: str | None
    category: str
    inviting_cat: str | None = None
    reason: str | None = None

    name: str = field(
        default="cat_guest_incident_not_attributed",
        init=False,
    )

    cat_responsibility: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if self.human is not None:
            object.__setattr__(
                self,
                "human",
                str(self.human),
            )

        object.__setattr__(
            self,
            "category",
            str(self.category),
        )

        if self.inviting_cat is not None:
            object.__setattr__(
                self,
                "inviting_cat",
                str(
                    self.inviting_cat
                ),
            )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(
                    self.reason
                ),
            )
