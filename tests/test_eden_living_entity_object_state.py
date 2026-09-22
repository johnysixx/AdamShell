import unittest

from eden import Eden
from eden.living_objects import EdenAnimal, EdenFruitTree, EdenPlant
from universe.universe import Universe


class EdenLivingEntityObjectStateTests(unittest.TestCase):

    def _created_life(self):
        universe = Universe()
        eden = Eden(universe)
        eden.day_1()
        eden.day_2()
        return universe, eden

    def _assert_object_only(self, value, key):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def test_day_one_creates_plant_and_tree_objects(self):
        universe = Universe()
        eden = Eden(universe)

        eden.day_1()

        grass, herb = eden.plants
        fruit_tree = eden.trees[0]

        self.assertIsInstance(grass, EdenPlant)
        self.assertIsInstance(herb, EdenPlant)
        self.assertIsInstance(fruit_tree, EdenFruitTree)
        self.assertEqual(
            (grass.name, herb.name, fruit_tree.name),
            ("grass", "herb", "fruit_tree"),
        )
        self.assertTrue(grass.edible)
        self.assertTrue(herb.edible)
        self.assertTrue(fruit_tree.fruit)
        self.assertFalse(grass.forbidden)
        self.assertFalse(fruit_tree.forbidden)

    def test_day_two_creates_animal_objects(self):
        universe = Universe()
        eden = Eden(universe)

        eden.day_2()

        bird, fish, beast = eden.animals

        for animal in eden.animals:
            self.assertIsInstance(
                animal,
                EdenAnimal,
            )

        self.assertEqual(
            (bird.kind, fish.kind, beast.kind),
            ("air", "water", "land"),
        )
        self.assertEqual(
            [animal.name for animal in eden.animals],
            ["bird", "fish", "beast"],
        )

    def test_world_collections_keep_same_live_objects(self):
        universe, eden = self._created_life()

        self.assertIs(
            universe.world["eden_plants"],
            eden.plants,
        )
        self.assertIs(
            universe.world["eden_trees"],
            eden.trees,
        )
        self.assertIs(
            universe.world["eden_animals"],
            eden.animals,
        )
        self.assertIs(
            universe.world["eden_entities"],
            eden.entities,
        )
        self.assertIs(
            eden.entities[0],
            eden.plants[0],
        )
        self.assertIs(
            eden.entities[2],
            eden.trees[0],
        )
        self.assertIs(
            eden.entities[3],
            eden.animals[0],
        )

    def test_living_entities_are_object_only(self):
        _, eden = self._created_life()

        self._assert_object_only(
            eden.plants[0],
            "edible",
        )
        self._assert_object_only(
            eden.trees[0],
            "fruit",
        )
        self._assert_object_only(
            eden.animals[0],
            "kind",
        )

    def test_state_snapshot_serializes_living_entities(self):
        _, eden = self._created_life()

        snapshot = eden.eden_state.to_dict()

        self.assertIsInstance(
            snapshot["plants"][0],
            dict,
        )
        self.assertIsInstance(
            snapshot["trees"][0],
            dict,
        )
        self.assertIsInstance(
            snapshot["animals"][0],
            dict,
        )
        self.assertIsInstance(
            snapshot["entities"][0],
            dict,
        )

        self.assertEqual(
            snapshot["plants"][0]["name"],
            "grass",
        )
        self.assertEqual(
            snapshot["trees"][0]["type"],
            "tree",
        )
        self.assertEqual(
            snapshot["animals"][0]["kind"],
            "air",
        )

    def test_snapshots_are_detached_boundaries(self):
        _, eden = self._created_life()

        grass = eden.plants[0]
        bird = eden.animals[0]
        snapshot = eden.eden_state.to_dict()

        snapshot["plants"][0]["name"] = "changed"
        snapshot["animals"][0]["kind"] = "changed"
        snapshot["entities"][0]["state"] = "changed"

        self.assertEqual(grass.name, "grass")
        self.assertEqual(grass.state, "alive")
        self.assertEqual(bird.kind, "air")

    def test_invalid_animal_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            EdenAnimal(
                name="unknown",
                kind="space",
            )


if __name__ == "__main__":
    unittest.main()
