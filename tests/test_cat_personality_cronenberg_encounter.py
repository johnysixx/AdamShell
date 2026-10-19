import unittest
from universe.universe import Universe
from core.entity.components import SpatialVector3
from cats.cat_cronenberg_encounter_memory_details import (
    CatCronenbergEncounterMemoryDetails,
)
from core.entity.cronenberg_system.origin import (
    CronenbergOrigin,
)
from core.entity.cronenberg_system.traits import (
    CronenbergTraitValues,
)

class FixedRng:

    def __init__(self, random_value):
        self.random_value = float(random_value)

    def random(self):
        return self.random_value

class CatPersonalityCronenbergEncounterTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()
        result = self.universe.manifest_cat(name='hunter', source='test', position=SpatialVector3(x=0.0, y=0.0, z=0.0))
        self.cat = result.cat

    def create_cronenberg(self, size):
        cronenberg = self.universe.create_cronenberg_from_quantum_error(error=RuntimeError('Personality encounter test.'), source_component='test', source_operation='personality_encounter')
        cronenberg.position = SpatialVector3(x=1.0, y=0.0, z=0.0)
        cronenberg.size = float(size)
        return cronenberg

    def create_route(self, cronenberg):
        result = self.universe.quantum_space.plan_direct_cat_route(cat_id=self.cat.name, start_position=SpatialVector3(x=0.0, y=0.0, z=0.0), destination_position=cronenberg.position, destination=cronenberg.id, step_size=1.0)
        return result.route

    def traits(self):
        return self.cat.personality.traits

    def test_successful_hunt_builds_courage(self):
        cronenberg = self.create_cronenberg(size=0.5)
        route = self.create_route(cronenberg)
        result = self.universe.cat_cronenberg_encounter.resolve(cat=self.cat, cronenberg=cronenberg, route=route, universe=self.universe, rng=FixedRng(1.0))
        self.assertEqual(result.result, 'cronenberg_hunted')
        self.assertAlmostEqual(self.traits().courage, 0.54)
        self.assertAlmostEqual(self.traits().aggression, 0.525)
        self.assertAlmostEqual(self.traits().curiosity, 0.51)

    def test_cronenberg_memory_details_are_objects(
        self
    ):
        cronenberg = self.create_cronenberg(
            size=0.5
        )

        route = self.create_route(
            cronenberg
        )

        (
            self.universe
            .cat_cronenberg_encounter
            .resolve(
                cat=self.cat,
                cronenberg=cronenberg,
                route=route,
                universe=self.universe,
                rng=FixedRng(1.0),
            )
        )

        memory = (
            self.cat
            .memory
            .cronenberg_encounters[-1]
        )

        details = memory.details

        self.assertIsInstance(
            details,
            CatCronenbergEncounterMemoryDetails,
        )

        for name in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
            "__setitem__",
            "update",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    details,
                    name,
                )
            )

        self.assertEqual(
            details.result,
            "cronenberg_hunted",
        )

        self.assertIsInstance(
            details.origin,
            CronenbergOrigin,
        )

        self.assertIsInstance(
            details.traits,
            CronenbergTraitValues,
        )

        self.assertTrue(
            all(
                not isinstance(
                    influence,
                    dict,
                )
                for influence
                in details.trait_birth_influences
            )
        )

        self.assertTrue(
            all(
                not isinstance(
                    link,
                    dict,
                )
                for link
                in details.quantum_links
            )
        )

        eaten = (
            self.cat
            .memory
            .cronenbergs_eaten
        )

        self.assertEqual(
            len(eaten),
            1,
        )

        self.assertIsInstance(
            eaten[0].details,
            CatCronenbergEncounterMemoryDetails,
        )

        snapshot = (
            self.cat
            .memory
            .public_state[
                "events"
            ][-1]
        )

        self.assertIsInstance(
            snapshot["details"],
            dict,
        )

        self.assertIsInstance(
            snapshot[
                "details"
            ][
                "origin"
            ],
            dict,
        )

        self.assertIsInstance(
            snapshot[
                "details"
            ][
                "traits"
            ],
            dict,
        )

    def test_large_cronenberg_builds_patience(self):
        cronenberg = self.create_cronenberg(size=2.0)
        route = self.create_route(cronenberg)
        result = self.universe.cat_cronenberg_encounter.resolve(cat=self.cat, cronenberg=cronenberg, route=route, universe=self.universe, rng=FixedRng(1.0))
        self.assertEqual(result.result, 'cat_avoids_cronenberg')
        self.assertAlmostEqual(self.traits().patience, 0.53)
        self.assertAlmostEqual(self.traits().courage, 0.51)

    def test_escaped_prey_builds_patience(self):
        cronenberg = self.create_cronenberg(size=0.8)
        route = self.create_route(cronenberg)
        result = self.universe.cat_cronenberg_encounter.resolve(cat=self.cat, cronenberg=cronenberg, route=route, universe=self.universe, rng=FixedRng(0.0))
        self.assertEqual(result.result, 'cronenberg_escaped')
        self.assertAlmostEqual(self.traits().patience, 0.52)
        self.assertAlmostEqual(self.traits().curiosity, 0.51)
if __name__ == '__main__':
    unittest.main()
