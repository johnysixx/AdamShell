from dataclasses import dataclass
from copy import deepcopy
from core.entity.domain_object import DomainObject


class CatMeowInvitation(DomainObject):
    pass


class CatGuestIncident(DomainObject):
    pass



class GarfieldTraining(DomainObject):
    pass


class CatLegend(DomainObject):
    pass



class CatTerritoryClaim(DomainObject):

    def __init__(
        self,
        owner,
        layer,
        location=None,
        **values
    ):
        owner = str(
            owner
        )

        layer = str(
            layer
        )

        if not owner:
            raise ValueError(
                "Cat territory claim requires owner."
            )

        if not layer:
            raise ValueError(
                "Cat territory claim requires layer."
            )

        super().__init__(
            owner=owner,
            layer=layer,
            location=location,
            **values
        )


class CatSocialMemory(DomainObject):

    def __init__(
        self,
        other_cat,
        **values
    ):
        other_cat = str(
            other_cat
        )

        if not other_cat:
            raise ValueError(
                "Cat social memory requires other_cat."
            )

        super().__init__(
            other_cat=other_cat,
            **values
        )


class CatBond(DomainObject):

    def __init__(
        self,
        other_cat,
        **values
    ):
        other_cat = str(
            other_cat
        )

        if not other_cat:
            raise ValueError(
                "Cat bond requires other_cat."
            )

        super().__init__(
            other_cat=other_cat,
            **values
        )


@dataclass(slots=True, frozen=True)
class CatRelationshipTrustEvent:
    reason: str
    previous: float | None = None
    current: float | None = None
    delta: float | None = None
    legend_id: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

        for field_name in (
            "previous",
            "current",
            "delta",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    float(value),
                )

def cat_relationship_trust_event_snapshot(
    event,
):
    if not isinstance(
        event,
        CatRelationshipTrustEvent,
    ):
        raise TypeError(
            "Relationship trust event snapshot "
            "requires CatRelationshipTrustEvent."
        )

    return {
        "previous": event.previous,
        "current": event.current,
        "delta": event.delta,
        "reason": event.reason,
        "legend_id": event.legend_id,
    }


class CatRelationship(DomainObject):

    @property
    def trust_history(self):
        return self._trust_history

    @trust_history.setter
    def trust_history(self, value):
        if value is None:
            value = []

        if not isinstance(value, list):
            raise TypeError(
                "Cat relationship trust history "
                "must be a list."
            )

        for event in value:
            if not isinstance(
                event,
                CatRelationshipTrustEvent,
            ):
                raise TypeError(
                    "Cat relationship trust history "
                    "must contain "
                    "CatRelationshipTrustEvent objects."
                )

        self._trust_history = value

    def __init__(
        self,
        other_cat=None,
        familiarity=0.0,
        trust=0.5,
        affiliation=0.0,
        tension=0.0,
        shared_scent=0.0,
        meet_count=0,
        last_interaction=None,
        trust_history=None,
    ):
        if other_cat is not None:
            other_cat = str(
                other_cat
            )

            if not other_cat:
                raise ValueError(
                    "Cat relationship requires "
                    "non-empty other_cat."
                )

        super().__init__(
            other_cat=other_cat,
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
    def create(
        cls,
        other_cat=None,
    ):
        return cls(
            other_cat=other_cat
        )


def cat_relationship_snapshot(
    relationship,
):
    if not isinstance(
        relationship,
        CatRelationship,
    ):
        raise TypeError(
            "Relationship snapshot requires "
            "CatRelationship."
        )

    snapshot = deepcopy(
        vars(
            relationship
        )
    )

    snapshot.pop(
        "_trust_history",
        None,
    )

    snapshot["trust_history"] = [
        cat_relationship_trust_event_snapshot(
            event
        )
        for event
        in relationship.trust_history
    ]

    return snapshot


@dataclass(slots=True, frozen=True)
class CatGroupKnowledgeTransmission:
    type: str
    source: str | None = None
    group: str | None = None
    source_group: str | None = None
    target_group: str | None = None

def cat_group_knowledge_transmission_snapshot(
    transmission,
):
    if not isinstance(
        transmission,
        CatGroupKnowledgeTransmission,
    ):
        raise TypeError(
            "Knowledge transmission snapshot requires "
            "CatGroupKnowledgeTransmission."
        )

    snapshot = {
        "type": transmission.type,
    }

    for field_name in (
        "source",
        "group",
        "source_group",
        "target_group",
    ):
        value = getattr(
            transmission,
            field_name,
        )

        if value is not None:
            snapshot[field_name] = value

    return snapshot


class CatGroupKnowledgeRecord(DomainObject):

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

def cat_group_knowledge_record_snapshot(
    record,
):
    if not isinstance(
        record,
        CatGroupKnowledgeRecord,
    ):
        raise TypeError(
            "Knowledge record snapshot requires "
            "CatGroupKnowledgeRecord."
        )

    snapshot = deepcopy(
        vars(
            record
        )
    )

    snapshot["transmission_path"] = [
        cat_group_knowledge_transmission_snapshot(
            transmission
        )
        for transmission
        in record.transmission_path
    ]

    return snapshot
