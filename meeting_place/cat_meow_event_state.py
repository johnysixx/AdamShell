from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class BouncerCatInvitedGuestAuthorizedEvent:
    human: str
    inviting_cat: str
    invitation_id: str

    name: str = field(
        default=(
            "bouncer_allows_"
            "cat_invited_guest"
        ),
        init=False,
    )

    authorized: bool = field(
        default=True,
        init=False,
    )

    guest_type: str = field(
        default="cat_invited_guest",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "human",
            str(self.human),
        )

        object.__setattr__(
            self,
            "inviting_cat",
            str(self.inviting_cat),
        )

        object.__setattr__(
            self,
            "invitation_id",
            str(self.invitation_id),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "authorized":
                self.authorized,
            "human": self.human,
            "inviting_cat":
                self.inviting_cat,
            "invitation_id":
                self.invitation_id,
            "guest_type":
                self.guest_type,
        }


@dataclass(slots=True, frozen=True)
class BouncerCatMeowEvent:
    cat: str
    recognized: bool

    name: str = field(
        default="cat_meowed_at_bouncer",
        init=False,
    )

    sound: str = field(
        default="MEOW",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "recognized",
            bool(self.recognized),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "sound": self.sound,
            "recognized": self.recognized,
        }


@dataclass(slots=True, frozen=True)
class BouncerCatMeowRecognitionEvent:
    cat: str
    recognized: bool

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "recognized",
            bool(self.recognized),
        )

    @property
    def name(self):
        if self.recognized:
            return (
                "bouncer_recognized_cat_meow"
            )

        return (
            "bouncer_heard_unrecognized_meow"
        )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "recognized": self.recognized,
        }


@dataclass(slots=True, frozen=True)
class BouncerCatAllowedEvent:
    cat: str
    meow_recognized: bool

    name: str = field(
        default="bouncer_allowed_cat",
        init=False,
    )

    allowed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "meow_recognized",
            bool(self.meow_recognized),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "meow_recognized":
                self.meow_recognized,
            "allowed": self.allowed,
        }


@dataclass(slots=True, frozen=True)
class BartenderCatMeowEvent:
    cat: str
    understood: bool

    name: str = field(
        default="cat_meowed_at_bartender",
        init=False,
    )

    sound: str = field(
        default="MEOW",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "understood",
            bool(self.understood),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "sound": self.sound,
            "understood": self.understood,
        }


@dataclass(slots=True, frozen=True)
class BartenderMeowReplyEvent:
    bartender: str
    cat: str

    name: str = field(
        default="bartender_replied_meow",
        init=False,
    )

    sound: str = field(
        default="MEOW",
        init=False,
    )

    reply: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "bartender",
            str(self.bartender),
        )

        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "bartender": self.bartender,
            "cat": self.cat,
            "sound": self.sound,
            "reply": self.reply,
        }


@dataclass(slots=True, frozen=True)
class BartenderCatMeowExchange:
    cat_meow: BartenderCatMeowEvent
    bartender_meow: BartenderMeowReplyEvent

    def __post_init__(self):
        if not isinstance(
            self.cat_meow,
            BartenderCatMeowEvent,
        ):
            raise TypeError(
                "Cat MEOW exchange requires "
                "BartenderCatMeowEvent."
            )

        if not isinstance(
            self.bartender_meow,
            BartenderMeowReplyEvent,
        ):
            raise TypeError(
                "Cat MEOW exchange requires "
                "BartenderMeowReplyEvent."
            )

    def to_dict(self):
        return {
            "cat_meow":
                self.cat_meow.to_dict(),
            "bartender_meow":
                self.bartender_meow.to_dict(),
        }
