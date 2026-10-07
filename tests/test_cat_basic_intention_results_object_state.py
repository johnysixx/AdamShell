import unittest

from cats.cat_basic_intention_result_state import (
    CatIntentionBodyActionDeferredEvent,
    CatRestStartedEvent,
    CatWanderedEvent,
    CatWanderFailedResult,
)
from cats.cat_intention_state import (
    CatIntentionCandidate,
)
from cats.cats import Cats
from core.entity.components import (
    SpatialVector3,
)
from universe.universe import Universe


class CatBasicIntentionResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = (
            self.cats.create_cat(
                name="basic_action_cat",
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

    def set_intention(
        self,
        intention_type,
        target=None,
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type=intention_type,
                target=target,
                score=1.0,
                reasons=[
                    "test"
                ],
            )
        )

    def test_wander_result_is_object(
        self
    ):
        self.cat.position = (
            SpatialVector3.zero()
        )

        self.set_intention(
            "wander"
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat,
                step_size=2.0,
            )
        )

        self.assertIsInstance(
            result,
            CatWanderedEvent,
        )

        self.assertTrue(
            result.executed
        )

        self.assertIsInstance(
            result.from_position,
            SpatialVector3,
        )

        self.assertIsInstance(
            result.position,
            SpatialVector3,
        )

        self.assertEqual(
            abs(result.step),
            2.0,
        )

        self.assert_object_only(
            result
        )

    def test_wander_failure_is_object(
        self
    ):
        self.set_intention(
            "wander"
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatWanderFailedResult,
        )

        self.assertFalse(
            result.executed
        )

        self.assertEqual(
            result.reason,
            "missing_position",
        )

        self.assert_object_only(
            result
        )

    def test_rest_result_is_object(
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

        self.assertIsInstance(
            result,
            CatRestStartedEvent,
        )

        self.assertTrue(
            result.executed
        )

        self.assertEqual(
            result.intention,
            "rest",
        )

        self.assertEqual(
            self.cat.state,
            "resting_by_own_choice",
        )

        self.assert_object_only(
            result
        )

    def test_deferred_result_is_object(
        self
    ):
        self.set_intention(
            "observe",
            target="unknown",
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatIntentionBodyActionDeferredEvent,
        )

        self.assertFalse(
            result.executed
        )

        self.assertTrue(
            result.deferred
        )

        self.assertTrue(
            result.decision_preserved
        )

        self.assertEqual(
            result.required_system,
            "cat_observation_body_system",
        )

        self.assert_object_only(
            result
        )

    def test_active_body_execution_is_detached_object(
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

        active = (
            self.cat
            .mind
            .active_body_execution
        )

        self.assertIsInstance(
            active,
            CatRestStartedEvent,
        )

        self.assertEqual(
            active,
            result,
        )

        self.assertIsNot(
            active,
            result,
        )

        self.assert_object_only(
            active
        )

    def test_executor_history_keeps_object(
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

        stored = (
            self.cats
            .intention_executor
            .history[-1]
        )

        self.assertIsInstance(
            stored,
            CatRestStartedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )


if __name__ == "__main__":
    unittest.main()
