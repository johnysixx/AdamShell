import unittest
from unittest.mock import patch

from cats.cat_intention_state import (
    CatIntentionCandidate,
)
from cats.cat_mind import CatMind
from cats.cat_mind_result_state import (
    CatIntentionNotSelectedResult,
    CatIntentionSelectedEvent,
)
from cats.cat_perception_state import (
    CatPerceptionState,
)
from cats.cats import Cats
from universe.universe import Universe


class CatMindDecisionResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = (
            self.cats.create_cat(
                name="object_mind_cat",
                color="black",
                fur_length="short",
            )
        )

    def assert_object_only(
        self,
        value,
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
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "name"
            ]

    def test_selected_decision_is_object(
        self
    ):
        result = CatMind.decide(
            self.cat,
            CatPerceptionState(
                bar_known=True,
            ),
        )

        self.assertIsInstance(
            result,
            CatIntentionSelectedEvent,
        )

        self.assertTrue(
            result.selected
        )

        self.assertEqual(
            result.intention,
            "visit_bar",
        )

        self.assertIsInstance(
            result.finalists,
            tuple,
        )

        self.assertTrue(
            all(
                isinstance(
                    finalist,
                    CatIntentionCandidate,
                )
                for finalist
                in result.finalists
            )
        )

        self.assert_object_only(
            result
        )

    def test_decision_history_stores_detached_object(
        self
    ):
        result = CatMind.decide(
            self.cat,
            CatPerceptionState(
                bar_known=True,
            ),
        )

        stored = (
            self.cat
            .mind
            .history[-1]
        )

        self.assertIsInstance(
            stored,
            CatIntentionSelectedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assertIsNot(
            stored.finalists,
            result.finalists,
        )

        self.assert_object_only(
            stored
        )

    def test_selected_intention_remains_object(
        self
    ):
        result = CatMind.decide(
            self.cat,
            CatPerceptionState(),
        )

        self.assertIsInstance(
            self.cat
            .mind
            .current_intention,
            CatIntentionCandidate,
        )

        self.assertEqual(
            self.cat
            .mind
            .current_intention
            .type,
            result.intention,
        )

    def test_no_candidate_result_is_object(
        self
    ):
        with patch.object(
            CatMind,
            "consider",
            return_value=[],
        ):
            result = (
                CatMind.decide(
                    self.cat,
                    CatPerceptionState(),
                )
            )

        self.assertIsInstance(
            result,
            CatIntentionNotSelectedResult,
        )

        self.assertFalse(
            result.selected
        )

        self.assertEqual(
            result.reason,
            "no_candidates",
        )

        self.assertEqual(
            self.cat.mind.history,
            [],
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
