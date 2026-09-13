import unittest

from idea_entities import IdeaEntities
from idea_entities.idea_entities_state import IdeaEntitiesState
from universe.universe import Universe


class IdeaEntitiesObjectStateTests(unittest.TestCase):

    def _layer(self):
        universe = Universe()
        layer = IdeaEntities(universe)

        return universe, layer

    def test_state_is_object_only(self):
        state = IdeaEntitiesState()

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
            _ = state["tick_count"]

    def test_initial_values_are_preserved(self):
        _, layer = self._layer()
        state = layer.idea_entities_state

        self.assertIs(layer.state, state)
        self.assertEqual(state.layer_type, "entity_layer")
        self.assertEqual(state.status, "created")
        self.assertEqual(state.idea_entities, [])
        self.assertEqual(state.events, [])
        self.assertEqual(state.event_history, [])
        self.assertEqual(state.tick_count, 0)
        self.assertEqual(
            state.permissions,
            {
                "can_exist_before_form": True,
                "can_influence": True,
                "can_become_process": True,
            },
        )

    def test_values_are_owned_by_same_state_object(self):
        _, layer = self._layer()
        state = layer.idea_entities_state

        self.assertIs(layer.idea_entities, state.idea_entities)
        self.assertIs(layer.eternal_fire, state.eternal_fire)
        self.assertIs(layer.events, state.events)
        self.assertIs(layer.event_history, state.event_history)
        self.assertIs(layer.permissions, state.permissions)

    def test_world_keeps_object_and_dict_boundaries(self):
        universe, layer = self._layer()

        self.assertIs(
            universe.world["idea_entities_state"],
            layer.idea_entities_state,
        )
        self.assertIsInstance(
            universe.world["idea_entities"],
            dict,
        )
        self.assertIsInstance(
            universe.world["idea_entities"][
                "idea_entities_state"
            ],
            dict,
        )
        self.assertIsInstance(
            universe.world["idea_entities"]["eternal_fire"],
            dict,
        )

    def test_public_registries_remain_live_boundaries(self):
        universe, layer = self._layer()
        boundary = universe.world["idea_entities"]

        self.assertIs(
            boundary["idea_entities"],
            layer.idea_entities,
        )
        self.assertIs(boundary["events"], layer.events)
        self.assertIs(
            boundary["event_history"],
            layer.event_history,
        )
        self.assertIs(
            boundary["permissions"],
            layer.permissions,
        )

    def test_entity_creation_mutates_same_state_object(self):
        universe, layer = self._layer()
        state = layer.idea_entities_state

        entity = layer.create_idea_entity(
            name="serpent",
            active=True,
            existence_pct=100.0,
        )

        self.assertIs(layer.idea_entities_state, state)
        self.assertEqual(state.idea_entities, [entity])
        self.assertIs(
            universe.world["idea_entities"][
                "idea_entities"
            ],
            state.idea_entities,
        )
        self.assertEqual(
            universe.world["idea_entities"][
                "idea_entities_state"
            ]["idea_entities"],
            [entity],
        )

    def test_events_and_tick_mutate_same_state_object(self):
        universe, layer = self._layer()
        state = layer.idea_entities_state
        event = {"name": "idea_seen"}

        layer.emit_event(event)

        self.assertEqual(state.events, [event])
        self.assertEqual(state.event_history, [event])

        layer.tick()

        self.assertIs(layer.idea_entities_state, state)
        self.assertEqual(state.tick_count, 1)
        self.assertEqual(state.events, [])
        self.assertEqual(state.event_history, [event])
        self.assertEqual(
            universe.world["idea_entities"][
                "idea_entities_state"
            ]["tick_count"],
            1,
        )

    def test_public_state_snapshot_is_detached(self):
        _, layer = self._layer()
        snapshot = layer.public_state["idea_entities_state"]

        snapshot["events"].append("changed")
        snapshot["permissions"][
            "can_influence"
        ] = False
        snapshot["eternal_fire"]["state"] = "changed"

        self.assertEqual(layer.events, [])
        self.assertTrue(layer.permissions["can_influence"])
        self.assertEqual(
            layer.eternal_fire.state,
            "unignited",
        )

    def test_to_dict_is_deeply_detached(self):
        state = IdeaEntitiesState()
        state.events.append({"name": "event"})
        state.event_history.append({"name": "history"})

        snapshot = state.to_dict()
        snapshot["events"][0]["name"] = "changed"
        snapshot["event_history"][0]["name"] = "changed"
        snapshot["permissions"]["can_influence"] = False
        snapshot["eternal_fire"]["state"] = "changed"

        self.assertEqual(state.events[0]["name"], "event")
        self.assertEqual(
            state.event_history[0]["name"],
            "history",
        )
        self.assertTrue(state.permissions["can_influence"])
        self.assertEqual(state.eternal_fire.state, "unignited")


if __name__ == "__main__":
    unittest.main()
