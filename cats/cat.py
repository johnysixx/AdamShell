class Cat:
    """
    A living cat entity.

    Cat owns its state and behavior.
    Mapping compatibility is temporary so the existing
    feline subsystem can migrate from dictionaries
    without a flag-day rewrite.
    """

    def __init__(
        self,
        name,
        color,
        pattern,
        eye_color,
        fur_length,
        sex,
        genotype,
        reproduction,
        origin,
        idea_energy,
        memory,
        access,
        learning,
        personality,
        mind,
        intellect,
        aroma
    ):
        self.name = name
        self.type = "cat"
        self.state = "created"

        self.color = color
        self.pattern = pattern
        self.eye_color = eye_color
        self.fur_length = fur_length
        self.sex = sex

        self.genotype = genotype
        self.reproduction = reproduction
        self.origin = origin

        self.idea_energy = idea_energy

        self.size = 1.0
        self.strength = 1.0

        self.cronenbergs_eaten = 0
        self.cronenberg_mass_eaten = 0.0

        self.memory = memory
        self.access = access
        self.learning = learning
        self.personality = personality
        self.mind = mind
        self.intellect = intellect

        # Persistent feline knowledge
        self.knowledge = {}

        # Persistent social relationships
        self.relationships = {}

        # Persistent memory of cat-to-cat encounters
        self.social_memory = {}

        # Persistent territorial claims
        self.territories = {}

        # Persistent close feline bonds
        self.bonds = {}

        # Persistent genealogy
        self.family = {
            "parents": {
                "mother": None,
                "father": None
            },
            "children": [],
            "siblings": [],
            "littermates": [],
            "half_siblings": []
        }

        # Persistent maternal state
        self.maternal_care = {
            "active": False,
            "kittens": {},
            "care_events": 0
        }

        self.maternal_care_received = {
            "mother": None,
            "care_events": 0,
            "nursing_events": 0,
            "cleaning_events": 0,
            "warming_events": 0,
            "protection_events": 0,
            "retrieval_events": 0,
            "last_care_day": None,
            "last_phase": None
        }

        # Persistent sibling play history
        self.sibling_play = {
            "play_events": 0,
            "partners": {},
            "last_partner": None,
            "last_play_day": None
        }

        # Persistent sibling rivalry
        self.sibling_rivalry = {
            "events": 0,
            "rivals": {},
            "last_rival": None,
            "last_resource": None
        }

        # Persistent parental teaching history
        self.parental_teaching = {
            "lessons_received": 0,
            "teachers": {},
            "skills": {},
            "last_lesson": None,
            "last_teacher": None
        }

        # Family-specific bond history
        self.family_bonding = {
            "events": 0,
            "family_bonds": []
        }

        # Persistent group membership
        self.group = {
            "group_id": None,
            "member": False,
            "joined_order": None,
            "shared_scent": 0.0,
            "accepted_members": [],
            "group_events": 0,

            # Dynamic group reputation.
            "influence": 0.0,
            "defense_events": 0,
            "support_events": 0,
            "recruitment_support": 0,
            "recruitment_vetoes": 0
        }

        # Personal cultural identity.
        self.culture = {
            "adopted_traditions": {},
            "rejected_traditions": {},
            "preferences": {},
            "myths": {},
            "innovations": {},
            "exposures": 0
        }

        # Dynamic social roles inside groups.
        self.group_roles = {
            "active": {},
            "history": [],
            "role_events": 0
        }

        # Cat -> human relationships are distinct from
        # ordinary cat social relationships.
        self.human_bonds = {}

        # Rare interspecies MEOW invitations.
        self.meow_invitations = {
            "offered": 0,
            "understood": 0,
            "guided_to_bar": 0,
            "history": []
        }

        # Group norm / taboo history
        self.norms = {
            "violations": [],
            "sanctions": [],
            "warnings": 0,
            "trust_penalties": 0.0
        }

        self.special_traits = []
        self.aroma = aroma

        self.social_interactions = []
        self.pet_count = 0
        self.meow_count = 0

        # ----------------------------------------------------
        # Runtime world state
        # ----------------------------------------------------

        self.position = None
        self.location = None
        self.current_layer = "quantum_layer"
        self.world_key = None

        # Navigation
        self.suggested_intent = None
        self.navigation_target = None
        self.navigation_offer = None
        self.last_navigation_decision = None

        # Cronenberg / hunting
        self.hunt_quota = 0
        self.overpopulation_response_available = False
        self.scent_search = None
        self.known_scent_follow = None
        self.scent_box_follow = None

        # Quantum exploration
        self.quantum_transfer = None
        self.quantum_exploration = None
        self.quantum_return = None
        self.box_exploration = None
        self.exploration_goal = None

        # Development / birth
        self.birth_day = None
        self.developmental_stage = None
        self.mother_name = None

        self.birth_profile = None
        self.rolled_birth_profile = None
        self.birth_canonical = None
        self.birth_genetics = None
        self.birth_trait_dice_mapping = None
        self.birth_percentile = None
        self.canonical_identity = None

        # Distribution
        self.recipient = None
        self.distribution = None

        # Cat D20
        self.cat_d20 = None
        self.cat_d20_box = None

    def _entity_name(
        self,
        entity
    ):
        if isinstance(
            entity,
            dict
        ):
            return entity.get(
                "name"
            )

        return getattr(
            entity,
            "name",
            None
        )

    def accept_pet(
        self,
        by_entity
    ):
        actor_name = self._entity_name(
            by_entity
        )

        self.pet_count += 1

        event = {
            "type": "cat_pet",
            "cat": self.name,
            "by": actor_name,
            "accepted": True,
            "pet_number": self.pet_count
        }

        self.social_interactions.append(
            event
        )

        return event

    def meow_to(
        self,
        listener,
        topic=None
    ):
        meow_knowledge = (
            self.learning.get(
                "meow_knowledge",
                {}
            )
        )

        if not meow_knowledge.get(
            "can_speak",
            False
        ):
            return {
                "type": "cat_meow",
                "cat": self.name,
                "listener": self._entity_name(
                    listener
                ),
                "spoken": False,
                "reason": "meow_not_learned"
            }

        known_contents = list(
            meow_knowledge.get(
                "contains",
                []
            )
        )

        if (
            topic is not None
            and topic not in known_contents
        ):
            return {
                "type": "cat_meow",
                "cat": self.name,
                "listener": self._entity_name(
                    listener
                ),
                "spoken": False,
                "reason": "unknown_meow_topic",
                "topic": topic
            }

        self.meow_count += 1

        event = {
            "type": "cat_meow",
            "cat": self.name,
            "listener": self._entity_name(
                listener
            ),
            "spoken": True,
            "meow_number": self.meow_count,
            "topic": topic,
            "contains": (
                [topic]
                if topic is not None
                else known_contents
            )
        }

        self.social_interactions.append(
            event
        )

        return event

    # --------------------------------------------------------
    # Temporary mapping compatibility
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

    def __contains__(
        self,
        key
    ):
        return hasattr(
            self,
            key
        )

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

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

    def pop(
        self,
        key,
        default=None
    ):
        if hasattr(
            self,
            key
        ):
            value = getattr(
                self,
                key
            )

            delattr(
                self,
                key
            )

            return value

        return default

    def update(
        self,
        other=None,
        **kwargs
    ):
        if other is not None:
            if hasattr(
                other,
                "items"
            ):
                source = other.items()
            else:
                source = other

            for key, value in source:
                setattr(
                    self,
                    key,
                    value
                )

        for key, value in kwargs.items():
            setattr(
                self,
                key,
                value
            )

    def copy(self):
        return dict(
            self.__dict__
        )

    def __iter__(self):
        return iter(
            self.__dict__
        )

    def __len__(self):
        return len(
            self.__dict__
        )

    def __delitem__(
        self,
        key
    ):
        if not hasattr(
            self,
            key
        ):
            raise KeyError(
                key
            )

        delattr(
            self,
            key
        )
