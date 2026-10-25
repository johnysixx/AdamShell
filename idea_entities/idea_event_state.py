from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class IdeaEntityEvent:
    name: str
    participants: tuple[str, ...]
    observer: str | None = None
    state: str = "unresolved"
    meaning: str | None = None
    place: str | None = None

    layer: str = field(
        default="idea_entities",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "name",
            str(self.name),
        )

        if isinstance(self.participants, str):
            raise TypeError(
                "Idea event participants must "
                "be a collection."
            )

        object.__setattr__(
            self,
            "participants",
            tuple(
                str(participant)
                for participant in self.participants
            ),
        )

        for field_name in (
            "observer",
            "meaning",
            "place",
        ):
            value = getattr(self, field_name)

            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    str(value),
                )

        object.__setattr__(
            self,
            "state",
            str(self.state),
        )

    @property
    def known_by(self):
        if self.observer is None:
            return ()

        return (self.observer,)

    def __deepcopy__(self, memo):
        return self

    def to_dict(self):
        snapshot = {
            "name": self.name,
            "layer": self.layer,
        }

        if self.place is not None:
            snapshot["place"] = self.place

        snapshot.update({
            "participants": list(self.participants),
            "observer": self.observer,
            "state": self.state,
            "meaning": self.meaning,
            "known_by": list(self.known_by),
        })

        return snapshot
