import unittest

from idea_entities import IdeaEntities
from idea_entities.prefysical_fire_state import (
    PrefysicalFireEnergyConversion,
    PrefysicalFireMaterials,
    PrefysicalFireRoles,
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


class PrefysicalFireOriginObjectStateTests(unittest.TestCase):

    def _origin(self, begin=True):
        universe = Universe()
        idea_entities = IdeaEntities(universe)
        universe.world["pazuzu_masculine_principle"] = {
            "name": "pazuzu",
            "type": "idea_entity",
            "energy_j": 100.0,
        }
        origin = idea_entities.prefysical_fire_origin

        if begin:
            origin.begin()

        return universe, idea_entities, origin

    def test_records_are_object_only(self):
        records = (
            PrefysicalFireMaterials(),
            PrefysicalFireEnergyConversion(),
            PrefysicalFireRoles(),
        )

        for record in records:
            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
            ):
                self.assertFalse(
                    hasattr(record, mapping_method)
                )

            with self.assertRaises(TypeError):
                _ = record["missing"]

    def test_initial_values_are_preserved(self):
        _, _, origin = self._origin(begin=False)

        self.assertEqual(origin.materials.wood_sticks, 2)
        self.assertTrue(origin.materials.dry_grass)
        self.assertEqual(origin.materials.found_by, "serpent")
        self.assertIsNone(origin.materials.handed_to)
        self.assertEqual(
            origin.energy_conversion.masculine_energy_spent_j,
            0.0,
        )
        self.assertEqual(
            origin.energy_conversion.friction_heat_j,
            0.0,
        )
        self.assertIsNone(origin.roles.fire_guardian)
        self.assertEqual(origin.roles.fuel_seekers, [])

    def test_begin_mutates_same_materials_object(self):
        _, _, origin = self._origin(begin=False)
        materials = origin.materials

        event = origin.begin()

        self.assertIs(origin.materials, materials)
        self.assertEqual(
            materials.handed_to,
            "pazuzu_masculine_principle",
        )
        self.assertIsInstance(event["details"]["materials"], dict)
        self.assertEqual(
            event["details"]["materials"]["handed_to"],
            "pazuzu_masculine_principle",
        )

    def test_attempt_mutates_same_energy_conversion_object(self):
        universe, _, origin = self._origin()
        conversion = origin.energy_conversion
        before = universe.world[
            "pazuzu_masculine_principle"
        ]["energy_j"]

        result = origin.attempt_ignition(
            rng=FixedRng(10)
        )

        self.assertIs(origin.energy_conversion, conversion)
        self.assertGreater(
            conversion.masculine_energy_spent_j,
            0.0,
        )
        self.assertEqual(
            conversion.masculine_energy_spent_j,
            conversion.friction_heat_j,
        )
        self.assertEqual(
            result["energy_conversion"][
                "source_energy_before_j"
            ],
            before,
        )

    def test_success_reads_object_records(self):
        _, idea_entities, origin = self._origin()

        origin.attempt_ignition(rng=FixedRng(20))

        self.assertEqual(
            idea_entities.eternal_fire.fuel.wood_sticks,
            float(origin.materials.wood_sticks),
        )
        self.assertEqual(
            idea_entities.eternal_fire.heat_energy_j,
            origin.energy_conversion.friction_heat_j,
        )

    def test_significance_mutates_same_roles_object(self):
        _, _, origin = self._origin()
        roles = origin.roles
        origin.attempt_ignition(rng=FixedRng(20))

        origin.understand_fire_significance()

        self.assertIs(origin.roles, roles)
        self.assertEqual(
            roles.fire_guardian,
            "pazuzu_masculine_principle",
        )
        self.assertEqual(
            roles.fuel_seekers,
            ["lilith", "serpent"],
        )

    def test_repeated_significance_event_keeps_dict_boundary(self):
        _, _, origin = self._origin()
        origin.attempt_ignition(rng=FixedRng(20))
        origin.understand_fire_significance()

        event = origin.understand_fire_significance()

        self.assertIsInstance(event["details"]["roles"], dict)
        self.assertEqual(
            event["details"]["roles"]["fuel_seekers"],
            ["lilith", "serpent"],
        )

    def test_public_state_keeps_detached_dict_boundaries(self):
        _, _, origin = self._origin()
        origin.attempt_ignition(rng=FixedRng(20))
        origin.understand_fire_significance()

        public_state = origin.public_state

        self.assertIsInstance(public_state["materials"], dict)
        self.assertIsInstance(
            public_state["energy_conversion"],
            dict,
        )
        self.assertIsInstance(public_state["roles"], dict)

        public_state["materials"]["wood_sticks"] = 999
        public_state["energy_conversion"][
            "friction_heat_j"
        ] = 999.0
        public_state["roles"]["fuel_seekers"].append(
            "changed"
        )

        self.assertEqual(origin.materials.wood_sticks, 2)
        self.assertNotEqual(
            origin.energy_conversion.friction_heat_j,
            999.0,
        )
        self.assertEqual(
            origin.roles.fuel_seekers,
            ["lilith", "serpent"],
        )

    def test_to_dict_snapshots_are_detached(self):
        materials = PrefysicalFireMaterials()
        conversion = PrefysicalFireEnergyConversion()
        roles = PrefysicalFireRoles(
            fuel_seekers=["lilith", "serpent"]
        )

        material_snapshot = materials.to_dict()
        conversion_snapshot = conversion.to_dict()
        role_snapshot = roles.to_dict()

        material_snapshot["wood_sticks"] = 999
        conversion_snapshot["friction_heat_j"] = 999.0
        role_snapshot["fuel_seekers"].append("changed")

        self.assertEqual(materials.wood_sticks, 2)
        self.assertEqual(conversion.friction_heat_j, 0.0)
        self.assertEqual(
            roles.fuel_seekers,
            ["lilith", "serpent"],
        )


if __name__ == "__main__":
    unittest.main()
