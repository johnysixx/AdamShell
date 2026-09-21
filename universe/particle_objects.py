from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ElementaryParticle:
    name: str
    type: str
    family: str
    electric_charge: str
    role: str
    state: str
    origin: str

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "family": self.family,
            "electric_charge": self.electric_charge,
            "role": self.role,
            "state": self.state,
            "origin": self.origin,
        }


@dataclass(frozen=True, slots=True)
class CompositeParticle:
    name: str
    type: str
    family: str
    state: str
    composition: tuple[str, ...]
    electric_charge: str
    future_use: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(
            self,
            "composition",
            tuple(self.composition),
        )
        object.__setattr__(
            self,
            "future_use",
            tuple(self.future_use),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "family": self.family,
            "state": self.state,
            "composition": list(self.composition),
            "electric_charge": self.electric_charge,
            "future_use": list(self.future_use),
        }


@dataclass(frozen=True, slots=True)
class ParticleField:
    name: str
    type: str
    state: str
    role: str
    related_particle: str | None = None
    note: str | None = None

    def to_dict(self):
        result = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "role": self.role,
        }

        if self.related_particle is not None:
            result["related_particle"] = self.related_particle

        if self.note is not None:
            result["note"] = self.note

        return result


@dataclass(frozen=True, slots=True)
class ParticleInteraction:
    name: str
    mediator: str | None = None
    mediators: tuple[str, ...] = ()
    acts_on: tuple[str, ...] = ()
    effect: str | None = None
    field: str | None = None
    particle: str | None = None
    example: str | None = None
    interaction: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "mediators",
            tuple(self.mediators),
        )
        object.__setattr__(
            self,
            "acts_on",
            tuple(self.acts_on),
        )

    def to_dict(self):
        result = {
            "name": self.name,
        }

        if self.mediator is not None:
            result["mediator"] = self.mediator

        if self.mediators:
            result["mediators"] = list(self.mediators)

        if self.acts_on:
            result["acts_on"] = list(self.acts_on)

        if self.effect is not None:
            result["effect"] = self.effect

        if self.field is not None:
            result["field"] = self.field

        if self.particle is not None:
            result["particle"] = self.particle

        if self.example is not None:
            result["example"] = self.example

        if self.interaction is not None:
            result["interaction"] = self.interaction

        return result
