import unittest

from meeting_place.dice_box import (
    DiceBox,
    DiceBoxRotationEvent,
)


class FixedRoll:

    def __init__(
        self,
        value
    ):
        self.value = value

    def randint(
        self,
        minimum,
        maximum
    ):
        return self.value


class DiceBoxRotationHistoryObjectStateTests(
    unittest.TestCase
):

    def test_rotation_history_uses_event_objects(
        self
    ):
        box = DiceBox()

        result = box.rotate_named_die(
            "d6",
            rng=FixedRoll(4),
        )

        event = (
            box.rotation_history[-1]
        )

        self.assertIsInstance(
            event,
            DiceBoxRotationEvent,
        )

        self.assertEqual(
            event.die,
            "d6",
        )

        self.assertEqual(
            event.value,
            4,
        )

        self.assertEqual(
            event.to_dict(),
            result,
        )

    def test_rotation_event_has_no_mapping_api(
        self
    ):
        box = DiceBox()

        box.rotate_named_die(
            "d8",
            rng=FixedRoll(5),
        )

        event = (
            box.rotation_history[-1]
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
            _ = event["die"]

    def test_returned_boundary_is_detached_from_history(
        self
    ):
        box = DiceBox()

        result = box.rotate_named_die(
            "d10",
            rng=FixedRoll(7),
        )

        event = (
            box.rotation_history[-1]
        )

        result["value"] = 99
        result["die"] = "changed"

        self.assertEqual(
            event.value,
            7,
        )

        self.assertEqual(
            event.die,
            "d10",
        )

    def test_rotation_history_rejects_mapping(
        self
    ):
        box = DiceBox()

        with self.assertRaises(
            TypeError
        ):
            box.record_rotation(
                {
                    "name": (
                        "dice_box_die_"
                        "secretly_rotated"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
