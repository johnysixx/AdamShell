import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatIntentionCandidate,
)
from cats.cat_mind import CatMind
from cats.cat_perception_state import (
    CatPerceptionState,
)


class CatIntentionCandidateObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="candidate_cat",
            color="black",
            fur_length="short",
        )

    def test_candidate_is_clean_object(
        self
    ):
        candidate = CatMind._candidate(
            intention_type="rest",
            score=0.5,
            reasons=["test"],
        )

        self.assertIsInstance(
            candidate,
            CatIntentionCandidate,
        )

        self.assertFalse(
            hasattr(
                candidate,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                candidate,
                "__getitem__",
            )
        )

        self.assertEqual(
            candidate.type,
            "rest",
        )

        self.assertEqual(
            candidate.score,
            0.5,
        )

        self.assertEqual(
            candidate.reasons,
            ["test"],
        )

    def test_consider_returns_candidate_objects(
        self
    ):
        candidates = CatMind.consider(
            self.cat,
            CatPerceptionState(),
        )

        self.assertTrue(
            candidates
        )

        self.assertTrue(
            all(
                isinstance(
                    candidate,
                    CatIntentionCandidate,
                )
                for candidate in candidates
            )
        )

    def test_decision_keeps_selected_intention_as_object(
        self
    ):
        result = CatMind.decide(
            self.cat,
            CatPerceptionState(),
        )

        self.assertTrue(
            result["selected"]
        )

        self.assertIsInstance(
            self.cat.mind.current_intention,
            CatIntentionCandidate,
        )

        self.assertEqual(
            self.cat.mind.current_intention.type,
            result["intention"],
        )

        self.assertTrue(
            all(
                isinstance(
                    finalist,
                    CatIntentionCandidate,
                )
                for finalist
                in result["finalists"]
            )
        )


if __name__ == "__main__":
    unittest.main()
