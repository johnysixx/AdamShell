import unittest
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace

from idea_entities import IdeaEntities
from idea_entities.idea_entities_state import (
    IdeaEntitiesPermissions,
    IdeaEntitiesState,
)
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
        self.assertIsInstance(
            state.permissions,
            IdeaEntitiesPermissions,
        )
        self.assertTrue(
            state.permissions.can_exist_before_form
        )
        self.assertTrue(
            state.permissions.can_influence
        )
        self.assertTrue(
            state.permissions.can_become_process
        )

    def test_values_are_owned_by_same_state_object(self):
        _, layer = self._layer()
        state = layer.idea_entities_state

        self.assertIs(layer.idea_entities, state.idea_entities)
        self.assertIs(layer.eternal_fire, state.eternal_fire)
        self.assertIs(layer.events, state.events)
        self.assertIs(layer.event_history, state.event_history)
        self.assertIs(layer.permissions, state.permissions)

    def test_world_exposes_export_not_canonical_state(self):
        universe, layer = self._layer()

        self.assertNotIn(
            "idea_entities_state",
            universe.world,
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

    def test_public_collections_are_detached(self):
        universe, layer = self._layer()

        event = IdeaEntityEvent(
            name="boundary_event",
            participants=("serpent",),
        )

        layer.emit_event(event)
        boundary = universe.world["idea_entities"]

        self.assertIsNot(
            boundary["idea_entities"],
            layer.idea_entities,
        )
        self.assertIsNot(
            boundary["events"],
            layer.events,
        )
        self.assertIsNot(
            boundary["event_history"],
            layer.event_history,
        )

        self.assertEqual(
            boundary["events"],
            [event.to_dict()],
        )
        self.assertEqual(
            boundary["event_history"],
            [event.to_dict()],
        )

        self.assertEqual(
            boundary["permissions"],
            layer.permissions.to_dict(),
        )

        boundary["permissions"]["can_influence"] = False
        self.assertTrue(layer.permissions.can_influence)

        self.assertNotIn(
            "idea_entities_state",
            universe.world,
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
        self.assertIsNot(
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
        self.assertEqual(
            universe.world["idea_entities"]["events"][-1],
            event.to_dict(),
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
        public = layer.public_state["permissions"]

        snapshot["events"].append("changed")
        snapshot["permissions"]["can_influence"] = False
        snapshot["eternal_fire"]["state"] = "changed"
        public["can_influence"] = False

        self.assertEqual(layer.events, [])
        self.assertTrue(
            layer.permissions.can_influence
        )
        self.assertTrue(
            layer.public_state["permissions"][
                "can_influence"
            ]
        )
        self.assertIs(
            layer.eternal_fire.state,
            EternalFirePotentialState.UNIGNITED,
        )

    def test_nested_permissions_snapshot_is_detached(self):
        state = IdeaEntitiesState()

        first = state.to_dict()
        second = state.to_dict()

        first["permissions"]["can_influence"] = False

        self.assertTrue(
            state.permissions.can_influence
        )
        self.assertTrue(
            second["permissions"]["can_influence"]
        )
        self.assertTrue(
            state.to_dict()["permissions"]["can_influence"]
        )

        self.assertIsNot(
            first["permissions"],
            second["permissions"],
        )

    def test_permissions_snapshot_ignores_later_live_changes(self):
        state = IdeaEntitiesState()
        original = state.permissions

        snapshot = state.to_dict()

        state.permissions = replace(
            original,
            can_influence=False,
        )

        self.assertIsNot(
            state.permissions,
            original,
        )
        self.assertTrue(
            original.can_influence
        )
        self.assertFalse(
            state.permissions.can_influence
        )

        self.assertTrue(
            snapshot["permissions"]["can_influence"]
        )
        self.assertFalse(
            state.to_dict()["permissions"]["can_influence"]
        )

    def test_live_permissions_identity_is_preserved(self):
        universe, layer = self._layer()
        state = layer.idea_entities_state

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
        self.assertIsInstance(
            entity.permissions,
            IdeaEntitiesPermissions,
        )

        boundary = universe.world[
            "idea_entities"
        ]["permissions"]

        self.assertEqual(
            boundary,
            state.permissions.to_dict(),
        )
        self.assertIsNot(
            boundary,
            state.permissions,
        )

        boundary["can_influence"] = False

        self.assertTrue(
            entity.permissions.can_influence
        )
        self.assertTrue(
            state.permissions.can_influence
        )
        self.assertIs(
            layer.idea_entities_state,
            state,
        )

    def test_permissions_reject_mapping_runtime_state(self):
        with self.assertRaises(TypeError):
            IdeaEntitiesState(permissions={})

        state = IdeaEntitiesState()
        original = state.permissions

        with self.assertRaises(TypeError):
            state.permissions = {
                "can_influence": True,
            }

        self.assertIs(
            state.permissions,
            original,
        )

        with self.assertRaises(TypeError):
            IdeaEntitiesPermissions(can_influence=1)

    def test_permissions_have_no_mapping_api_and_are_frozen(self):
        permissions = IdeaEntitiesPermissions()

        for method in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
        ):
            self.assertFalse(
                hasattr(permissions, method)
            )

        with self.assertRaises(TypeError):
            _ = permissions["can_influence"]

        with self.assertRaises(FrozenInstanceError):
            permissions.can_influence = False

        changed = replace(
            permissions,
            can_influence=False,
        )

        self.assertTrue(
            permissions.can_influence
        )
        self.assertFalse(
            changed.can_influence
        )
        self.assertIsNot(
            changed,
            permissions,
        )

    def test_world_permission_boundary_tracks_object_replacement(self):
        universe, layer = self._layer()

        state = layer.idea_entities_state
        original = state.permissions

        before = universe.world[
            "idea_entities"
        ]["permissions"]

        state.permissions = replace(
            original,
            can_influence=False,
        )

        layer.write_to_world()

        after = universe.world[
            "idea_entities"
        ]["permissions"]

        self.assertIs(
            layer.permissions,
            state.permissions,
        )

        self.assertTrue(
            original.can_influence
        )
        self.assertTrue(
            before["can_influence"]
        )
        self.assertFalse(
            state.permissions.can_influence
        )
        self.assertFalse(
            after["can_influence"]
        )

        after["can_influence"] = True

        self.assertFalse(
            layer.permissions.can_influence
        )
        self.assertFalse(
            layer.public_state["permissions"][
                "can_influence"
            ]
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

        self.assertEqual(
            universe.world["idea_entities"]["events"][-1],
            event.to_dict(),
        )

        self.assertEqual(
            universe.world["idea_entities"][
                "event_history"
            ][-1],
            event.to_dict(),
        )

        self.assertNotIn(
            "idea_entities_state",
            universe.world,
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
        self.assertTrue(state.permissions.can_influence)
        self.assertIs(
            state.eternal_fire.state,
            EternalFirePotentialState.UNIGNITED,
        )



    def test_world_events_cannot_bypass_emitter(self):
        universe, layer = self._layer()

        event = IdeaEntityEvent(
            name="legitimate_event",
            participants=("serpent",),
        )

        layer.emit_event(event)

        boundary = universe.world["idea_entities"]

        boundary["events"].append(
            {"name": "invalid_event"}
        )
        boundary["event_history"].append(
            {"name": "invalid_history"}
        )

        self.assertEqual(layer.events, [event])
        self.assertEqual(layer.event_history, [event])

        self.assertEqual(
            universe.world["idea_entities"][
                "idea_entities_state"
            ]["events"],
            [event.to_dict()],
        )

    def test_world_event_payloads_are_detached(self):
        universe, layer = self._layer()

        event = IdeaEntityEvent(
            name="immutable_source",
            participants=("serpent",),
        )

        layer.emit_event(event)

        boundary = universe.world["idea_entities"]

        boundary["events"][0]["participants"].append(
            "intruder"
        )
        boundary["event_history"][0]["participants"].append(
            "intruder"
        )

        self.assertEqual(
            event.participants,
            ("serpent",),
        )

        self.assertIs(layer.events[0], event)
        self.assertIs(layer.event_history[0], event)

        self.assertEqual(
            layer.public_state["events"][0]["participants"],
            ["serpent"],
        )

    def test_world_projection_has_snapshot_semantics(self):
        universe, layer = self._layer()

        old_view = universe.world["idea_entities"]

        self.assertEqual(
            old_view["idea_entities_state"]["tick_count"],
            0,
        )

        layer.tick()

        new_view = universe.world["idea_entities"]

        self.assertIsNot(old_view, new_view)
        self.assertEqual(
            old_view["idea_entities_state"]["tick_count"],
            0,
        )
        self.assertEqual(
            new_view["idea_entities_state"]["tick_count"],
            1,
        )
        self.assertEqual(layer.tick_count, 1)



    def test_world_alias_stays_absent_during_lifecycle(self):
        universe, layer = self._layer()
        canonical = layer.idea_entities_state

        self.assertNotIn(
            "idea_entities_state",
            universe.world,
        )

        entity = layer.create_idea_entity(
            name="a05_entity",
        )

        event = layer.record_idea_event(
            name="a05_event",
            participants=("a05_entity",),
        )

        layer.tick()

        self.assertIs(
            layer.idea_entities_state,
            canonical,
        )
        self.assertIs(
            layer.state,
            canonical,
        )

        self.assertIn(entity, canonical.idea_entities)
        self.assertIn(event, canonical.event_history)
        self.assertEqual(canonical.tick_count, 1)

        self.assertNotIn(
            "idea_entities_state",
            universe.world,
        )

        exported = universe.world[
            "idea_entities"
        ]["idea_entities_state"]

        self.assertIsInstance(exported, dict)
        self.assertIsNot(exported, canonical)
        self.assertEqual(exported["tick_count"], 1)

        exported["tick_count"] = 999
        exported["event_history"].clear()

        self.assertEqual(canonical.tick_count, 1)
        self.assertEqual(
            canonical.event_history,
            [event],
        )

    def test_refresh_removes_legacy_world_alias(self):
        universe, layer = self._layer()
        canonical = layer.idea_entities_state

        # Simulate an old integration retaining the
        # pre-A05 registry entry.
        universe.world["idea_entities_state"] = canonical

        self.assertIs(
            universe.world["idea_entities_state"],
            canonical,
        )

        layer.write_to_world()

        self.assertNotIn(
            "idea_entities_state",
            universe.world,
        )

        self.assertIs(layer.idea_entities_state, canonical)

        self.assertIsInstance(
            universe.world["idea_entities"][
                "idea_entities_state"
            ],
            dict,
        )

    def test_fire_interaction_keeps_world_alias_absent(self):
        universe, layer = self._layer()
        canonical = layer.idea_entities_state
        fire = layer.eternal_fire

        event = layer.record_fire_interaction(
            name="a05_fire_observed",
            participants=("serpent",),
            observer="lilith",
        )

        self.assertIs(layer.idea_entities_state, canonical)
        self.assertIs(layer.eternal_fire, fire)

        self.assertIs(fire.interactions[-1], event)
        self.assertIs(layer.event_history[-1], event)

        self.assertNotIn(
            "idea_entities_state",
            universe.world,
        )

        exported = universe.world["idea_entities"]

        self.assertEqual(
            exported["eternal_fire"]["interactions"][-1],
            event.to_dict(),
        )

        self.assertEqual(
            exported["idea_entities_state"]["event_history"][-1],
            event.to_dict(),
        )


if __name__ == "__main__":
    unittest.main()
