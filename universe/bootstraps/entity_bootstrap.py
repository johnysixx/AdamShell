from cats import Cats
from gods import Gods
from idea_entities import IdeaEntities


class EntityBootstrap:

    def __init__(self, universe, idea_universe, root_transition):
        self.universe = universe
        self.idea_universe = idea_universe
        self.root_transition = root_transition

    def run(self):
        self.gods = Gods(self.universe)
        self.god = self.gods.create_god(
            name="god",
            role="creator_entity"
        )

        self.god["role"] = {
            "creator_of": ["eden"],
            "authority": "creator"
        }

        self.god["access"] = {
            "eden": True,
            "universe": "via_eden",
            "quantum_layer": "via_eden",
            "meeting_place": True,
            "library": "write"
        }

        self.god["meeting_place_access"] = {
            "quantum_layer": True,
            "eden": False,
            "universe": False
        }

        self.god["administers"] = [
            "eden",
            "library",
            "root_universe"
        ]

        self.universe.world["god"] = self.god
        self.universe.create_entity("god")

        print("God entity created from Gods layer")

        self.cats = Cats(self.universe)

        self.pazuzu = self.cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short",
            pattern="solid",
            eye_color="green"
        )

        self.pazuzu["alias"] = "classical_probe_debug_entity"

        self.pazuzu["access"] = {
            "cat_access": self.cats.access_rules,
            "eden": True,
            "meeting_place": True,
            "library": "read",
            "quantum_layer": "via_meeting_place"
        }

        self.universe.world["pazuzu"] = self.pazuzu
        self.universe.create_entity("pazuzu")
        self.universe.world["classical_probe_debug_entity"] = self.pazuzu

        print("Pazuzu created as black cat")

        self.idea_entities = IdeaEntities(self.universe)

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

        self.serpent["energy_j"] = 0.0

        self.serpent["access"] = {
            "eden": True,
            "meeting_place": True,
            "quantum_layer": "via_meeting_place"
        }

        self.serpent["serpent_process"] = {
            "ready": False,
            "active": False,
            "knowledge_payload": None,
            "target": None
        }

        self.universe.world["serpent"] = self.serpent
        self.universe.create_entity("serpent")
        self.idea_universe.add_entity(self.serpent)

        print("Serpent created as idea entity")

        serpent_can_create_transition = self.root_transition.can_create(
            self.serpent
        )

        print(
            "SERPENT CAN CREATE ROOT TRANSITION:",
            serpent_can_create_transition
        )

        self.lilith = self.idea_entities.create_idea_entity(
            name="lilith",
            role="archetype_principle",
            active=True
        )

        self.lilith["principle"] = {
            "name": "feminine_principle",
            "domain": [
                "woman",
                "creation",
                "feminine_archetype"
            ],
            "origin": "lilith"
        }

        self.lilith["access"] = {
            "meeting_place": True,
            "library": "read",
            "quantum_layer": "via_meeting_place"
        }

        self.lilith["meeting_presence"] = False
        self.lilith["known_by_bartender"] = True
        self.lilith["history"] = [
            "lilith was born as an idea entity",
            "with lilith the feminine principle came into existence"
        ]

        self.universe.world["lilith"] = self.lilith
        self.universe.create_entity("lilith")

        print("Lilith created as idea entity")

        self.pazuzu_masculine_principle = (
            self.idea_entities.create_idea_entity(
                name="pazuzu",
                role="archetype_principle",
                active=True
            )
        )

        self.pazuzu_masculine_principle["alias"] = "pazuzu"
        self.pazuzu_masculine_principle["world_key"] = (
            "pazuzu_masculine_principle"
        )

        self.pazuzu_masculine_principle["principle"] = {
            "name": "masculine_principle",
            "domain": [
                "man",
                "creation",
                "masculine_archetype"
            ],
            "origin": "pazuzu_alias"
        }

        self.pazuzu_masculine_principle["access"] = {
            "meeting_place": False,
            "library": "read",
            "quantum_layer": True
        }

        self.pazuzu_masculine_principle["meeting_presence"] = False
        self.pazuzu_masculine_principle["known_by_bartender"] = False
        self.pazuzu_masculine_principle["history"] = [
            "pazuzu masculine principle was born in the idea world",
            "with pazuzu the masculine principle came into existence",
            "pazuzu masculine principle has no access to the bar"
        ]

        self.universe.create_entity("pazuzu_masculine_principle")
        self.universe.world["pazuzu_masculine_principle"] = (
            self.pazuzu_masculine_principle
        )

        print("Pazuzu masculine principle created as idea entity")

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

        return (
            self.god,
            self.pazuzu,
            self.serpent,
            self.lilith,
            self.pazuzu_masculine_principle
        )






