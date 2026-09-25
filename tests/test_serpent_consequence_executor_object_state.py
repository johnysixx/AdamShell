import unittest

from quantum.serpent_consequence_executor import (
    SerpentConsequenceExecutor,
    SerpentConsequencesExecutedEvent,
    SerpentResolvedConsequence,
    SerpentUnresolvedConsequence,
)


class FakeUniverse:
    pass


class FakeSerpentD20:

    def __init__(
        self,
        consequences,
    ):
        self.consequences = list(
            consequences
        )

        self.recorded_roll_id = None
        self.recorded = None

    def hidden_resolution_for(
        self,
        roll_id,
    ):
        return {
            "roll_id": roll_id,
            "possible_consequences": list(
                self.consequences
            ),
        }

    def record_resolved_consequences(
        self,
        roll_id,
        resolved_consequences,
    ):
        self.recorded_roll_id = roll_id

        self.recorded = tuple(
            resolved_consequences
        )

        return {
            "roll_id": roll_id,
        }


class SerpentConsequenceExecutorObjectStateTests(
    unittest.TestCase
):

    def test_execution_history_uses_object_state(
        self,
    ):
        executor = (
            SerpentConsequenceExecutor(
                FakeUniverse()
            )
        )

        serpent = FakeSerpentD20(
            [
                "not_implemented",
            ]
        )

        result = (
            executor.execute_hidden_plan(
                serpent,
                "roll-object-state",
            )
        )

        event = (
            executor
            .execution_history[-1]
        )

        self.assertIsInstance(
            event,
            SerpentConsequencesExecutedEvent,
        )

        self.assertEqual(
            event.planned_consequences,
            (
                "not_implemented",
            ),
        )

        self.assertEqual(
            len(
                event.unresolved_consequences
            ),
            1,
        )

        self.assertIsInstance(
            event.unresolved_consequences[0],
            SerpentUnresolvedConsequence,
        )

        self.assertEqual(
            result[
                "unresolved_consequences"
            ][0][
                "reason"
            ],
            "handler_not_implemented",
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

        with self.assertRaises(TypeError):
            _ = event["roll_id"]

    def test_resolved_consequences_remain_objects(
        self,
    ):
        executor = (
            SerpentConsequenceExecutor(
                FakeUniverse()
            )
        )

        executor.handlers = {
            "custom_consequence": (
                lambda: {
                    "nested": [
                        7,
                    ],
                }
            ),
        }

        serpent = FakeSerpentD20(
            [
                "custom_consequence",
            ]
        )

        result = (
            executor.execute_hidden_plan(
                serpent,
                "resolved-roll",
            )
        )

        event = (
            executor
            .execution_history[-1]
        )

        consequence = (
            event
            .resolved_consequences[0]
        )

        self.assertIsInstance(
            consequence,
            SerpentResolvedConsequence,
        )

        self.assertIs(
            consequence,
            serpent.recorded[0],
        )

        self.assertEqual(
            serpent.recorded_roll_id,
            "resolved-roll",
        )

        result[
            "resolved_consequences"
        ][0][
            "result"
        ][
            "nested"
        ][0] = 99

        self.assertEqual(
            consequence.result[
                "nested"
            ][0],
            7,
        )

    def test_execution_snapshot_is_detached(
        self,
    ):
        executor = (
            SerpentConsequenceExecutor(
                FakeUniverse()
            )
        )

        serpent = FakeSerpentD20(
            [
                "missing_one",
            ]
        )

        result = (
            executor.execute_hidden_plan(
                serpent,
                "detached-roll",
            )
        )

        event = (
            executor
            .execution_history[-1]
        )

        result[
            "planned_consequences"
        ][0] = "changed"

        result[
            "unresolved_consequences"
        ][0][
            "reason"
        ] = "changed"

        self.assertEqual(
            event.planned_consequences,
            (
                "missing_one",
            ),
        )

        self.assertEqual(
            event
            .unresolved_consequences[0]
            .reason,
            "handler_not_implemented",
        )

    def test_execution_history_rejects_mapping(
        self,
    ):
        executor = (
            SerpentConsequenceExecutor(
                FakeUniverse()
            )
        )

        with self.assertRaises(TypeError):
            executor.record_execution(
                {
                    "name":
                        "serpent_consequences_executed",
                }
            )


if __name__ == "__main__":
    unittest.main()
