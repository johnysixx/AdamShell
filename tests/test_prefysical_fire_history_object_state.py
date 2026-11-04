import unittest
from types import SimpleNamespace
from core.entity.social_entity import SocialEntity

from idea_entities import IdeaEntities
from idea_entities.prefysical_fire_origin import (
    PrefysicalFireEvent,
)
from universe.universe import Universe


class PrefysicalFireHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()

        self.idea_entities = IdeaEntities(
            self.universe
        )

        self.universe.world[
            "pazuzu_masculine_principle"
        ] = SocialEntity(
            name="pazuzu",
            type="idea_entity",
            energy_j=100.0,
        )

        self.origin = (
            self.idea_entities
            .prefysical_fire_origin
        )

    def test_history_uses_object_state(
        self
    ):
        result = self.origin.begin()

        event = (
            self.origin
            .history[-1]
        )

        self.assertIsInstance(
            event,
            PrefysicalFireEvent,
        )

        self.assertEqual(
            event.name,
            "prefysical_fire_origin_started",
        )

        self.assertEqual(
            event.participants,
            tuple(
                self.origin.participants
            ),
        )

        self.assertIs(
            result,
            event,
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

        with self.assertRaises(
            TypeError
        ):
            _ = event["name"]

    def test_details_are_read_only_and_boundary_is_detached(
        self
    ):
        result = self.origin.begin()

        event = (
            self.origin
            .history[-1]
        )

        with self.assertRaises(
            TypeError
        ):
            event.details[
                "temperature_state"
            ] = "changed"

        with self.assertRaises(
            TypeError
        ):
            event.details[
                "materials"
            ][
                "handed_to"
            ] = "changed"

        self.assertIs(
            result,
            event,
        )

        snapshot = result.to_dict()

        snapshot[
            "details"
        ][
            "materials"
        ][
            "handed_to"
        ] = "changed"

        self.assertEqual(
            event.details[
                "materials"
            ][
                "handed_to"
            ],
            "pazuzu_masculine_principle",
        )

    def test_public_state_keeps_detached_dict_history_boundary(
        self
    ):
        self.origin.begin()

        event = (
            self.origin
            .history[-1]
        )

        public_state = (
            self.origin.public_state
        )

        history = (
            public_state[
                "history"
            ]
        )

        self.assertIsInstance(
            history,
            list,
        )

        self.assertIsInstance(
            history[0],
            dict,
        )

        self.assertIsInstance(
            history[0][
                "details"
            ],
            dict,
        )

        history[0][
            "details"
        ][
            "temperature_state"
        ] = "changed"

        self.assertEqual(
            event.details[
                "temperature_state"
            ],
            "freezing",
        )

    def test_history_snapshot_detaches_nested_object(self):
        payload = SimpleNamespace(
            notes=["original"],
        )

        event = PrefysicalFireEvent(
            name="nested_history_test",
            layer="prefysical_fire",
            logical_step=1,
            participants=("serpent",),
            details={
                "metadata": payload,
            },
        )

        self.origin.record_event(event)

        first = self.origin.public_state
        second = self.origin.public_state

        first["history"][0]["details"][
            "metadata"
        ].notes.append("snapshot_only")

        self.assertEqual(
            payload.notes,
            ["original"],
        )

        self.assertEqual(
            second["history"][0]["details"][
                "metadata"
            ].notes,
            ["original"],
        )

        self.assertEqual(
            self.origin.public_state["history"][0][
                "details"
            ]["metadata"].notes,
            ["original"],
        )

        self.assertIs(
            self.origin.history[0],
            event,
        )

        self.assertIs(
            event.details["metadata"],
            payload,
        )

        self.assertIsNot(
            first["history"][0]["details"][
                "metadata"
            ],
            payload,
        )

    def test_history_snapshot_ignores_later_live_changes(self):
        payload = SimpleNamespace(
            metadata={
                "notes": ["original"],
            },
        )

        event = PrefysicalFireEvent(
            name="history_change_test",
            layer="prefysical_fire",
            logical_step=1,
            participants=("lilith",),
            details={
                "payload": payload,
            },
        )

        self.origin.record_event(event)

        snapshot = self.origin.public_state

        payload.metadata["notes"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot["history"][0]["details"][
                "payload"
            ].metadata["notes"],
            ["original"],
        )

        current = self.origin.public_state

        self.assertEqual(
            current["history"][0]["details"][
                "payload"
            ].metadata["notes"],
            ["original", "live_change"],
        )

        snapshot["history"].clear()

        self.assertEqual(
            len(self.origin.history),
            1,
        )

        self.assertIs(
            self.origin.history[0],
            event,
        )

        self.assertIs(
            event.details["payload"],
            payload,
        )

    def test_world_history_snapshot_preserves_event_identity(self):
        payload = SimpleNamespace(
            notes=["original"],
        )

        event = PrefysicalFireEvent(
            name="world_history_test",
            layer="prefysical_fire",
            logical_step=1,
            participants=("serpent", "lilith"),
            details={
                "metadata": payload,
            },
        )

        self.origin.record_event(event)
        self.idea_entities.write_to_world()

        world_snapshot = self.universe.world[
            "idea_entities"
        ]["prefysical_fire_origin"]

        public_snapshot = self.idea_entities.public_state[
            "prefysical_fire_origin"
        ]

        origin_snapshot = self.origin.public_state

        self.assertIs(
            self.idea_entities.prefysical_fire_origin,
            self.origin,
        )

        self.assertIs(
            self.origin.history[0],
            event,
        )

        self.assertIs(
            event.details["metadata"],
            payload,
        )

        world_snapshot["history"][0]["details"][
            "metadata"
        ].notes.append("snapshot_only")

        self.assertEqual(
            payload.notes,
            ["original"],
        )

        for snapshot in (
            public_snapshot,
            origin_snapshot,
        ):
            self.assertEqual(
                snapshot["history"][0]["details"][
                    "metadata"
                ].notes,
                ["original"],
            )

        payload.notes.append(
            "live_change"
        )

        self.assertEqual(
            public_snapshot["history"][0][
                "details"
            ]["metadata"].notes,
            ["original"],
        )

        self.assertEqual(
            origin_snapshot["history"][0][
                "details"
            ]["metadata"].notes,
            ["original"],
        )

        current = self.idea_entities.public_state[
            "prefysical_fire_origin"
        ]

        self.assertEqual(
            current["history"][0]["details"][
                "metadata"
            ].notes,
            ["original", "live_change"],
        )

        self.assertIs(
            self.origin.history[0],
            event,
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            self.origin.record_event(
                {
                    "name": (
                        "prefysical_fire_origin_started"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
