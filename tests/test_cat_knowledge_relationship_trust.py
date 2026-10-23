import unittest

from cats.cat_knowledge import CatKnowledge
from cats.cat_social_objects import (
    CatRelationship,
    CatRelationshipTrustEvent,
)
from core.entity.domain_object import (
    DomainObject,
)
from cats.cats import Cats
from universe.universe import Universe


class CatKnowledgeRelationshipTrustTests(
    unittest.TestCase
):

    def setUp(self):
        self.cats = Cats(
            Universe()
        )

        self.listener = self.cats.create_cat(
            name="listener",
            color="black",
            fur_length="short",
        )

        self.storyteller_name = (
            "storyteller"
        )

    def _past_event(self):
        return CatRelationshipTrustEvent(
            reason="past_meeting",
        )

    def _assert_object_only(
        self,
        event,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["reason"]

    def test_reads_and_clamps_object_relationship_trust(
        self
    ):
        relationship = (
            CatRelationship.create()
        )

        history = [
            self._past_event()
        ]

        second_relationship = (
            CatRelationship(
                trust_history=history
            )
        )

        for value, expected in (
            (0.9, 0.9),
            ("0.8", 0.8),
            (-0.2, 0.0),
            (1.2, 1.0),
        ):
            relationship.trust = value
            second_relationship.trust = (
                value
            )

            for record in (
                relationship,
                second_relationship,
            ):
                record.other_cat = self.storyteller_name
                self.listener.relationships.store(
                    record
                )
                self.assertAlmostEqual(
                    CatKnowledge._trust_in_cat(
                        self.listener,
                        self.storyteller_name,
                    ),
                    expected,
                )

                self.assertIs(
                    self.listener.relationships.record(self.storyteller_name),
                    record,
                )

            self.assertEqual(
                relationship.trust,
                value,
            )

            self.assertEqual(
                second_relationship.trust,
                value,
            )

        self.assertIs(
            second_relationship.trust_history,
            history,
        )

        self.assertIsInstance(
            history[0],
            CatRelationshipTrustEvent,
        )

        self._assert_object_only(
            history[0]
        )

        self.assertEqual(
            history[0].reason,
            "past_meeting",
        )

    def test_missing_trust_defaults_without_mutating_records(
        self
    ):
        self.assertEqual(
            CatKnowledge._trust_in_cat(
                self.listener,
                self.storyteller_name,
            ),
            0.5,
        )

        self.assertIsNone(
            self.listener.relationships.record(
                self.storyteller_name
            )
        )

        relationship = CatRelationship(
            other_cat=self.storyteller_name
        )

        self.listener.relationships.store(
            relationship
        )

        self.assertEqual(
            CatKnowledge._trust_in_cat(
                self.listener,
                self.storyteller_name,
            ),
            0.5,
        )

        self.assertIs(
            self.listener.relationships.record(
                self.storyteller_name
            ),
            relationship,
        )

        with self.assertRaises(
            TypeError
        ):
            self.listener.relationships.store(
                None
            )

    def test_adjustment_records_object_event(
        self
    ):
        relationship = (
            CatRelationship()
        )

        second_relationship = (
            CatRelationship()
        )

        for name, record in (
            (
                "object",
                relationship,
            ),
            (
                "second_relationship",
                second_relationship,
            ),
        ):
            record.other_cat = name
            self.listener.relationships.store(
                record
            )
            event = (
                CatKnowledge
                .adjust_storyteller_trust(
                    self.listener,
                    name,
                    0.1,
                    "confirmed",
                    legend_id="legend_1",
                )
            )

            self.assertIs(
                self.listener.relationships.record(name),
                record,
            )

            self.assertAlmostEqual(
                event.previous,
                0.5,
            )

            self.assertAlmostEqual(
                event.current,
                0.6,
            )

            self.assertAlmostEqual(
                event.delta,
                0.1,
            )

            self.assertEqual(
                event.reason,
                "confirmed",
            )

            self.assertEqual(
                event.legend_id,
                "legend_1",
            )

            history_event = (
                record.trust_history[-1]
            )

            self.assertIs(
                history_event,
                event,
            )

            self.assertIsInstance(
                history_event,
                CatRelationshipTrustEvent,
            )

            self._assert_object_only(
                history_event
            )

            self.assertEqual(
                history_event.reason,
                "confirmed",
            )

        self.assertAlmostEqual(
            relationship.trust,
            0.6,
        )

        self.assertAlmostEqual(
            second_relationship.trust,
            0.6,
        )

        self.assertEqual(
            relationship.trust_history,
            second_relationship.trust_history,
        )

        self.assertIsNot(
            relationship.trust_history,
            second_relationship.trust_history,
        )

    def test_adjustments_preserve_object_history_and_effective_delta(
        self
    ):
        relationship = (
            CatRelationship.create()
        )

        relationship.trust = "1.2"

        object_history = [
            self._past_event()
        ]

        relationship.trust_history = (
            object_history
        )

        second_history = [
            self._past_event()
        ]

        second_relationship = (
            CatRelationship(
                trust="1.2",
                trust_history=second_history,
            )
        )

        for name, record, history in (
            (
                "object",
                relationship,
                object_history,
            ),
            (
                "second_relationship",
                second_relationship,
                second_history,
            ),
        ):
            record.other_cat = name
            self.listener.relationships.store(
                record
            )
            previous_entry = history[0]

            for index, (
                delta,
                previous,
                current,
            ) in enumerate(
                (
                    (-0.1, 1.2, 1.0),
                    (-2.0, 1.0, 0.0),
                    (2.0, 0.0, 1.0),
                )
            ):
                returned_event = (
                    CatKnowledge
                    .adjust_storyteller_trust(
                        self.listener,
                        name,
                        delta,
                        "updated",
                        legend_id=(
                            "legend_1"
                        ),
                    )
                )

                event = history[-1]

                self.assertIsInstance(
                    event,
                    CatRelationshipTrustEvent,
                )

                self.assertAlmostEqual(
                    event.previous,
                    previous,
                )

                self.assertAlmostEqual(
                    event.current,
                    current,
                )

                self.assertAlmostEqual(
                    event.delta,
                    current - previous,
                )

                self.assertEqual(
                    event.reason,
                    "updated",
                )

                self.assertEqual(
                    event.legend_id,
                    "legend_1",
                )

                self.assertEqual(
                    len(history),
                    index + 2,
                )

                self.assertIs(
                    returned_event,
                    event,
                )

                with self.assertRaises(
                    AttributeError
                ):
                    returned_event.current = -1.0

                self.assertAlmostEqual(
                    event.current,
                    current,
                )

            self.assertIs(
                self.listener.relationships.record(name),
                record,
            )

            self.assertIs(
                history[0],
                previous_entry,
            )

            self.assertEqual(
                previous_entry.reason,
                "past_meeting",
            )

        self.assertEqual(
            relationship.trust,
            1.0,
        )

        self.assertEqual(
            second_relationship.trust,
            1.0,
        )

        self.assertIs(
            relationship.trust_history,
            object_history,
        )

        self.assertIs(
            second_relationship.trust_history,
            second_history,
        )

    def test_relationship_rejects_mapping_trust_history(
        self
    ):
        with self.assertRaises(TypeError):
            CatRelationship(
                trust_history=[
                    {
                        "reason": "legacy",
                    }
                ]
            )

        relationship = (
            CatRelationship.create()
        )

        with self.assertRaises(TypeError):
            relationship.trust_history = [
                {
                    "reason": "legacy",
                }
            ]

        self.assertEqual(
            relationship.trust_history,
            [],
        )

if __name__ == "__main__":
    unittest.main()
