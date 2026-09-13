import unittest

from core.entity.serpent_d20 import SerpentD20
from core.eternal_flame.eternal_flame import EternalFlame
from idea_entities import IdeaEntities
from idea_entities.eternal_fire_potential import (
    EternalFirePotential,
)
from idea_entities.prefysical_fire_origin import (
    PrefysicalFireOrigin,
)
from universe.universe import Universe


class FixedRng:

    def __init__(self, first_roll):
        self.first_roll = first_roll
        self.roll_used = False

    def randint(self, start, end):
        if not self.roll_used:
            self.roll_used = True
            return self.first_roll

        return start

    def random(self):
        return 0.99

    def choice(self, sequence):
        return sequence[0]

    def sample(self, population, k):
        return list(population)[:k]

    def shuffle(self, sequence):
        return None


class EternalFirePotentialObjectStateTests(unittest.TestCase):

    def _system(self):
        universe = Universe()
        idea_entities = IdeaEntities(universe)
        universe.world["pazuzu_masculine_principle"] = {
            "name": "pazuzu",
            "type": "idea_entity",
            "energy_j": 100.0,
        }
        origin = idea_entities.prefysical_fire_origin
        origin.begin()

        return universe, idea_entities, origin

    def test_state_is_object_only(self):
        fire = EternalFirePotential()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(fire, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = fire["state"]

    def test_initial_values_and_public_shape_are_preserved(self):
        fire = EternalFirePotential()

        self.assertEqual(fire.name, "eternal_fire")
        self.assertEqual(fire.type, "idea_fire_potential")
        self.assertEqual(fire.state, "unignited")
        self.assertFalse(fire.actualized)
        self.assertIsNone(fire.physical_time)
        self.assertIsNone(fire.physical_location)
        self.assertTrue(fire.requires_maintenance)
        self.assertEqual(
            fire.maintainer,
            "pazuzu_masculine_principle",
        )
        self.assertEqual(fire.interactions, [])
        self.assertEqual(
            set(fire.to_dict()),
            {
                "name",
                "type",
                "state",
                "actualized",
                "physical_time",
                "physical_location",
                "requires_maintenance",
                "maintainer",
                "interactions",
            },
        )

    def test_origin_and_layer_share_same_state_object(self):
        _, idea_entities, origin = self._system()

        self.assertIsInstance(
            idea_entities.eternal_fire,
            EternalFirePotential,
        )
        self.assertIs(
            origin.eternal_fire,
            idea_entities.eternal_fire,
        )

    def test_world_keeps_detached_dict_boundary(self):
        universe, idea_entities, _ = self._system()
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertIsInstance(boundary, dict)
        self.assertIsNot(boundary, idea_entities.eternal_fire)

        boundary["state"] = "changed"
        boundary["interactions"].append("changed")

        self.assertEqual(
            idea_entities.eternal_fire.state,
            "unignited",
        )
        self.assertEqual(
            idea_entities.eternal_fire.interactions,
            [],
        )

    def test_failed_attempt_keeps_same_unactualized_object(self):
        universe, idea_entities, origin = self._system()
        fire = idea_entities.eternal_fire

        result = origin.attempt_ignition(
            rng=FixedRng(10)
        )

        self.assertEqual(result["result"], "fire_not_ignited")
        self.assertIs(idea_entities.eternal_fire, fire)
        self.assertFalse(fire.actualized)
        self.assertEqual(fire.state, "unignited")
        self.assertFalse(
            universe.world["idea_entities"][
                "eternal_fire"
            ]["actualized"]
        )

    def test_success_mutates_same_object_and_refreshes_boundary(self):
        universe, idea_entities, origin = self._system()
        fire = idea_entities.eternal_fire

        result = origin.attempt_ignition(
            rng=FixedRng(20)
        )
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertEqual(
            result["result"],
            "prefysical_fire_ignited",
        )
        self.assertIs(idea_entities.eternal_fire, fire)
        self.assertTrue(fire.actualized)
        self.assertEqual(fire.state, "burning")
        self.assertEqual(fire.type, "idea_focal_point")
        self.assertEqual(fire.flame_state, "small")
        self.assertEqual(fire.fuel["wood_sticks"], 2.0)
        self.assertTrue(boundary["actualized"])
        self.assertEqual(boundary["state"], "burning")
        self.assertEqual(boundary["fuel"]["wood_sticks"], 2.0)

    def test_significance_mutates_object_and_boundary(self):
        universe, idea_entities, origin = self._system()
        origin.attempt_ignition(rng=FixedRng(20))

        origin.understand_fire_significance()
        fire = idea_entities.eternal_fire
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertTrue(fire.meaning["requires_fuel"])
        self.assertEqual(
            fire.guardian,
            "pazuzu_masculine_principle",
        )
        self.assertEqual(
            fire.fuel_seekers,
            ["lilith", "serpent"],
        )
        self.assertTrue(boundary["meaning"]["requires_fuel"])
        self.assertEqual(
            boundary["fuel_seekers"],
            ["lilith", "serpent"],
        )

    def test_fuel_advance_mutates_object_and_boundary(self):
        universe, idea_entities, origin = self._system()
        origin.attempt_ignition(rng=FixedRng(20))

        origin.advance_fire()
        fire = idea_entities.eternal_fire
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertEqual(fire.fuel["dry_grass"], 0.0)
        self.assertEqual(
            fire.fuel_consumed_last_step["dry_grass"],
            1.0,
        )
        self.assertEqual(boundary["fuel"]["dry_grass"], 0.0)
        self.assertEqual(
            boundary["fuel_consumed_last_step"]["dry_grass"],
            1.0,
        )

    def test_interaction_mutates_object_and_boundary(self):
        universe, idea_entities, _ = self._system()
        fire = idea_entities.eternal_fire

        interaction = idea_entities.record_fire_interaction(
            name="fire_watched",
            participants=["serpent"],
            observer="lilith",
        )
        boundary = universe.world["idea_entities"][
            "eternal_fire"
        ]

        self.assertIs(idea_entities.eternal_fire, fire)
        self.assertIs(fire.interactions[0], interaction)
        self.assertEqual(
            boundary["interactions"],
            [interaction],
        )

    def test_to_dict_is_deeply_detached(self):
        fire = EternalFirePotential()
        fire.actualized = True
        fire.fuel = {"wood_sticks": 2.0}
        fire.meaning = {"requires_fuel": True}
        fire.interactions.append({"name": "watched"})

        snapshot = fire.to_dict()
        snapshot["fuel"]["wood_sticks"] = 999.0
        snapshot["meaning"]["requires_fuel"] = False
        snapshot["interactions"][0]["name"] = "changed"

        self.assertEqual(fire.fuel["wood_sticks"], 2.0)
        self.assertTrue(fire.meaning["requires_fuel"])
        self.assertEqual(
            fire.interactions[0]["name"],
            "watched",
        )

    def test_origin_rejects_old_mapping_state(self):
        with self.assertRaises(TypeError):
            PrefysicalFireOrigin(
                eternal_fire={"name": "eternal_fire"},
                serpent_d20=SerpentD20(),
            )

    def test_eternal_flame_accepts_object_and_rejects_mapping(self):
        fire = EternalFirePotential()
        fire.type = "idea_focal_point"
        fire.state = "burning"
        fire.actualized = True
        flame = EternalFlame()

        result = flame.ignite(
            fire,
            tick=1,
            keeper="pazuzu",
        )

        self.assertEqual(result["name"], "eternal_flame_ignited")
        self.assertEqual(
            result["source_idea"],
            {
                "name": "eternal_fire",
                "type": "idea_focal_point",
                "state": "burning",
            },
        )

        with self.assertRaises(TypeError):
            EternalFlame().ignite(fire.to_dict())


if __name__ == "__main__":
    unittest.main()
