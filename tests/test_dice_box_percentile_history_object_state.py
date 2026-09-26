import unittest

from meeting_place.dice_box import (
    DiceBox,
    DiceBoxPercentilePairRotationEvent,
    DiceBoxRotationEvent,
)


class SequenceRng:

    def __init__(
        self,
        values
    ):
        self.values = list(
            values
        )

    def randint(
        self,
        minimum,
        maximum
    ):
        value = self.values.pop(
            0
        )

        return min(
            max(
                value,
                minimum,
            ),
            maximum,
        )


class DiceBoxPercentileHistoryObjectStateTests(
    unittest.TestCase
):

    def test_percentile_history_uses_event_object(
        self
    ):
        box = DiceBox()

        result = (
            box.rotate_percentile_pair(
                rng=SequenceRng(
                    [
                        4,
                        7,
                    ]
                )
            )
        )

        event = (
            box.percentile_history[-1]
        )

        self.assertIsInstance(
            event,
            DiceBoxPercentilePairRotationEvent,
        )

        self.assertIsInstance(
            event.tens,
            DiceBoxRotationEvent,
        )

        self.assertIsInstance(
            event.units,
            DiceBoxRotationEvent,
        )

        self.assertEqual(
            event.percentile_units,
            7,
        )

        self.assertEqual(
            event.value,
            47,
        )

        self.assertEqual(
            event.to_dict(),
            result,
        )

    def test_percentile_event_reuses_rotation_history_objects(
        self
    ):
        box = DiceBox()

        box.rotate_percentile_pair(
            rng=SequenceRng(
                [
                    3,
                    6,
                ]
            )
        )

        event = (
            box.percentile_history[-1]
        )

        self.assertIs(
            event.tens,
            box.rotation_history[-2],
        )

        self.assertIs(
            event.units,
            box.rotation_history[-1],
        )

    def test_boundary_is_detached_and_event_has_no_mapping_api(
        self
    ):
        box = DiceBox()

        result = (
            box.rotate_percentile_pair(
                rng=SequenceRng(
                    [
                        5,
                        8,
                    ]
                )
            )
        )

        event = (
            box.percentile_history[-1]
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
                "value"
            ]

        result[
            "tens"
        ][
            "value"
        ] = 999

        result[
            "units"
        ][
            "percentile_units"
        ] = 999

        result[
            "dice"
        ][0] = "changed"

        self.assertEqual(
            event.tens.value,
            50,
        )

        self.assertEqual(
            event.percentile_units,
            8,
        )

        self.assertEqual(
            event.dice,
            (
                "d10_percentile",
                "d10",
            ),
        )

    def test_percentile_history_rejects_mapping(
        self
    ):
        box = DiceBox()

        with self.assertRaises(
            TypeError
        ):
            box.record_percentile_rotation(
                {
                    "name": (
                        "dice_box_percentile_"
                        "pair_rotated"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
