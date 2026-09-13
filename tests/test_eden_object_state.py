import unittest

from eden import Eden
from eden.eden_state import EdenState
from universe.universe import Universe


class EdenObjectStateTests(unittest.TestCase):

    def _eden(self):
        universe = Universe()
        eden = Eden(universe)

        return universe, eden

    def test_state_is_object_only(self):
        state = EdenState()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(state, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = state["day"]

    def test_initial_values_are_preserved(self):
        _, eden = self._eden()
        state = eden.eden_state

        self.assertIs(eden.state, state)
        self.assertEqual(state.name, "eden")
        self.assertEqual(state.layer_type, "sandbox")
        self.assertEqual(state.status, "initialized")
        self.assertEqual(state.creator, "god")
        self.assertEqual(state.created_by, "god")
        self.assertEqual(state.administrator, "god")
        self.assertEqual(state.day, 0)
        self.assertEqual(state.max_day, 7)
        self.assertEqual(state.tick_count, 0)

    def test_collections_are_owned_by_state_object(self):
        _, eden = self._eden()
        state = eden.eden_state

        self.assertIs(eden.entities, state.entities)
        self.assertIs(eden.plants, state.plants)
        self.assertIs(eden.trees, state.trees)
        self.assertIs(eden.animals, state.animals)
        self.assertIs(eden.rules, state.rules)
        self.assertIs(eden.relations, state.relations)
        self.assertIs(eden.permissions, state.permissions)

    def test_world_keeps_object_and_dict_boundaries(self):
        universe, eden = self._eden()

        self.assertIs(
            universe.world["eden_state"],
            eden.eden_state,
        )
        self.assertIsInstance(universe.world["eden"], dict)
        self.assertIsInstance(
            universe.world["eden"]["eden_state"],
            dict,
        )

    def test_existing_public_metadata_is_preserved(self):
        universe, eden = self._eden()
        boundary = universe.world["eden"]

        self.assertEqual(boundary["name"], "eden")
        self.assertEqual(boundary["type"], "sandbox")
        self.assertEqual(boundary["state"], "initialized")
        self.assertEqual(boundary["creator"], "god")
        self.assertEqual(boundary["created_by"], "god")
        self.assertEqual(boundary["administrator"], "god")
        self.assertIs(boundary["permissions"], eden.permissions)

    def test_add_entity_mutates_same_state_object(self):
        universe, eden = self._eden()
        state = eden.eden_state
        entity = {"name": "adam"}

        eden.add_entity(entity)

        self.assertIs(eden.eden_state, state)
        self.assertEqual(state.entities, [entity])
        self.assertEqual(
            universe.world["eden"]["eden_state"]["entities"],
            [entity],
        )

    def test_tick_mutates_same_state_object(self):
        universe, eden = self._eden()
        state = eden.eden_state

        eden.tick()

        self.assertIs(eden.eden_state, state)
        self.assertEqual(state.tick_count, 1)
        self.assertEqual(state.day, 1)
        self.assertEqual(
            universe.world["eden"]["eden_state"]["day"],
            1,
        )

    def test_creation_days_keep_live_world_collections(self):
        universe, eden = self._eden()

        eden.tick()
        eden.tick()
        eden.tick()

        self.assertIs(
            universe.world["eden_plants"],
            eden.eden_state.plants,
        )
        self.assertIs(
            universe.world["eden_trees"],
            eden.eden_state.trees,
        )
        self.assertIs(
            universe.world["eden_animals"],
            eden.eden_state.animals,
        )
        self.assertIs(
            universe.world["eden_entities"],
            eden.eden_state.entities,
        )

    def test_public_state_snapshot_is_detached(self):
        _, eden = self._eden()
        snapshot = eden.public_state["eden_state"]

        snapshot["permissions"]["can_modify"].append(
            "serpent"
        )
        snapshot["entities"].append("changed")

        self.assertEqual(
            eden.eden_state.permissions["can_modify"],
            ["god"],
        )
        self.assertEqual(eden.eden_state.entities, [])

    def test_to_dict_is_detached_boundary(self):
        state = EdenState()
        snapshot = state.to_dict()

        snapshot["permissions"]["can_administer"].append(
            "serpent"
        )
        snapshot["animals"].append("changed")

        self.assertEqual(
            state.permissions["can_administer"],
            ["god"],
        )
        self.assertEqual(state.animals, [])


if __name__ == "__main__":
    unittest.main()
