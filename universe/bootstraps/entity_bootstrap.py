from universe.logger import UniverseLogger
from cats import Cats
from gods import Gods
from idea_entities import IdeaEntities


class EntityBootstrap:

    def __init__(
        self,
        universe,
        idea_universe,
        root_transition,
        pazuzu_profile=None
    ):
        self.universe = universe
        self.idea_universe = idea_universe
        self.root_transition = root_transition

        self.pazuzu_profile = {
            "color": "black",
            "fur_length": "short",
            "pattern": "solid",
            "eye_color": "green",
            "sex": "female"
        }

        if pazuzu_profile is not None:
            self.pazuzu_profile.update(
                dict(pazuzu_profile)
            )

    def run(self):
        self._create_god()
        self._create_pazuzu()
        self._create_serpent()
        self._create_lilith()
        self._create_pazuzu_masculine_principle()

        return (
            self.god,
            self.pazuzu,
            self.serpent,
            self.lilith,
            self.pazuzu_masculine_principle
        )


    def _create_god(self):
        # God was already created by UniverseBootstrap.
        #
        # EntityBootstrap does not create another God,
        # does not make him Creator and does not assign
        # Eden to him.

        self.gods = getattr(
            self.universe,
            "gods",
            None
        )

        self.god = getattr(
            self.universe,
            "god",
            None
        )

        if self.gods is None:
            raise RuntimeError(
                "Gods layer must exist before "
                "EntityBootstrap."
            )

        if self.god is None:
            self.god = (
                self.universe.world.get(
                    "god"
                )
            )

        if self.god is None:
            raise RuntimeError(
                "Canonical God must exist before "
                "EntityBootstrap."
            )

        if getattr(
            self.god,
            "type",
            None
        ) != "god":
            raise RuntimeError(
                "Canonical God is invalid."
            )

        if getattr(
            self.god,
            "role",
            None
        ) != "librarian":
            raise RuntimeError(
                "Canonical God must currently "
                "be the Librarian."
            )

        self.universe.world[
            "god"
        ] = self.god

        UniverseLogger.boot(
            "Canonical Librarian God reused "
            "by EntityBootstrap"
        )


    def _create_pazuzu(self):
        self.cats = getattr(
            self.universe,
            "cats_layer",
            None
        )

        if self.cats is None:
            self.cats = Cats(
                self.universe
            )

            self.universe.cats_layer = (
                self.cats
            )

        self.pazuzu = self.cats.create_cat(
            name="pazuzu",
            color=self.pazuzu_profile[
                "color"
            ],
            fur_length=self.pazuzu_profile[
                "fur_length"
            ],
            pattern=self.pazuzu_profile[
                "pattern"
            ],
            eye_color=self.pazuzu_profile[
                "eye_color"
            ],
            sex=self.pazuzu_profile[
                "sex"
            ]
        )

        self.pazuzu.alias = "classical_probe_debug_entity"

        self.pazuzu.access = {
            "cat_access": self.cats.access_rules,
            "eden": True,
            "meeting_place": True,
            "library": "read",
            "quantum_layer": "via_meeting_place"
        }

        self.universe.world["pazuzu"] = self.pazuzu
        self.universe.create_entity("pazuzu")
        self.universe.world["classical_probe_debug_entity"] = self.pazuzu

        UniverseLogger.boot("Pazuzu created as black cat")


    def _create_serpent(self):
        self.idea_entities = IdeaEntities(self.universe)

        self.universe.idea_entities = (
            self.idea_entities
        )

        self.universe.d20_registry.register(
            self.idea_entities.serpent_d20
        )

        self.serpent = self.idea_entities.create_idea_entity(
            name="serpent",
            role="primordial_idea_entity",
            active=False,
            existence_pct=100.0,
            native_world="idea_universe",
            existence_by_world={
                "idea_universe": 100.0,
                "root_universe": 0.0,
                "eden": 0.0
            }
        )

        self.serpent.energy_j = 0.0

        self.serpent.access = {
            "eden": True,
            "meeting_place": True,
            "quantum_layer": "via_meeting_place"
        }

        self.serpent.serpent_process = {
            "ready": False,
            "active": False,
            "knowledge_payload": None,
            "target": None
        }

        self.universe.world["serpent"] = self.serpent
        self.universe.create_entity("serpent")
        self.idea_universe.add_entity(self.serpent)

        UniverseLogger.boot("Serpent created as idea entity")

        serpent_can_create_transition = self.root_transition.can_create(
            self.serpent
        )

        UniverseLogger.boot(f"SERPENT CAN CREATE ROOT TRANSITION: {serpent_can_create_transition}")


    def _create_lilith(self):
        self.lilith = self.idea_entities.create_idea_entity(
            name="lilith",
            role="archetype_principle",
            active=True
        )

        self.lilith.principle = {
            "name": "feminine_principle",
            "domain": [
                "woman",
                "creation",
                "feminine_archetype"
            ],
            "origin": "lilith"
        }

        self.lilith.access = {
            "meeting_place": True,
            "library": "read",
            "quantum_layer": "via_meeting_place"
        }

        self.lilith.meeting_presence = False
        self.lilith.known_by_bartender = True
        self.lilith.history = [
            "lilith was born as an idea entity",
            "with lilith the feminine principle came into existence"
        ]

        self.universe.world["lilith"] = self.lilith
        self.universe.create_entity("lilith")

        UniverseLogger.boot("Lilith created as idea entity")


    def _create_pazuzu_masculine_principle(self):
        self.pazuzu_masculine_principle = (
            self.idea_entities.create_idea_entity(
                name="pazuzu",
                role="archetype_principle",
                active=True
            )
        )

        self.pazuzu_masculine_principle.alias = "pazuzu"
        self.pazuzu_masculine_principle.world_key = (
            "pazuzu_masculine_principle"
        )

        self.pazuzu_masculine_principle.principle = {
            "name": "masculine_principle",
            "domain": [
                "man",
                "creation",
                "masculine_archetype"
            ],
            "origin": "pazuzu_alias"
        }

        self.pazuzu_masculine_principle.access = {
            "meeting_place": False,
            "library": "read",
            "quantum_layer": True
        }

        self.pazuzu_masculine_principle.meeting_presence = False
        self.pazuzu_masculine_principle.known_by_bartender = False
        self.pazuzu_masculine_principle.history = [
            "pazuzu masculine principle was born in the idea world",
            "with pazuzu the masculine principle came into existence",
            "pazuzu masculine principle has no access to the bar"
        ]

        self.universe.create_entity("pazuzu_masculine_principle")
        self.universe.world["pazuzu_masculine_principle"] = (
            self.pazuzu_masculine_principle
        )

        UniverseLogger.boot("Pazuzu masculine principle created as idea entity")


    def _record_first_fire_interaction(self):
        self.idea_entities.record_fire_interaction(
            name="first_fire_interaction",
            participants=[
                "lilith",
                "pazuzu_masculine_principle"
            ],
            observer="serpent",
            state="unresolved",
            meaning=None
        )




