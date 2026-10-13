from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ArchetypePrincipleState:
    name: str
    domain: tuple[str, ...]
    origin: str

    def __post_init__(self):
        object.__setattr__(
            self,
            "name",
            str(
                self.name
            ),
        )

        object.__setattr__(
            self,
            "domain",
            tuple(
                str(value)
                for value
                in self.domain
            ),
        )

        object.__setattr__(
            self,
            "origin",
            str(
                self.origin
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "domain": list(
                self.domain
            ),
            "origin": self.origin,
        }


@dataclass(slots=True, frozen=True)
class IdeaEntityAccessProfile:
    meeting_place: bool = False
    library: str | None = None
    quantum_layer: str | bool | None = None
    eden: bool | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "meeting_place",
            bool(
                self.meeting_place
            ),
        )

        if self.library is not None:
            object.__setattr__(
                self,
                "library",
                str(
                    self.library
                ),
            )

        if (
            self.quantum_layer
            is not None
            and not isinstance(
                self.quantum_layer,
                bool,
            )
        ):
            object.__setattr__(
                self,
                "quantum_layer",
                str(
                    self.quantum_layer
                ),
            )

        if self.eden is not None:
            object.__setattr__(
                self,
                "eden",
                bool(
                    self.eden
                ),
            )

    def to_dict(self):
        result = {
            "meeting_place":
                self.meeting_place,
        }

        if self.library is not None:
            result[
                "library"
            ] = self.library

        if self.quantum_layer is not None:
            result[
                "quantum_layer"
            ] = self.quantum_layer

        if self.eden is not None:
            result[
                "eden"
            ] = self.eden

        return result
