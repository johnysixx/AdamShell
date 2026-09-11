import unittest

from multiverse import UniverseRegistry
from root_universe import RootUniverse
from root_universe.root_universe_state import RootUniverseState
from universe.universe import Universe


class RootUniverseObjectStateTests(unittest.TestCase):

    def _root_universe(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        root_universe = RootUniverse(universe)

        return universe, root_universe

    def test_state_is_object_only(self):
        state = RootUniverseState()

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
            _ = state["history_started"]

    def test_initial_values_are_preserved(self):
        _, root_universe = self._root_universe()
        state = root_universe.root_universe_state

        self.assertIs(root_universe.state, state)
        self.assertEqual(state.status, "created")
        self.assertEqual(state.creator, "god")
        self.assertEqual(state.administrator, "god")
        self.assertTrue(state.part_of_physics)
        self.assertFalse(state.history_started)
        self.assertTrue(state.awaiting_adam_and_eve)
        self.assertEqual(state.eden_influence, [])
        self.assertEqual(state.history, [])
        self.assertEqual(state.events, [])
        self.assertEqual(state.tick_count, 0)

    def test_permissions_remain_collection_boundaries(self):
        _, root_universe = self._root_universe()
        state = root_universe.root_universe_state

        self.assertIsInstance(state.access, dict)
        self.assertIsInstance(state.permissions, dict)
        self.assertIsInstance(state.eden, dict)
        self.assertIsInstance(state.eden_influence, list)
        self.assertIsInstance(state.history, list)
        self.assertTrue(root_universe.can_read("serpent"))
        self.assertTrue(root_universe.can_modify("god"))
        self.assertFalse(root_universe.can_modify("serpent"))

    def test_world_stores_object_and_dict_boundaries(self):
        universe, root_universe = self._root_universe()

        self.assertIs(
            universe.world["root_universe_state"],
            root_universe.root_universe_state,
        )
        self.assertIsInstance(
            universe.world["root_universe"],
            dict,
        )
        self.assertIsInstance(
            universe.physics["root_universe"],
            dict,
        )
        self.assertIs(
            universe.world["root_universe"],
            universe.physics["root_universe"],
        )

    def test_eden_influence_mutates_same_state_object(self):
        universe, root_universe = self._root_universe()
        state = root_universe.root_universe_state
        influence = {"event": "eden_opened"}

        root_universe.apply_eden_influence(
            "god",
            influence,
        )

        self.assertIs(root_universe.root_universe_state, state)
        self.assertEqual(state.eden_influence, [influence])
        self.assertEqual(
            universe.world["root_universe"][
                "eden_influence"
            ],
            [influence],
        )

    def test_denied_influence_does_not_mutate_state(self):
        _, root_universe = self._root_universe()
        state = root_universe.root_universe_state

        result = root_universe.apply_eden_influence(
            "serpent",
            {"event": "forbidden_change"},
        )

        self.assertIsNone(result)
        self.assertEqual(state.eden_influence, [])

    def test_history_start_mutates_same_state_object(self):
        universe, root_universe = self._root_universe()
        state = root_universe.root_universe_state

        root_universe.start_history("god")

        self.assertIs(root_universe.root_universe_state, state)
        self.assertTrue(state.history_started)
        self.assertFalse(state.awaiting_adam_and_eve)
        self.assertTrue(
            universe.world["root_universe"][
                "history_started"
            ]
        )

    def test_events_and_tick_mutate_same_state_object(self):
        _, root_universe = self._root_universe()
        state = root_universe.root_universe_state

        root_universe.emit_event("event")

        self.assertEqual(state.events, ["event"])

        root_universe.tick()

        self.assertIs(root_universe.root_universe_state, state)
        self.assertEqual(state.tick_count, 1)
        self.assertEqual(state.events, [])

    def test_public_state_is_deeply_detached(self):
        _, root_universe = self._root_universe()
        state = root_universe.root_universe_state

        public_state = root_universe.public_state
        public_state["permissions"]["can_modify"].append(
            "serpent"
        )
        public_state["root_universe_state"][
            "eden_influence"
        ].append({"event": "changed"})

        self.assertEqual(state.permissions["can_modify"], ["god"])
        self.assertEqual(state.eden_influence, [])

    def test_to_dict_is_deeply_detached(self):
        state = RootUniverseState()

        snapshot = state.to_dict()
        snapshot["permissions"]["can_modify"].append(
            "serpent"
        )
        snapshot["history"].append("changed")

        self.assertEqual(state.permissions["can_modify"], ["god"])
        self.assertEqual(state.history, [])


if __name__ == "__main__":
    unittest.main()
