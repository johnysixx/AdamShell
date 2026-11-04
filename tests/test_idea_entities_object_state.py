import unittest
from copy import deepcopy

from idea_entities import IdeaEntities
from idea_entities.idea_entities_state import IdeaEntitiesState
from idea_entities.idea_event_state import IdeaEntityEvent
from idea_entities.eternal_fire_potential_state import (
    EternalFirePotentialState,
)
from universe.universe import Universe


class MutableSerializedIdeaEvent(IdeaEntityEvent):

    def __init__(self):
        super().__init__(
            name="test_idea_event",
            participants=("serpent",),
        )
        object.__setattr__(
            self,
            "metadata",
            {
                "nested": {
                    "notes": ["original"],
                },
            },
        )

    def to_dict(self):
        snapshot = super().to_dict()
        snapshot["metadata"] = self.metadata
        return snapshot


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
        event = IdeaEntityEvent(
            name="idea_seen",
            participants=(),
        )

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

    def test_record_idea_event_keeps_object_identity(self):
        universe, layer = self._layer()

        participants = ["serpent", "lilith"]

        event = layer.record_idea_event(
            name="idea_shared",
            participants=participants,
            observer="pazuzu",
            meaning="shared knowledge",
        )

        participants.append("changed")

        self.assertIsInstance(
            event,
            IdeaEntityEvent,
        )
        self.assertEqual(
            event.participants,
            ("serpent", "lilith"),
        )
        self.assertEqual(
            event.known_by,
            ("pazuzu",),
        )
        self.assertIsNone(event.place)

        self.assertIs(layer.events[-1], event)
        self.assertIs(layer.event_history[-1], event)
        self.assertIs(
            universe.world["idea_entities"]["events"][-1],
            event,
        )
        self.assertIs(deepcopy(event), event)

        snapshot = layer.idea_entities_state.to_dict()

        self.assertEqual(
            snapshot["events"][0],
            event.to_dict(),
        )

        snapshot["events"][0]["known_by"].append(
            "intruder"
        )
        snapshot["event_history"][0][
            "participants"
        ][0] = "changed"

        self.assertEqual(
            event.known_by,
            ("pazuzu",),
        )
        self.assertEqual(
            event.participants,
            ("serpent", "lilith"),
        )

        layer.tick()

        self.assertEqual(layer.events, [])
        self.assertIs(
            layer.event_history[-1],
            event,
        )

    def test_emit_event_rejects_mapping(self):
        _, layer = self._layer()

        with self.assertRaises(TypeError):
            layer.emit_event({
                "name": "invalid",
                "layer": "idea_entities",
            })

        self.assertEqual(layer.events, [])
        self.assertEqual(layer.event_history, [])

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
        self.assertIs(
            layer.eternal_fire.state,
            EternalFirePotentialState.UNIGNITED,
        )

    def test_nested_permissions_snapshot_is_detached(self):
        state = IdeaEntitiesState()

        state.permissions["nested"] = {
            "allowed": ["create"],
        }

        first = state.to_dict()
        second = state.to_dict()

        first["permissions"]["nested"][
            "allowed"
        ].append("snapshot_only")

        self.assertEqual(
            state.permissions["nested"]["allowed"],
            ["create"],
        )

        self.assertEqual(
            second["permissions"]["nested"][
                "allowed"
            ],
            ["create"],
        )

        self.assertEqual(
            state.to_dict()["permissions"][
                "nested"
            ]["allowed"],
            ["create"],
        )

        self.assertIsNot(
            first["permissions"]["nested"],
            state.permissions["nested"],
        )

    def test_permissions_snapshot_ignores_later_live_changes(self):
        state = IdeaEntitiesState()

        state.permissions["nested"] = {
            "allowed": ["create"],
        }

        snapshot = state.to_dict()

        state.permissions["nested"][
            "allowed"
        ].append("influence")

        self.assertEqual(
            snapshot["permissions"]["nested"][
                "allowed"
            ],
            ["create"],
        )

        self.assertEqual(
            state.to_dict()["permissions"][
                "nested"
            ]["allowed"],
            ["create", "influence"],
        )

        self.assertTrue(
            snapshot["permissions"]["can_influence"],
        )

    def test_live_permissions_identity_is_preserved(self):
        universe, layer = self._layer()

        state = layer.idea_entities_state

        state.permissions["nested"] = {
            "roles": ["observer"],
        }

        entity = layer.create_idea_entity(
            name="permission_test",
        )

        self.assertIs(
            layer.permissions,
            state.permissions,
        )

        self.assertIs(
            entity.permissions,
            state.permissions,
        )

        self.assertIs(
            universe.world["idea_entities"][
                "permissions"
            ],
            state.permissions,
        )

        snapshot = state.to_dict()

        snapshot["permissions"]["nested"][
            "roles"
        ].append("intruder")

        self.assertEqual(
            state.permissions["nested"]["roles"],
            ["observer"],
        )

        self.assertEqual(
            entity.permissions["nested"]["roles"],
            ["observer"],
        )

        self.assertIs(
            layer.idea_entities_state,
            state,
        )

    def test_event_snapshots_detach_nested_serialized_data(self):
        event = MutableSerializedIdeaEvent()

        state = IdeaEntitiesState(
            events=[event],
            event_history=[event],
        )

        first = state.to_dict()
        second = state.to_dict()

        first["events"][0]["metadata"][
            "nested"
        ]["notes"].append("snapshot_only")

        first["event_history"][0]["metadata"][
            "nested"
        ]["notes"].append("history_only")

        self.assertEqual(
            event.metadata["nested"]["notes"],
            ["original"],
        )

        for collection in ("events", "event_history"):
            self.assertEqual(
                second[collection][0]["metadata"][
                    "nested"
                ]["notes"],
                ["original"],
            )

            self.assertEqual(
                state.to_dict()[collection][0][
                    "metadata"
                ]["nested"]["notes"],
                ["original"],
            )

        self.assertIs(state.events[0], event)
        self.assertIs(state.event_history[0], event)

        self.assertIsNot(
            first["events"][0]["metadata"],
            event.metadata,
        )

        self.assertIsNot(
            first["event_history"][0]["metadata"],
            event.metadata,
        )

    def test_event_snapshots_ignore_later_live_changes(self):
        event = MutableSerializedIdeaEvent()

        state = IdeaEntitiesState(
            events=[event],
            event_history=[event],
        )

        snapshot = state.to_dict()

        event.metadata["nested"]["notes"].append(
            "live_change"
        )

        for collection in ("events", "event_history"):
            self.assertEqual(
                snapshot[collection][0]["metadata"][
                    "nested"
                ]["notes"],
                ["original"],
            )

            self.assertEqual(
                state.to_dict()[collection][0][
                    "metadata"
                ]["nested"]["notes"],
                ["original", "live_change"],
            )

        snapshot["events"].clear()
        snapshot["event_history"].clear()

        self.assertEqual(len(state.events), 1)
        self.assertEqual(len(state.event_history), 1)

        self.assertIs(state.events[0], event)
        self.assertIs(state.event_history[0], event)

    def test_world_event_snapshots_preserve_live_identity(self):
        universe, layer = self._layer()
        event = MutableSerializedIdeaEvent()

        layer.emit_event(event)

        self.assertIs(layer.events[-1], event)
        self.assertIs(layer.event_history[-1], event)

        self.assertIs(
            universe.world["idea_entities"]["events"][-1],
            event,
        )

        self.assertIs(
            universe.world["idea_entities"][
                "event_history"
            ][-1],
            event,
        )

        self.assertIs(
            universe.world["idea_entities_state"],
            layer.idea_entities_state,
        )

        world_snapshot = universe.world[
            "idea_entities"
        ]["idea_entities_state"]

        public_snapshot = layer.public_state[
            "idea_entities_state"
        ]

        world_snapshot["events"][0]["metadata"][
            "nested"
        ]["notes"].append("snapshot_only")

        world_snapshot["event_history"][0][
            "metadata"
        ]["nested"]["notes"].append("history_only")

        self.assertEqual(
            event.metadata["nested"]["notes"],
            ["original"],
        )

        for collection in ("events", "event_history"):
            self.assertEqual(
                public_snapshot[collection][0][
                    "metadata"
                ]["nested"]["notes"],
                ["original"],
            )

        event.metadata["nested"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            public_snapshot["events"][0]["metadata"][
                "nested"
            ]["notes"],
            ["original"],
        )

        current = layer.public_state[
            "idea_entities_state"
        ]

        for collection in ("events", "event_history"):
            self.assertEqual(
                current[collection][0]["metadata"][
                    "nested"
                ]["notes"],
                ["original", "live_change"],
            )

        self.assertIs(layer.events[-1], event)
        self.assertIs(layer.event_history[-1], event)

    def test_to_dict_is_deeply_detached(self):
        state = IdeaEntitiesState()
        state.events.append(
            IdeaEntityEvent(
                name="event",
                participants=(),
            )
        )
        state.event_history.append(
            IdeaEntityEvent(
                name="history",
                participants=(),
            )
        )

        snapshot = state.to_dict()
        snapshot["events"][0]["name"] = "changed"
        snapshot["event_history"][0]["name"] = "changed"
        snapshot["permissions"]["can_influence"] = False
        snapshot["eternal_fire"]["state"] = "changed"

        self.assertEqual(state.events[0].name, "event")
        self.assertEqual(
            state.event_history[0].name,
            "history",
        )
        self.assertTrue(state.permissions["can_influence"])
        self.assertIs(
            state.eternal_fire.state,
            EternalFirePotentialState.UNIGNITED,
        )


if __name__ == "__main__":
    unittest.main()
