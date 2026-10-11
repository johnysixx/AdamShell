from dataclasses import dataclass, field

from core.entity.components import (
    SpatialVector3,
    require_optional_spatial_vector,
    require_spatial_vector,
)


@dataclass(slots=True, frozen=True)
class CatManifestedEvent:
    cat_name: str
    source: str
    position: SpatialVector3 | None
    tick: int
    collapse_cause: str | None = None
    box_id: str | None = None
    observer: object = None
    name: str = field(default="cat_manifested", init=False)

    def __post_init__(self):
        object.__setattr__(self, "cat_name", str(self.cat_name))
        object.__setattr__(self, "source", str(self.source))
        object.__setattr__(
            self,
            "position",
            require_optional_spatial_vector(
                self.position,
                field_name="manifestation position",
            ),
        )
        object.__setattr__(self, "tick", int(self.tick))
        if self.collapse_cause is not None:
            object.__setattr__(
                self,
                "collapse_cause",
                str(self.collapse_cause),
            )
        if self.box_id is not None:
            object.__setattr__(self, "box_id", str(self.box_id))

    def to_dict(self):
        snapshot = {
            "name": self.name,
            "cat": self.cat_name,
            "source": self.source,
            "position": (
                None
                if self.position is None
                else self.position.to_dict()
            ),
            "tick": self.tick,
        }
        if self.collapse_cause is not None or self.box_id is not None:
            snapshot.update({
                "collapse_cause": self.collapse_cause,
                "box_id": self.box_id,
                "observer": self.observer,
            })
        return snapshot


@dataclass(slots=True, frozen=True)
class CatManifestationResult:
    cat: object
    entity: object
    event: CatManifestedEvent

    def __post_init__(self):
        if not isinstance(self.event, CatManifestedEvent):
            raise TypeError(
                "Cat manifestation result requires a CatManifestedEvent object."
            )


@dataclass(slots=True, frozen=True)
class EmptyQuantumBoxOpenedEvent:
    box_id: str
    position: SpatialVector3
    observer: object
    tick: int
    collapse_cause: str = field(default="opened", init=False)
    name: str = field(default="empty_quantum_box_opened", init=False)

    def __post_init__(self):
        object.__setattr__(self, "box_id", str(self.box_id))
        object.__setattr__(
            self,
            "position",
            require_spatial_vector(
                self.position,
                field_name="empty quantum box position",
            ),
        )
        object.__setattr__(self, "tick", int(self.tick))

    def to_dict(self):
        return {
            "name": self.name,
            "collapse_cause": self.collapse_cause,
            "box_id": self.box_id,
            "position": self.position.to_dict(),
            "observer": self.observer,
            "tick": self.tick,
        }
