from .possibility import Possibility
from .potential import Potential


class PotentialBlueprint:

    def __init__(
        self,
        name,
        probability,
        action,
        mandatory,
        available,
        source=None,
        context=None
    ):
        self.name = name
        self.probability = probability
        self.action = action
        self.mandatory = mandatory
        self.available = available
        self.source = source
        self.context = dict(
            context or {}
        )

    @classmethod
    def from_potential(
        cls,
        potential
    ):
        possibility = potential.possibility

        return cls(
            name=possibility.name,
            probability=possibility.probability,
            action=possibility.action,
            mandatory=possibility.mandatory,
            available=potential.is_available,
            source=potential.source,
            context=potential.context
        )

    def create_potential(
        self,
        cycle_id
    ):
        possibility = Possibility(
            name=self.name,
            probability=self.probability,
            action=self.action,
            condition=lambda: self.available,
            mandatory=self.mandatory
        )

        return Potential(
            possibility=possibility,
            cycle_id=cycle_id,
            source=self.source,
            context=dict(
                self.context
            )
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "probability": self.probability,
            "mandatory": self.mandatory,
            "available": self.available,
            "source": self.source,
            "context": dict(
                self.context
            )
        }
