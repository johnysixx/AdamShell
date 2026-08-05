import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind


class CatIntentionExecutorTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="autonomous_cat",
            color="black",
            fur_length="short"
        )

        self.cat["position"] = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

    def set_intention(
        self,
        intention_type,
        target=None
    ):
        self.cat[
            "mind"
        ][
            "current_intention"
        ] = {
            "type": intention_type,
            "target": target,
            "score": 0.8,
            "reasons": [
                "test"
            ]
        }

    def create_cronenberg(
        self
    ):
        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Executor test."
                ),
                source_component="test",
                source_operation=(
                    "cat_intention_executor"
                )
            )
        )

        cronenberg.position = {
            "x": 3.0,
            "y": 0.0,
            "z": 0.0
        }

        cronenberg.size = 0.5

        return cronenberg

    def test_visit_bar_starts_existing_navigation(
        self
    ):
        self.set_intention(
            "visit_bar"
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertTrue(
            result["executed"]
        )

        self.assertEqual(
            result["intention"],
            "visit_bar"
        )

        self.assertEqual(
            result["body_intent"],
            "return_to_bar"
        )

        self.assertEqual(
            self.cat["intent"],
            "return_to_bar"
        )

        self.assertIn(
            "active_route_id",
            self.cat
        )

    def test_hunt_uses_existing_hunt_navigation(
        self
    ):
        cronenberg = (
            self.create_cronenberg()
        )

        self.set_intention(
            "hunt_cronenberg",
            target=cronenberg.id
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat,
                cronenbergs=[
                    cronenberg
                ]
            )
        )

        self.assertTrue(
            result["executed"]
        )

        self.assertEqual(
            result["body_intent"],
            (
                "hunt_nearest_cronenberg"
            )
        )

        self.assertEqual(
            self.cat["intent"],
            (
                "hunt_nearest_cronenberg"
            )
        )

    def test_rest_is_executed_without_route(
        self
    ):
        self.set_intention(
            "rest"
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertTrue(
            result["executed"]
        )

        self.assertEqual(
            self.cat["state"],
            "resting_by_own_choice"
        )

        self.assertNotIn(
            "active_route_id",
            self.cat
        )

    def test_unimplemented_body_action_is_deferred(
        self
    ):
        self.set_intention(
            "explore_box",
            target="unknown_box"
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertFalse(
            result["executed"]
        )

        self.assertTrue(
            result["deferred"]
        )

        self.assertTrue(
            result[
                "decision_preserved"
            ]
        )

        self.assertEqual(
            self.cat[
                "mind"
            ][
                "current_intention"
            ][
                "type"
            ],
            "explore_box"
        )

    def test_executor_does_not_make_new_decision(
        self
    ):
        decision = CatMind.decide(
            cat=self.cat,
            observations={
                "bar_known": True,
                "bar_visible": True
            }
        )

        decision_count = self.cat[
            "mind"
        ][
            "decision_count"
        ]

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertTrue(
            result["executed"]
        )

        self.assertEqual(
            self.cat[
                "mind"
            ][
                "decision_count"
            ],
            decision_count
        )

        self.assertEqual(
            decision["intention"],
            result["intention"]
        )

    def test_no_intention_does_nothing(
        self
    ):
        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertFalse(
            result["executed"]
        )

        self.assertEqual(
            result["reason"],
            "no_current_intention"
        )


if __name__ == "__main__":
    unittest.main()