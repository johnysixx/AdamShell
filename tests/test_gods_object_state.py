import unittest

from gods.gods import Gods
from gods.gods_state import GodsState
from universe.universe import Universe


class GodsObjectStateTests(unittest.TestCase):

    def _layer(self):
        universe = Universe()
        gods = Gods(universe)

        return universe, gods

    def test_state_is_object_only(self):
        state = GodsState()

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
            _ = state["status"]

    def test_initial_values_are_preserved(self):
        _, gods = self._layer()
        state = gods.gods_state

        self.assertIs(gods.state, state)
        self.assertEqual(state.layer_type, "entity_layer")
        self.assertEqual(state.status, "created")
        self.assertEqual(state.gods, [])
        self.assertEqual(state.events, [])
        self.assertEqual(state.tick_count, 0)
        self.assertEqual(
            state.permissions,
            {
                "can_create": True,
                "can_administer": True,
                "can_modify": True,
            },
        )

    def test_values_are_owned_by_same_state_object(self):
        _, gods = self._layer()
        state = gods.gods_state

        self.assertIs(gods.gods, state.gods)
        self.assertIs(gods.events, state.events)
        self.assertIs(gods.permissions, state.permissions)

    def test_world_keeps_object_and_dict_boundaries(self):
        universe, gods = self._layer()

        self.assertIs(
            universe.world["gods_state"],
            gods.gods_state,
        )
        self.assertIsInstance(
            universe.world["gods"],
            dict,
        )
        self.assertIsInstance(
            universe.world["gods"]["gods_state"],
            dict,
        )

    def test_public_registries_remain_live_boundaries(self):
        universe, gods = self._layer()
        boundary = universe.world["gods"]

        self.assertIs(boundary["gods"], gods.gods)
        self.assertIs(
            boundary["permissions"],
            gods.permissions,
        )

    def test_god_creation_mutates_same_state_object(self):
        universe, gods = self._layer()
        state = gods.gods_state

        god = gods.create_god(
            name="god",
            role="creator_entity",
        )

        self.assertIs(gods.gods_state, state)
        self.assertEqual(state.gods, [god])
        self.assertIs(
            universe.world["gods"]["gods"],
            state.gods,
        )
        self.assertEqual(
            universe.world["gods"]["gods_state"]["gods"],
            [god],
        )

    def test_events_and_tick_mutate_same_state_object(self):
        universe, gods = self._layer()
        state = gods.gods_state
        event = {
            "name": "god_seen",
        }

        gods.emit_event(event)

        self.assertEqual(state.events, [event])
        self.assertEqual(
            universe.world["gods"]["gods_state"]["events"],
            [event],
        )

        gods.tick()

        self.assertIs(gods.gods_state, state)
        self.assertEqual(state.tick_count, 1)
        self.assertEqual(state.events, [])
        self.assertEqual(
            universe.world["gods"]["gods_state"]["tick_count"],
            1,
        )

    def test_public_state_snapshot_is_detached(self):
        _, gods = self._layer()
        snapshot = gods.public_state["gods_state"]

        snapshot["events"].append(
            {"name": "changed"}
        )
        snapshot["permissions"]["can_create"] = False
        snapshot["gods"].append(
            {"name": "changed"}
        )

        self.assertEqual(gods.events, [])
        self.assertTrue(
            gods.permissions["can_create"]
        )
        self.assertEqual(gods.gods, [])

    def test_to_dict_returns_detached_values(self):
        state = GodsState()
        snapshot = state.to_dict()

        snapshot["events"].append(
            {"name": "changed"}
        )
        snapshot["permissions"]["can_create"] = False
        snapshot["gods"].append(
            {"name": "changed"}
        )

        self.assertEqual(state.events, [])
        self.assertTrue(
            state.permissions["can_create"]
        )
        self.assertEqual(state.gods, [])


if __name__ == "__main__":
    unittest.main()
