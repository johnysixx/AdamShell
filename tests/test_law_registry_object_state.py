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

    def test_missing_law_history_uses_object_state(
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

        self.assertIsInstance(
            event,
            LawNotFoundEvent,
        )

        self.assertEqual(
            event.law,
            "missing-law",
        )

        self.assertFalse(
            event.executed
        )

        self.assertEqual(
            result,
            {
                "name": "law_not_found",
                "law": "missing-law",
                "executed": False,
            },
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
            _ = event["law"]

    def test_triggered_history_freezes_payloads(
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

        self.assertIsInstance(
            event,
            LawTriggeredEvent,
        )

        self.assertEqual(
            event.context["value"],
            7,
        )

        self.assertEqual(
            event.context["items"],
            (
                1,
                2,
            ),
        )

        self.assertEqual(
            event.result[
                "nested"
            ][
                "value"
            ],
            7,
        )

        with self.assertRaises(
            TypeError
        ):
            event.context[
                "value"
            ] = 99

        with self.assertRaises(
            TypeError
        ):
            event.result[
                "nested"
            ][
                "value"
            ] = 99

        context["value"] = 99

        result[
            "context"
        ][
            "value"
        ] = 100

        result[
            "result"
        ][
            "nested"
        ][
            "value"
        ] = 101

        self.assertEqual(
            event.context["value"],
            7,
        )

        self.assertEqual(
            event.result[
                "nested"
            ][
                "value"
            ],
            7,
        )

    def test_trigger_boundary_shape_stays_dict_based(
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

        self.assertEqual(
            result,
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
