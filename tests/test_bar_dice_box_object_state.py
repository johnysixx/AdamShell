import unittest

from meeting_place.bar_objects import (
    DiceBoxRotationState,
    DiceBoxState,
)
from meeting_place.dice_box import DiceBox


class FixedRoll:

    def __init__(self, value):
        self.value = value

    def randint(self, minimum, maximum):
        return self.value


class FixedRolls:

    def __init__(self, values):
        self.values = iter(values)

    def randint(self, minimum, maximum):
        return next(self.values)


class BarDiceBoxObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key
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
                    mapping_method
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[key]

    def test_dice_box_state_has_no_mapping_api(
        self
    ):
        rotation = DiceBoxRotationState(
            die="d6",
            value=4,
        )
        state = DiceBoxState(
            last_secret_rotation=rotation
        )

        self._assert_object_only(
            state,
            "contents"
        )
        self._assert_object_only(
            rotation,
            "die"
        )

    def test_public_state_is_detached_dict(
        self
    ):
        box = DiceBox()
        snapshot = box.public_state

        self.assertIsInstance(
            snapshot,
            dict
        )
        snapshot["contents"].append(
            "changed"
        )
        snapshot["missing"].clear()

        self.assertNotIn(
            "changed",
            box.state.contents
        )
        self.assertEqual(
            box.state.missing,
            ["d20"]
        )

    def test_named_rotation_updates_same_state(
        self
    ):
        box = DiceBox()
        state = box.state

        event = box.rotate_named_die(
            "d6",
            rng=FixedRoll(4)
        )

        self.assertIs(
            box.state,
            state
        )
        self.assertIsInstance(
            state.last_secret_rotation,
            DiceBoxRotationState
        )
        self.assertEqual(
            state.last_secret_rotation.die,
            event["die"]
        )
        self.assertEqual(
            state.last_secret_rotation.value,
            event["value"]
        )

    def test_all_rotation_uses_object_summaries(
        self
    ):
        box = DiceBox()
        event = box.rotate_all_dice(
            rng=FixedRoll(1)
        )

        self.assertEqual(
            len(box.state.last_all_rotation),
            len(box.contents)
        )
        self.assertTrue(
            all(
                isinstance(
                    rotation,
                    DiceBoxRotationState
                )
                for rotation in
                box.state.last_all_rotation
            )
        )
        self.assertEqual(
            box.public_state[
                "last_all_rotation"
            ],
            {
                result["die"]:
                    result["value"]
                for result in
                event["results"]
            }
        )

    def test_percentile_rotation_is_object_state(
        self
    ):
        box = DiceBox()
        event = (
            box.rotate_percentile_pair(
                rng=FixedRolls(
                    [7, 4]
                )
            )
        )

        self.assertEqual(
            box.state
            .last_percentile_rotation,
            74
        )
        self.assertEqual(
            box.public_state[
                "last_percentile_rotation"
            ],
            event["value"]
        )

    def test_removing_die_mutates_object_state(
        self
    ):
        box = DiceBox()
        state = box.state

        removed = box.remove_next_die()

        self.assertEqual(
            removed,
            "d12"
        )
        self.assertNotIn(
            removed,
            state.contents
        )
        self.assertIn(
            removed,
            state.missing
        )
        self.assertEqual(
            box.public_state["missing"],
            ["d20", "d12"]
        )


if __name__ == "__main__":
    unittest.main()
