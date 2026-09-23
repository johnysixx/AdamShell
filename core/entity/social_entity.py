from dataclasses import dataclass


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


@dataclass
class SocialRelationship:
    affinity: float = 0.0
    pet_count: int = 0
    last_interaction: str | None = None

    def record_pet(self, affinity_gain=0.1):
        affinity_before = float(self.affinity)
        self.pet_count = int(self.pet_count) + 1
        self.affinity = min(
            1.0,
            affinity_before + float(affinity_gain),
        )
        self.last_interaction = 'pet'
        return affinity_before

    def to_dict(self):
        return {
            'affinity': self.affinity,
            'pet_count': self.pet_count,
            'last_interaction': self.last_interaction,
        }


class EntityObject:

    def __init__(self, **state):
        for key, value in state.items():
            setattr(self, key, value)

    @classmethod
    def from_mapping(cls, mapping):
        if isinstance(mapping, cls):
            return mapping
        if not isinstance(mapping, dict):
            raise TypeError('EntityObject.from_mapping requires dict input.')
        return cls(**mapping)

    def to_dict(self):
        return dict(self.__dict__)

    def __repr__(self):
        name = getattr(self, 'name', None)
        entity_type = getattr(self, 'type', self.__class__.__name__)
        return f'<{self.__class__.__name__} name={name!r} type={entity_type!r}>'


class SocialMixin:

    @staticmethod
    def _relationship_for(entity, actor_name):
        relationships = getattr(entity, 'social_relationships', None)
        if relationships is None:
            relationships = {}
            entity.social_relationships = relationships

        relation = relationships.get(actor_name)
        if relation is None:
            relation = SocialRelationship()
            relationships[actor_name] = relation
        elif not isinstance(relation, SocialRelationship):
            raise TypeError(
                'social_relationships values must be '
                'SocialRelationship objects.'
            )
        return relation

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

        relation = self._relationship_for(cat, actor_name)
        affinity_before = relation.record_pet(affinity_gain)
        cat.next_social_target = actor_name
        cat.social_attention_bias = relation.affinity
        cat.last_social_interaction = (
            SocialInteractionRecord(
                interaction_type='pet',
                actor=actor_name,
            )
        )
        return {
            'name': 'cat_petted',
            'cat': cat_name,
            'actor': actor_name,
            'pet_count': relation.pet_count,
            'affinity_before': affinity_before,
            'affinity_after': relation.affinity,
            'next_social_target': cat.next_social_target,
        }

    def receive_pet(self, actor, affinity_gain=0.1):
        actor_name = getattr(actor, 'name', None)
        if actor_name is None:
            raise ValueError('Petting actor has no name.')

        relation = self._relationship_for(self, actor_name)
        affinity_before = relation.record_pet(affinity_gain)
        self.next_social_target = actor_name
        self.social_attention_bias = relation.affinity
        self.last_social_interaction = (
            SocialInteractionRecord(
                interaction_type='pet',
                actor=actor_name,
            )
        )
        return {
            'name': 'cat_petted',
            'cat': getattr(self, 'name', None),
            'actor': actor_name,
            'pet_count': relation.pet_count,
            'affinity_before': affinity_before,
            'affinity_after': relation.affinity,
            'next_social_target': self.next_social_target,
        }

    def affinity_toward(self, actor):
        actor_name = (
            actor
            if isinstance(actor, str)
            else getattr(actor, 'name', None)
        )
        relationships = getattr(self, 'social_relationships', {})
        relation = relationships.get(actor_name)
        if relation is None:
            return 0.0
        if not isinstance(relation, SocialRelationship):
            raise TypeError(
                'social_relationships values must be '
                'SocialRelationship objects.'
            )
        return float(relation.affinity)


class SocialEntity(SocialMixin, EntityObject):
    pass


def _entity_attr_setdefault(entity, name, default):
    if not hasattr(entity, name):
        setattr(entity, name, default)
    return getattr(entity, name)
