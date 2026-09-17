import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_exploration_planner import (
    CatExplorationPlanner
)
from cats.cat_exploration_state import (
    CatAfterArrivalCandidate,
    CatAfterArrivalDecision,
)


class CatAfterArrivalDecisionObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="after_arrival_cat",
            color="black",
            fur_length="short",
        )

    def decision(
        self,
        quantum_roll=None,
    ):
        return (
            CatExplorationPlanner
            .choose_after_arrival(
                cat=self.cat,
                pair=object(),
                quantum_roll=quantum_roll,
            )
        )

    def test_after_arrival_decision_is_object(
        self
    ):
        decision = self.decision()

        self.assertIsInstance(
            decision,
            CatAfterArrivalDecision,
        )

        self.assertTrue(
            decision.selected
        )

        self.assertFalse(
            hasattr(
                decision,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                decision,
                "__getitem__",
            )
        )

    def test_after_arrival_finalists_are_objects(
        self
    ):
        decision = self.decision()

        self.assertEqual(
            len(
                decision.finalists
            ),
            2,
        )

        self.assertTrue(
            all(
                isinstance(
                    candidate,
                    CatAfterArrivalCandidate,
                )
                for candidate
                in decision.finalists
            )
        )

        self.assertTrue(
            all(
                not hasattr(
                    candidate,
                    "get",
                )
                for candidate
                in decision.finalists
            )
        )

    def test_high_quantum_roll_selects_second_finalist(
        self
    ):
        decision = self.decision(
            quantum_roll=20
        )

        self.assertEqual(
            decision.action,
            decision.finalists[1].action,
        )

        self.assertEqual(
            decision.score,
            decision.finalists[1].score,
        )

        self.assertEqual(
            decision.quantum_roll,
            20,
        )


if __name__ == "__main__":
    unittest.main()
