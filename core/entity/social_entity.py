from copy import deepcopy
from dataclasses import dataclass, field

from core.entity.world_existence_state import (
    WorldExistenceState,
)


@dataclass(slots=True, frozen=True)
class SocialInteractionRecord:
    interaction_type: str
    actor: str

    def __post_init__(self):
        object.__setattr__(
            self,
            "interaction_type",
            str(self.interaction_type),
        )
        object.__setattr__(
            self,
            "actor",
            str(self.actor),
        )

    def to_dict(self):
        return {
            "type": self.interaction_type,
            "actor": self.actor,
        }




@dataclass(slots=True, frozen=True)
class CatPettedEvent:
    cat: str
    actor: str
    pet_count: int
    affinity_before: float
    affinity_after: float
    next_social_target: str
    name: str = field(
        default="cat_petted",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(self, "cat", str(self.cat))
        object.__setattr__(self, "actor", str(self.actor))
        object.__setattr__(self, "pet_count", int(self.pet_count))
        object.__setattr__(self, "affinity_before", float(self.affinity_before))
        object.__setattr__(self, "affinity_after", float(self.affinity_after))
        object.__setattr__(self, "next_social_target", str(self.next_social_target))

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "actor": self.actor,
            "pet_count": self.pet_count,
            "affinity_before": self.affinity_before,
            "affinity_after": self.affinity_after,
            "next_social_target": self.next_social_target,
        }


@dataclass(slots=True, frozen=True)
class SocialRelationship:
    affinity: float = 0.0
    pet_count: int = 0
    last_interaction: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self, "affinity", float(self.affinity)
        )
        object.__setattr__(
            self, "pet_count", int(self.pet_count)
        )

    def after_pet(self, affinity_gain=0.1):
        return SocialRelationship(
            affinity=min(
                1.0,
                self.affinity + float(affinity_gain),
            ),
            pet_count=self.pet_count + 1,
            last_interaction="pet",
        )

    def to_dict(self):
        return {
            "affinity": self.affinity,
            "pet_count": self.pet_count,
            "last_interaction": self.last_interaction,
        }


@dataclass(slots=True, frozen=True)
class SocialRelationshipEntry:
    actor: str
    relationship: SocialRelationship

    def __post_init__(self):
        if not isinstance(self.actor, str) or not self.actor:
            raise TypeError(
                "Social relationship actor must be a string."
            )

        if not isinstance(
            self.relationship, SocialRelationship
        ):
            raise TypeError(
                "Relationship must be SocialRelationship."
            )


@dataclass(slots=True, frozen=True)
class SocialRelationshipRegistry:
    entries: tuple[SocialRelationshipEntry, ...] = ()

    def __post_init__(self):
        if not isinstance(self.entries, tuple):
            raise TypeError(
                "Social relationship entries must be a tuple."
            )

        if not all(
            isinstance(entry, SocialRelationshipEntry)
            for entry in self.entries
        ):
            raise TypeError(
                "Registry requires typed entries."
            )

        actors = tuple(
            entry.actor for entry in self.entries
        )

        if len(actors) != len(set(actors)):
            raise ValueError(
                "Duplicate social relationship actor."
            )

    def relationship_for(self, actor):
        for entry in self.entries:
            if entry.actor == actor:
                return entry.relationship

        return None

    def with_relationship(self, actor, relationship):
        updated = SocialRelationshipEntry(
            actor=actor,
            relationship=relationship,
        )

        if self.relationship_for(actor) is not None:
            entries = tuple(
                updated if entry.actor == actor else entry
                for entry in self.entries
            )
        else:
            entries = self.entries + (updated,)

        return SocialRelationshipRegistry(entries=entries)

    @classmethod
    def from_mapping(cls, mapping):
        if not isinstance(mapping, dict):
            raise TypeError(
                "Social relationship boundary requires dict."
            )

        entries = []

        for actor, value in mapping.items():
            if not isinstance(value, dict):
                raise TypeError(
                    "Relationship boundary requires dict values."
                )

            entries.append(
                SocialRelationshipEntry(
                    actor=actor,
                    relationship=SocialRelationship(
                        affinity=value.get("affinity", 0.0),
                        pet_count=value.get("pet_count", 0),
                        last_interaction=value.get(
                            "last_interaction"
                        ),
                    ),
                )
            )

        return cls(entries=tuple(entries))

    def to_dict(self):
        return {
            entry.actor: entry.relationship.to_dict()
            for entry in self.entries
        }


class EntityObject:

    def __setattr__(self, name, value):
        if (
            name == "existence_by_world"
            and not isinstance(value, WorldExistenceState)
        ):
            raise TypeError(
                "existence_by_world requires "
                "WorldExistenceState."
            )

        if (
            name == "social_relationships"
            and not isinstance(
                value, SocialRelationshipRegistry
            )
        ):
            raise TypeError(
                "social_relationships requires "
                "SocialRelationshipRegistry."
            )

        super().__setattr__(name, value)

    def __init__(self, **state):
        for key, value in state.items():
            setattr(self, key, value)

    @classmethod
    def from_mapping(cls, mapping):
        if isinstance(mapping, cls):
            return mapping
        if not isinstance(mapping, dict):
            raise TypeError('EntityObject.from_mapping requires dict input.')
        values = dict(mapping)

        if isinstance(
            values.get("existence_by_world"),
            dict,
        ):
            values["existence_by_world"] = (
                WorldExistenceState.from_mapping(
                    values["existence_by_world"]
                )
            )

        if isinstance(
            values.get("social_relationships"), dict
        ):
            values["social_relationships"] = (
                SocialRelationshipRegistry.from_mapping(
                    values["social_relationships"]
                )
            )

        return cls(**values)

    def to_dict(self):
        snapshot = dict(self.__dict__)

        if "metadata" in snapshot:
            snapshot["metadata"] = deepcopy(
                snapshot["metadata"]
            )

        if isinstance(
            snapshot.get("existence_by_world"),
            WorldExistenceState,
        ):
            snapshot["existence_by_world"] = (
                snapshot["existence_by_world"].to_dict()
            )

        if isinstance(
            snapshot.get("social_relationships"),
            SocialRelationshipRegistry,
        ):
            snapshot["social_relationships"] = (
                snapshot["social_relationships"].to_dict()
            )

        return snapshot

    def __repr__(self):
        name = getattr(self, 'name', None)
        entity_type = getattr(self, 'type', self.__class__.__name__)
        return f'<{self.__class__.__name__} name={name!r} type={entity_type!r}>'


class SocialMixin:

    def __setattr__(self, name, value):
        if (
            name == "social_relationships"
            and not isinstance(
                value, SocialRelationshipRegistry
            )
        ):
            raise TypeError(
                "social_relationships requires "
                "SocialRelationshipRegistry."
            )

        super().__setattr__(name, value)

    @staticmethod
    def _record_pet_relationship(
        entity, actor_name, affinity_gain
    ):
        registry = getattr(
            entity, "social_relationships", None
        )

        if registry is None:
            registry = SocialRelationshipRegistry()

        if not isinstance(
            registry, SocialRelationshipRegistry
        ):
            raise TypeError(
                "Social relationships require typed registry."
            )

        previous = registry.relationship_for(actor_name)

        if previous is None:
            previous = SocialRelationship()

        before = previous.affinity
        updated = previous.after_pet(affinity_gain)

        entity.social_relationships = (
            registry.with_relationship(
                actor_name, updated
            )
        )

        return before, updated

    def pet_cat(self, cat, affinity_gain=0.1):
        if isinstance(cat, dict):
            raise TypeError('Cat must be an object entity.')
        if getattr(cat, 'type', None) != 'cat':
            raise TypeError('Target must be a cat object.')
        actor_name = getattr(self, 'name', None)
        cat_name = getattr(cat, 'name', None)
        if actor_name is None:
            raise ValueError('Petting actor has no name.')
        if cat_name is None:
            raise ValueError('Cat has no name.')

        affinity_before, relation = (
            self._record_pet_relationship(
                cat, actor_name, affinity_gain
            )
        )
        cat.next_social_target = actor_name
        cat.social_attention_bias = relation.affinity
        cat.last_social_interaction = (
            SocialInteractionRecord(
                interaction_type='pet',
                actor=actor_name,
            )
        )
        return CatPettedEvent(
            cat=cat_name,
            actor=actor_name,
            pet_count=relation.pet_count,
            affinity_before=affinity_before,
            affinity_after=relation.affinity,
            next_social_target=cat.next_social_target,
        )

    def receive_pet(self, actor, affinity_gain=0.1):
        actor_name = getattr(actor, 'name', None)
        if actor_name is None:
            raise ValueError('Petting actor has no name.')

        affinity_before, relation = (
            self._record_pet_relationship(
                self, actor_name, affinity_gain
            )
        )
        self.next_social_target = actor_name
        self.social_attention_bias = relation.affinity
        self.last_social_interaction = (
            SocialInteractionRecord(
                interaction_type='pet',
                actor=actor_name,
            )
        )
        return CatPettedEvent(
            cat=getattr(self, 'name', None),
            actor=actor_name,
            pet_count=relation.pet_count,
            affinity_before=affinity_before,
            affinity_after=relation.affinity,
            next_social_target=self.next_social_target,
        )

    def affinity_toward(self, actor):
        actor_name = (
            actor
            if isinstance(actor, str)
            else getattr(actor, 'name', None)
        )
        registry = getattr(
            self, "social_relationships", None
        )

        if registry is None:
            return 0.0

        if not isinstance(
            registry, SocialRelationshipRegistry
        ):
            raise TypeError(
                "Social relationships require typed registry."
            )

        relation = registry.relationship_for(actor_name)

        if relation is None:
            return 0.0

        return relation.affinity


class SocialEntity(SocialMixin, EntityObject):
    pass


def _entity_attr_setdefault(entity, name, default):
    if not hasattr(entity, name):
        setattr(entity, name, default)
    return getattr(entity, name)
