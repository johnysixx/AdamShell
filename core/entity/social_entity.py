class EntityObject:

    def __init__(
        self,
        **state
    ):
        for key, value in state.items():
            setattr(
                self,
                key,
                value
            )

    @classmethod
    def from_mapping(
        cls,
        mapping
    ):
        if isinstance(
            mapping,
            cls
        ):
            return mapping

        if not isinstance(
            mapping,
            dict
        ):
            raise TypeError(
                "EntityObject.from_mapping "
                "requires dict input."
            )

        return cls(
            **mapping
        )

    # --------------------------------------------------------
    # Temporary mapping compatibility.
    #
    # Entity is NOT a dict.
    # Old code can still use entity["name"] while migration
    # to entity.name is completed.
    # --------------------------------------------------------

    def __getitem__(
        self,
        key
    ):
        return getattr(
            self,
            key
        )

    def __setitem__(
        self,
        key,
        value
    ):
        setattr(
            self,
            key,
            value
        )

    def __delitem__(
        self,
        key
    ):
        delattr(
            self,
            key
        )

    def __contains__(
        self,
        key
    ):
        return hasattr(
            self,
            key
        )

    def get(
        self,
        key,
        default=None
    ):
        return getattr(
            self,
            key,
            default
        )

    def setdefault(
        self,
        key,
        default=None
    ):
        if not hasattr(
            self,
            key
        ):
            setattr(
                self,
                key,
                default
            )

        return getattr(
            self,
            key
        )

    def update(
        self,
        *args,
        **kwargs
    ):
        state = {}

        for arg in args:
            if isinstance(
                arg,
                EntityObject
            ):
                state.update(
                    arg.to_dict()
                )
            else:
                state.update(
                    dict(
                        arg
                    )
                )

        state.update(
            kwargs
        )

        for key, value in state.items():
            setattr(
                self,
                key,
                value
            )

    def keys(
        self
    ):
        return self.__dict__.keys()

    def values(
        self
    ):
        return self.__dict__.values()

    def items(
        self
    ):
        return self.__dict__.items()

    def __iter__(
        self
    ):
        return iter(
            self.__dict__
        )

    def __len__(
        self
    ):
        return len(
            self.__dict__
        )

    def copy(
        self
    ):
        return dict(
            self.__dict__
        )

    def to_dict(
        self
    ):
        return dict(
            self.__dict__
        )

    def __repr__(
        self
    ):
        name = getattr(
            self,
            "name",
            None
        )

        entity_type = getattr(
            self,
            "type",
            self.__class__.__name__
        )

        return (
            f"<{self.__class__.__name__} "
            f"name={name!r} "
            f"type={entity_type!r}>"
        )


class SocialMixin:

    def pet_cat(
        self,
        cat,
        affinity_gain=0.10
    ):
        if isinstance(
            cat,
            dict
        ):
            raise TypeError(
                "Cat must be an object entity."
            )

        if getattr(
            cat,
            "type",
            None
        ) != "cat":
            raise TypeError(
                "Target must be a cat object."
            )

        actor_name = getattr(
            self,
            "name",
            None
        )

        cat_name = getattr(
            cat,
            "name",
            None
        )

        if actor_name is None:
            raise ValueError(
                "Petting actor has no name."
            )

        if cat_name is None:
            raise ValueError(
                "Cat has no name."
            )

        relationships = getattr(
            cat,
            "social_relationships",
            None
        )

        if relationships is None:
            relationships = {}

            cat.social_relationships = (
                relationships
            )

        relation = relationships.setdefault(
            actor_name,
            {
                "affinity": 0.0,
                "pet_count": 0,
                "last_interaction": None
            }
        )

        affinity_before = float(
            relation.get(
                "affinity",
                0.0
            )
        )

        relation[
            "pet_count"
        ] = int(
            relation.get(
                "pet_count",
                0
            )
        ) + 1

        relation[
            "affinity"
        ] = min(
            1.0,
            affinity_before
            + float(
                affinity_gain
            )
        )

        relation[
            "last_interaction"
        ] = "pet"

        # Petting immediately influences the cat's
        # next social decision.
        cat.next_social_target = (
            actor_name
        )

        cat.social_attention_bias = (
            relation[
                "affinity"
            ]
        )

        cat.last_social_interaction = {
            "type": "pet",
            "actor": actor_name
        }

        return {
            "name": "cat_petted",
            "cat": cat_name,
            "actor": actor_name,
            "pet_count": relation[
                "pet_count"
            ],
            "affinity_before": (
                affinity_before
            ),
            "affinity_after": relation[
                "affinity"
            ],
            "next_social_target": (
                cat.next_social_target
            )
        }


    def receive_pet(
        self,
        actor,
        affinity_gain=0.10
    ):
        actor_name = getattr(
            actor,
            "name",
            None
        )

        if actor_name is None:
            raise ValueError(
                "Petting actor has no name."
            )

        relationships = getattr(
            self,
            "social_relationships",
            None
        )

        if relationships is None:
            relationships = {}
            self.social_relationships = (
                relationships
            )

        relation = relationships.setdefault(
            actor_name,
            {
                "affinity": 0.0,
                "pet_count": 0,
                "last_interaction": None
            }
        )

        affinity_before = float(
            relation.get(
                "affinity",
                0.0
            )
        )

        relation[
            "pet_count"
        ] = int(
            relation.get(
                "pet_count",
                0
            )
        ) + 1

        relation[
            "affinity"
        ] = min(
            1.0,
            affinity_before
            + float(
                affinity_gain
            )
        )

        relation[
            "last_interaction"
        ] = "pet"

        # Immediate behavioural bias for the next decision.
        self.next_social_target = (
            actor_name
        )

        self.social_attention_bias = (
            relation[
                "affinity"
            ]
        )

        self.last_social_interaction = {
            "type": "pet",
            "actor": actor_name
        }

        return {
            "name": "cat_petted",
            "cat": getattr(
                self,
                "name",
                None
            ),
            "actor": actor_name,
            "pet_count": relation[
                "pet_count"
            ],
            "affinity_before": (
                affinity_before
            ),
            "affinity_after": relation[
                "affinity"
            ],
            "next_social_target": (
                self.next_social_target
            )
        }

    def affinity_toward(
        self,
        actor
    ):
        actor_name = (
            actor
            if isinstance(
                actor,
                str
            )
            else getattr(
                actor,
                "name",
                None
            )
        )

        relationships = getattr(
            self,
            "social_relationships",
            {}
        )

        return float(
            relationships.get(
                actor_name,
                {}
            ).get(
                "affinity",
                0.0
            )
        )


class SocialEntity(
    SocialMixin,
    EntityObject
):
    pass
