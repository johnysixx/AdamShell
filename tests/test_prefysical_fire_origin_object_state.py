import unittest
from core.entity.social_entity import SocialEntity

from idea_entities import IdeaEntities
from idea_entities.prefysical_fire_origin import (
    PrefysicalFireAlreadyBurningResult,
    PrefysicalFireEnergyConversionEvent,
    PrefysicalFireEvent,
    PrefysicalFireIgnitedResult,
    PrefysicalFireIgnitionFailedResult,
)
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
        universe.world["pazuzu_masculine_principle"] = SocialEntity(
            name="pazuzu",
            type="idea_entity",
            energy_j=100.0,
        )
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
        self.assertIsInstance(
            event,
            PrefysicalFireEvent,
        )
        self.assertEqual(
            event.details[
                "materials"
            ][
                "handed_to"
            ],
            "pazuzu_masculine_principle",
        )

    def test_attempt_mutates_same_energy_conversion_object(self):
        universe, _, origin = self._origin()
        conversion = origin.energy_conversion
        before = universe.world[
            "pazuzu_masculine_principle"
        ].energy_j

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
            result
            .energy_conversion
            .source_energy_before_j,
            before,
        )

        self.assertIsInstance(
            result,
            PrefysicalFireIgnitionFailedResult,
        )
        self.assertIsInstance(
            result.energy_conversion,
            PrefysicalFireEnergyConversionEvent,
        )
        self.assertIsInstance(
            result.attempt_event,
            PrefysicalFireEvent,
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

    def test_repeated_significance_event_uses_object_state(self):
        _, _, origin = self._origin()
        origin.attempt_ignition(rng=FixedRng(20))
        origin.understand_fire_significance()

        event = origin.understand_fire_significance()

        self.assertIsInstance(
            event,
            PrefysicalFireEvent,
        )
        self.assertEqual(
            event.details[
                "roles"
            ][
                "fuel_seekers"
            ],
            (
                "lilith",
                "serpent",
            ),
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["details"]

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

    def test_nested_fuel_seeker_snapshots_are_detached(self):
        seeker = {
            "name": "lilith",
            "metadata": {
                "notes": ["original"],
            },
        }

        roles = PrefysicalFireRoles(
            fuel_seekers=[seeker],
        )

        first = roles.to_dict()
        second = roles.to_dict()

        first["fuel_seekers"][0][
            "metadata"
        ]["notes"].append("snapshot_only")

        self.assertEqual(
            seeker["metadata"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["fuel_seekers"][0][
                "metadata"
            ]["notes"],
            ["original"],
        )

        self.assertEqual(
            roles.to_dict()["fuel_seekers"][0][
                "metadata"
            ]["notes"],
            ["original"],
        )

        self.assertIs(
            roles.fuel_seekers[0],
            seeker,
        )

        self.assertIsNot(
            first["fuel_seekers"][0],
            seeker,
        )

    def test_nested_fire_guardian_snapshot_is_detached(self):
        guardian = {
            "name": "pazuzu",
            "permissions": {
                "roles": ["guardian"],
            },
        }

        roles = PrefysicalFireRoles(
            fire_guardian=guardian,
        )

        first = roles.to_dict()
        second = roles.to_dict()

        first["fire_guardian"][
            "permissions"
        ]["roles"].append("snapshot_only")

        self.assertEqual(
            guardian["permissions"]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            second["fire_guardian"][
                "permissions"
            ]["roles"],
            ["guardian"],
        )

        guardian["permissions"][
            "roles"
        ].append("live_change")

        self.assertEqual(
            second["fire_guardian"][
                "permissions"
            ]["roles"],
            ["guardian"],
        )

        self.assertEqual(
            roles.to_dict()["fire_guardian"][
                "permissions"
            ]["roles"],
            ["guardian", "live_change"],
        )

        self.assertIs(
            roles.fire_guardian,
            guardian,
        )

    def test_public_state_preserves_live_fire_roles(self):
        _, _, origin = self._origin(
            begin=False
        )

        roles = origin.roles

        guardian = {
            "name": "pazuzu",
            "notes": ["original"],
        }

        seeker = {
            "name": "serpent",
            "notes": ["original"],
        }

        roles.fire_guardian = guardian
        roles.fuel_seekers.append(seeker)

        first = origin.public_state
        second = origin.public_state

        self.assertIs(
            origin.roles,
            roles,
        )

        self.assertIs(
            roles.fire_guardian,
            guardian,
        )

        self.assertIs(
            roles.fuel_seekers[0],
            seeker,
        )

        first["roles"]["fire_guardian"][
            "notes"
        ].append("snapshot_only")

        first["roles"]["fuel_seekers"][0][
            "notes"
        ].append("snapshot_only")

        self.assertEqual(
            guardian["notes"],
            ["original"],
        )

        self.assertEqual(
            seeker["notes"],
            ["original"],
        )

        self.assertEqual(
            second["roles"]["fire_guardian"][
                "notes"
            ],
            ["original"],
        )

        self.assertEqual(
            second["roles"]["fuel_seekers"][0][
                "notes"
            ],
            ["original"],
        )

        guardian["notes"].append(
            "live_change"
        )

        seeker["notes"].append(
            "live_change"
        )

        current = origin.public_state

        self.assertEqual(
            current["roles"]["fire_guardian"][
                "notes"
            ],
            ["original", "live_change"],
        )

        self.assertEqual(
            current["roles"]["fuel_seekers"][0][
                "notes"
            ],
            ["original", "live_change"],
        )

        self.assertIs(
            origin.roles,
            roles,
        )

    def test_material_recipient_snapshot_detaches_nested_data(self):
        recipient = {
            "name": "pazuzu",
            "inventory": {
                "items": ["wood"],
            },
        }

        materials = PrefysicalFireMaterials(
            handed_to=recipient,
        )

        first = materials.to_dict()
        second = materials.to_dict()

        first["handed_to"]["inventory"][
            "items"
        ].append("snapshot_only")

        self.assertEqual(
            recipient["inventory"]["items"],
            ["wood"],
        )

        self.assertEqual(
            second["handed_to"]["inventory"][
                "items"
            ],
            ["wood"],
        )

        self.assertEqual(
            materials.to_dict()["handed_to"][
                "inventory"
            ]["items"],
            ["wood"],
        )

        self.assertIs(
            materials.handed_to,
            recipient,
        )

        self.assertIsNot(
            first["handed_to"],
            recipient,
        )

    def test_material_recipient_snapshot_ignores_later_changes(self):
        recipient = {
            "name": "pazuzu",
            "history": ["original"],
        }

        materials = PrefysicalFireMaterials(
            handed_to=recipient,
        )

        snapshot = materials.to_dict()

        recipient["history"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot["handed_to"]["history"],
            ["original"],
        )

        self.assertEqual(
            materials.to_dict()["handed_to"][
                "history"
            ],
            ["original", "live_change"],
        )

        self.assertIs(
            materials.handed_to,
            recipient,
        )

        default_materials = PrefysicalFireMaterials()

        self.assertIsNone(
            default_materials.to_dict()["handed_to"]
        )

        self.assertEqual(
            PrefysicalFireMaterials(
                handed_to="pazuzu_masculine_principle"
            ).to_dict()["handed_to"],
            "pazuzu_masculine_principle",
        )

    def test_world_material_snapshots_preserve_live_identity(self):
        universe = Universe()
        layer = IdeaEntities(universe)

        origin = layer.prefysical_fire_origin
        materials = origin.materials

        recipient = {
            "name": "pazuzu",
            "inventory": {
                "wood": ["original"],
            },
        }

        materials.handed_to = recipient

        layer.write_to_world()

        world_snapshot = universe.world[
            "idea_entities"
        ]["prefysical_fire_origin"]["materials"]

        public_snapshot = layer.public_state[
            "prefysical_fire_origin"
        ]["materials"]

        origin_snapshot = origin.public_state[
            "materials"
        ]

        self.assertIs(
            origin.materials,
            materials,
        )

        self.assertIs(
            materials.handed_to,
            recipient,
        )

        world_snapshot["handed_to"][
            "inventory"
        ]["wood"].append("snapshot_only")

        self.assertEqual(
            recipient["inventory"]["wood"],
            ["original"],
        )

        for snapshot in (
            public_snapshot,
            origin_snapshot,
        ):
            self.assertEqual(
                snapshot["handed_to"][
                    "inventory"
                ]["wood"],
                ["original"],
            )

        recipient["inventory"]["wood"].append(
            "live_change"
        )

        self.assertEqual(
            world_snapshot["handed_to"][
                "inventory"
            ]["wood"],
            ["original", "snapshot_only"],
        )

        self.assertEqual(
            public_snapshot["handed_to"][
                "inventory"
            ]["wood"],
            ["original"],
        )

        current = layer.public_state[
            "prefysical_fire_origin"
        ]["materials"]

        self.assertEqual(
            current["handed_to"]["inventory"][
                "wood"
            ],
            ["original", "live_change"],
        )

        self.assertIs(
            layer.prefysical_fire_origin,
            origin,
        )

        self.assertIs(
            origin.materials,
            materials,
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


    def test_ignition_results_are_object_only(
        self
    ):
        _, _, origin = self._origin()

        failed = origin.attempt_ignition(
            rng=FixedRng(10)
        )

        ignited = origin.attempt_ignition(
            rng=FixedRng(20)
        )

        already = origin.attempt_ignition()

        self.assertIsInstance(
            failed,
            PrefysicalFireIgnitionFailedResult,
        )
        self.assertIsInstance(
            ignited,
            PrefysicalFireIgnitedResult,
        )
        self.assertIsInstance(
            already,
            PrefysicalFireAlreadyBurningResult,
        )

        self.assertIsInstance(
            failed.energy_conversion,
            PrefysicalFireEnergyConversionEvent,
        )
        self.assertIsInstance(
            ignited.energy_conversion,
            PrefysicalFireEnergyConversionEvent,
        )

        for result in (
            failed,
            ignited,
            already,
        ):
            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
            ):
                self.assertFalse(
                    hasattr(
                        result,
                        mapping_method,
                    )
                )

            with self.assertRaises(
                TypeError
            ):
                _ = result["result"]

        snapshot = ignited.to_dict()

        self.assertIsInstance(
            snapshot,
            dict,
        )
        self.assertIsInstance(
            snapshot["public_roll"],
            dict,
        )
        self.assertIsInstance(
            snapshot["energy_conversion"],
            dict,
        )
        self.assertIsInstance(
            snapshot["ignition_event"],
            dict,
        )


if __name__ == "__main__":
    unittest.main()
