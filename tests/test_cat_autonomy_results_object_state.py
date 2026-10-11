import unittest

from cats.cat_autonomy_result_state import (
    CatsTickCompletedEvent,
    CatThoughtCycleCompletedEvent,
)
from cats.cat_basic_intention_result_state import (
    CatIntentionExecutionSkippedResult,
)
from cats.cat_mind import (
    CatMind,
)
from cats.cat_mind_result_state import (
    CatIntentionClearedEvent,
)
from cats.cats import (
    Cats,
)
from core.entity.components import (
    SpatialVector3,
)
from universe.universe import (
    Universe,
)


class CatAutonomyResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.universe = (
            Universe()
        )

        self.universe.enable_quantum_layer()

        self.cats = (
            Cats(
                self.universe
            )
        )

        self.cat = (
            self.cats.create_cat(
                name="autonomy_object_cat",
                color="black",
                fur_length="short",
            )
        )

        self.cat.position = (
            SpatialVector3.zero()
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

    def test_no_intention_result_is_object(
        self,
    ):
        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatIntentionExecutionSkippedResult,
        )

        self.assertFalse(
            result.executed
        )

        self.assert_object_only(
            result
        )

    def test_clear_intention_event_is_object(
        self,
    ):
        result = (
            CatMind.clear_intention(
                self.cat,
                reason="test",
            )
        )

        self.assertIsInstance(
            result,
            CatIntentionClearedEvent,
        )

        self.assertTrue(
            result.cleared
        )

        self.assert_object_only(
            result
        )

    def test_thought_cycle_result_is_object(
        self,
    ):
        result = (
            self.cats.think_and_act(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatThoughtCycleCompletedEvent,
        )

        self.assertTrue(
            result.completed
        )

        self.assert_object_only(
            result
        )

    def test_tick_report_and_nested_results_are_objects(
        self,
    ):
        report = (
            self.cats.tick()
        )

        self.assertIsInstance(
            report,
            CatsTickCompletedEvent,
        )

        self.assert_object_only(
            report
        )

        self.assertTrue(
            report.cats
        )

        operation = (
            report.cats[0]
        )

        self.assert_object_only(
            operation
        )

        self.assert_object_only(
            operation.result
        )


if __name__ == "__main__":
    unittest.main()
