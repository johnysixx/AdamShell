import unittest

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
        ] = {
            "name": "pazuzu",
            "type": "idea_entity",
            "energy_j": 100.0,
        }

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

        self.assertEqual(
            result["name"],
            event.name,
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

        result[
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
