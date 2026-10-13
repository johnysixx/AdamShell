from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class GodBornEvent:
    name: str = field(
        default="god_born",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass(slots=True, frozen=True)
class GodEnteredLibraryEvent:
    door_sign: str

    name: str = field(
        default="god_entered_library",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "door_sign",
            str(
                self.door_sign
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass(slots=True, frozen=True)
class GodBeginsFirstUnnamedBookEvent:
    title: None = field(
        default=None,
        init=False,
    )
    state: str = field(
        default="being_written",
        init=False,
    )
    location: str = field(
        default="library_with_author",
        init=False,
    )

    name: str = field(
        default=(
            "god_begins_first_"
            "unnamed_book"
        ),
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass(slots=True, frozen=True)
class GodLibraryOpeningResult:
    god: object
    book: object
    born: GodBornEvent
    entered: GodEnteredLibraryEvent
    began_book: GodBeginsFirstUnnamedBookEvent

    def __post_init__(self):
        if not isinstance(
            self.born,
            GodBornEvent,
        ):
            raise TypeError(
                "God birth must be "
                "object state."
            )

        if not isinstance(
            self.entered,
            GodEnteredLibraryEvent,
        ):
            raise TypeError(
                "God library entry must be "
                "object state."
            )

        if not isinstance(
            self.began_book,
            GodBeginsFirstUnnamedBookEvent,
        ):
            raise TypeError(
                "God first book event must be "
                "object state."
            )


@dataclass(slots=True, frozen=True)
class GodLeftLibraryEvent:
    name: str = field(
        default="god_left_library",
        init=False,
    )
    source: str = field(
        default="library",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass(slots=True, frozen=True)
class GodEnteredBarEvent:
    name: str = field(
        default="god_entered_bar",
        init=False,
    )
    source: str = field(
        default="library",
        init=False,
    )
    destination: str = field(
        default="bar",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass(slots=True, frozen=True)
class GodLibraryDepartureResult:
    god: object
    book: object
    left: GodLeftLibraryEvent
    entered_bar: GodEnteredBarEvent

    def __post_init__(self):
        if not isinstance(
            self.left,
            GodLeftLibraryEvent,
        ):
            raise TypeError(
                "God library departure must "
                "be object state."
            )

        if not isinstance(
            self.entered_bar,
            GodEnteredBarEvent,
        ):
            raise TypeError(
                "God bar entry must be "
                "object state."
            )
