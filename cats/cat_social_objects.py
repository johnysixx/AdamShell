from dataclasses import dataclass
from copy import deepcopy
from core.entity.component_object import ComponentObject


class CatMeowInvitation(ComponentObject):
    pass


class CatGuestIncident(ComponentObject):
    pass



class GarfieldTraining(ComponentObject):
    pass


class CatLegend(ComponentObject):
    pass



class CatTerritoryClaim(ComponentObject):
    pass


class CatSocialMemory(ComponentObject):
    pass


class CatBond(ComponentObject):
    pass


class CatRelationship(ComponentObject):

    def __init__(
        self,
        familiarity=0.0,
        trust=0.5,
        affiliation=0.0,
        tension=0.0,
        shared_scent=0.0,
        meet_count=0,
        last_interaction=None,
        trust_history=None,
    ):
        super().__init__(
            familiarity=familiarity,
            trust=trust,
            affiliation=affiliation,
            tension=tension,
            shared_scent=shared_scent,
            meet_count=meet_count,
            last_interaction=last_interaction,
            trust_history=(
                []
                if trust_history is None
                else trust_history
            ),
        )

    @classmethod
    def create(cls):
        return cls()


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeTransmission:
    type: str
    source: str | None = None
    group: str | None = None
    source_group: str | None = None
    target_group: str | None = None

    def to_dict(self):
        snapshot = {
            "type": self.type,
        }

        for field_name in (
            "source",
            "group",
            "source_group",
            "target_group",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                snapshot[field_name] = value

        return snapshot


class CatGroupKnowledgeRecord(ComponentObject):

    def __init__(self, **values):
        transmission_path = list(
            values.get(
                "transmission_path",
                [],
            )
        )

        for transmission in transmission_path:
            if not isinstance(
                transmission,
                CatGroupKnowledgeTransmission,
            ):
                raise TypeError(
                    "Cat group knowledge transmission path "
                    "must contain "
                    "CatGroupKnowledgeTransmission objects."
                )

        values["transmission_path"] = (
            transmission_path
        )

        super().__init__(
            **values
        )

    def to_dict(self):
        snapshot = deepcopy(
            super().to_dict()
        )

        snapshot["transmission_path"] = [
            transmission.to_dict()
            for transmission
            in self.transmission_path
        ]

        return snapshot
