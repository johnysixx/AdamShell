import unittest

from meeting_place.dice_box import (
    DiceBox,
    DiceBoxAllRotationEvent,
    DiceBoxRotationEvent,
)


class FixedRoll:

    def __init__(
        self,
        value=1
    ):
        self.value = value

    def randint(
        self,
        minimum,
        maximum
    ):
        return min(
            max(
                self.value,
                minimum,
            ),
            maximum,
        )


class DiceBoxAllRotationHistoryObjectStateTests(
    unittest.TestCase
):

    def test_all_rotation_history_uses_event_objects(
        self
    ):
        box = DiceBox()

        result = box.rotate_all_dice(
            rng=FixedRoll(1)
        )

        event = (
            box.all_rotation_history[-1]
        )

        self.assertIsInstance(
            event,
            DiceBoxAllRotationEvent,
        )

        self.assertEqual(
            event.rotated_count,
            len(
                box.contents
            ),
        )

        self.assertTrue(
            event.results
        )

        self.assertTrue(
            all(
                isinstance(
                    item,
                    DiceBoxRotationEvent,
                )
                for item
                in event.results
            )
        )

        self.assertEqual(
            event.to_dict(),
            result,
        )

    def test_all_rotation_event_reuses_rotation_history_objects(
        self
    ):
        box = DiceBox()

        box.rotate_all_dice(
            rng=FixedRoll(2)
        )

        event = (
            box.all_rotation_history[-1]
        )

        self.assertEqual(
            len(
                event.results
            ),
            len(
                box.rotation_history
            ),
        )

        for (
            result_event,
            history_event,
        ) in zip(
            event.results,
            box.rotation_history,
        ):
            self.assertIs(
                result_event,
                history_event,
            )

    def test_boundary_is_detached_and_event_has_no_mapping_api(
        self
    ):
        box = DiceBox()

        result = box.rotate_all_dice(
            rng=FixedRoll(3)
        )

        event = (
            box.all_rotation_history[-1]
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

        with self.assertRaises(
            TypeError
        ):
            _ = event[
                "results"
            ]

        original_value = (
            event.results[0].value
        )

        result[
            "results"
        ][0][
            "value"
        ] = 999

        self.assertEqual(
            event.results[0].value,
            original_value,
        )

    def test_all_rotation_history_rejects_mapping(
        self
    ):
        box = DiceBox()

        with self.assertRaises(
            TypeError
        ):
            box.record_all_rotation(
                {
                    "name": (
                        "dice_box_all_rotation"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
