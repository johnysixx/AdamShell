from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatMatingContact:

    contact_number: int
    female: str
    male: str
    successful: bool
    day: int

    male_ref: object = field(
        repr=False,
        compare=False,
    )

    name: str = field(
        default="cat_mating_contact",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "contact_number",
            int(
                self.contact_number
            ),
        )

        object.__setattr__(
            self,
            "female",
            str(
                self.female
            ),
        )

        object.__setattr__(
            self,
            "male",
            str(
                self.male
            ),
        )

        object.__setattr__(
            self,
            "successful",
            bool(
                self.successful
            ),
        )

        object.__setattr__(
            self,
            "day",
            int(
                self.day
            ),
        )

    @property
    def male_name(self):
        return self.male

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "contact_number": (
                self.contact_number
            ),
            "female": self.female,
            "male": self.male,
            "male_name": (
                self.male_name
            ),
            "successful": (
                self.successful
            ),
            "day": self.day,
            "_male_ref": (
                self.male_ref
            ),
        }


class CatMatingHistoryEvent:

    def __deepcopy__(
        self,
        memo
    ):
        return self


@dataclass(slots=True, frozen=True)
class CatMatingContactRecordedEvent(
    CatMatingHistoryEvent
):

    contact: CatMatingContact

    potential_fathers: tuple[
        str,
        ...,
    ]

    ovulation_stimulation: int
    ovulation_threshold: int
    ovulation_threshold_reached: bool

    name: str = field(
        default=(
            "cat_mating_contact_recorded"
        ),
        init=False,
    )

    mating_window_open: bool = field(
        default=True,
        init=False,
    )

    pregnancy_started: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.contact,
            CatMatingContact,
        ):
            raise TypeError(
                "Mating contact event "
                "requires a "
                "CatMatingContact object."
            )

        object.__setattr__(
            self,
            "potential_fathers",
            tuple(
                self.potential_fathers
            ),
        )

        object.__setattr__(
            self,
            "ovulation_stimulation",
            int(
                self.ovulation_stimulation
            ),
        )

        object.__setattr__(
            self,
            "ovulation_threshold",
            int(
                self.ovulation_threshold
            ),
        )

        object.__setattr__(
            self,
            "ovulation_threshold_reached",
            bool(
                self.ovulation_threshold_reached
            ),
        )

    @property
    def female(self):
        return self.contact.female

    @property
    def male(self):
        return self.contact.male

    @property
    def day(self):
        return self.contact.day

    @property
    def contact_number(self):
        return (
            self.contact
            .contact_number
        )

    def to_dict(self):
        return {
            "name": self.name,
            "female": self.female,
            "male": self.male,
            "day": self.day,
            "contact_number": (
                self.contact_number
            ),
            "mating_window_open": (
                self.mating_window_open
            ),
            "potential_fathers": list(
                self.potential_fathers
            ),
            "pregnancy_started": (
                self.pregnancy_started
            ),
            "ovulation_stimulation": (
                self.ovulation_stimulation
            ),
            "ovulation_threshold": (
                self.ovulation_threshold
            ),
            "ovulation_threshold_reached": (
                self.ovulation_threshold_reached
            ),
        }
