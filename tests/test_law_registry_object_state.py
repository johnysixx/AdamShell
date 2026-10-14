import unittest

from universe.law_registry import (
    LawNotFoundEvent,
    LawRegistry,
    LawTriggeredEvent,
)


class ExampleLaw:

    def execute(
        self,
        context,
    ):
        return {
            "accepted": True,
            "nested": {
                "value": context["value"],
            },
        }


class LawRegistryObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def test_missing_law_returns_history_object(
        self
    ):
        registry = LawRegistry()

        result = registry.trigger(
            "missing-law"
        )

        event = (
            registry
            .trigger_history[-1]
        )

        self.assertIs(
            result,
            event,
        )
        self.assertIsInstance(
            result,
            LawNotFoundEvent,
        )
        self.assertEqual(
            result.law,
            "missing-law",
        )
        self.assertFalse(
            result.executed
        )

        self._assert_object_only(
            result,
            "law",
        )

        snapshot = result.to_dict()

        self.assertEqual(
            snapshot,
            {
                "name": "law_not_found",
                "law": "missing-law",
                "executed": False,
            },
        )

        snapshot["law"] = "changed"

        self.assertEqual(
            result.law,
            "missing-law",
        )

    def test_triggered_result_is_history_object(
        self
    ):
        registry = LawRegistry()

        registry.register(
            "example",
            ExampleLaw(),
        )

        context = {
            "value": 7,
            "items": [
                1,
                2,
            ],
        }

        result = registry.trigger(
            "example",
            context=context,
        )

        event = (
            registry
            .trigger_history[-1]
        )

        self.assertIs(
            result,
            event,
        )
        self.assertIsInstance(
            result,
            LawTriggeredEvent,
        )

        self._assert_object_only(
            result,
            "law",
        )

        self.assertEqual(
            result.context["value"],
            7,
        )
        self.assertEqual(
            result.context["items"],
            (
                1,
                2,
            ),
        )
        self.assertEqual(
            result.result[
                "nested"
            ][
                "value"
            ],
            7,
        )

        with self.assertRaises(
            TypeError
        ):
            result.context[
                "value"
            ] = 99

        with self.assertRaises(
            TypeError
        ):
            result.result[
                "nested"
            ][
                "value"
            ] = 99

        context["value"] = 99

        self.assertEqual(
            result.context["value"],
            7,
        )
        self.assertEqual(
            result.result[
                "nested"
            ][
                "value"
            ],
            7,
        )

    def test_to_dict_is_detached_boundary(
        self
    ):
        registry = LawRegistry()

        registry.register(
            "example",
            ExampleLaw(),
        )

        result = registry.trigger(
            "example",
            context={
                "value": 3,
                "items": [
                    4,
                    5,
                ],
            },
        )

        snapshot = result.to_dict()

        self.assertEqual(
            snapshot,
            {
                "name": "law_triggered",
                "law": "example",
                "executed": True,
                "context": {
                    "value": 3,
                    "items": [
                        4,
                        5,
                    ],
                },
                "result": {
                    "accepted": True,
                    "nested": {
                        "value": 3,
                    },
                },
            },
        )

        snapshot[
            "context"
        ][
            "value"
        ] = 100

        snapshot[
            "result"
        ][
            "nested"
        ][
            "value"
        ] = 101

        self.assertEqual(
            result.context["value"],
            3,
        )
        self.assertEqual(
            result.result[
                "nested"
            ][
                "value"
            ],
            3,
        )

    def test_history_rejects_mapping_event(
        self
    ):
        registry = LawRegistry()

        with self.assertRaises(TypeError):
            registry.record_trigger(
                {
                    "name":
                        "law_not_found",
                    "law": "legacy",
                    "executed": False,
                }
            )


if __name__ == "__main__":
    unittest.main()
