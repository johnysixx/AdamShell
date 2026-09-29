import unittest

from meeting_place.bar_counter import BarCounter
from meeting_place.bar_objects import BarGlass
from meeting_place.bar_serving_vessel_fill_state import (
    BarServingVesselFillState,
)


class BarServingVesselFillStateObjectStateTests(
    unittest.TestCase
):

    def _glass(
        self,
        state="clean",
        dirt=0.0,
    ):
        return BarGlass(
            name="glass",
            type="bar_glass",
            owner=None,
            state=state,
            dirt=dirt,
            location="shelf",
        )

    def test_glass_starts_empty_without_changing_cleanliness(
        self
    ):
        glass = self._glass()

        self.assertEqual(
            glass.state,
            "clean",
        )
        self.assertIs(
            glass.fill_state,
            BarServingVesselFillState.EMPTY,
        )

    def test_fill_changes_only_fill_state(self):
        glass = self._glass()

        glass.fill("water")

        self.assertEqual(
            glass.state,
            "clean",
        )
        self.assertIs(
            glass.fill_state,
            BarServingVesselFillState.FILLED,
        )
        self.assertEqual(
            glass.contains,
            "water",
        )

    def test_empty_preserves_dirty_cleanliness_state(
        self
    ):
        glass = self._glass(
            state="dirty",
            dirt=1.0,
        )
        glass.fill("water")

        glass.empty()

        self.assertEqual(
            glass.state,
            "dirty",
        )
        self.assertIs(
            glass.fill_state,
            BarServingVesselFillState.EMPTY,
        )
        self.assertIsNone(
            glass.contains,
        )

    def test_milk_bowl_uses_explicit_fill_state(self):
        bowl = BarCounter().milk_bowl

        self.assertFalse(
            hasattr(
                bowl,
                "state",
            )
        )
        self.assertIs(
            bowl.fill_state,
            BarServingVesselFillState.EMPTY,
        )
        self.assertEqual(
            bowl.to_dict()["fill_state"],
            "empty",
        )

    def test_string_fill_state_is_rejected(self):
        glass = self._glass()

        with self.assertRaises(TypeError):
            glass.fill_state = "filled"

    def test_fill_state_boundary_uses_strings(self):
        glass = self._glass()
        glass.fill("water")

        self.assertEqual(
            glass.to_dict()["fill_state"],
            "filled",
        )

    def test_fill_state_values_define_domain_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in BarServingVesselFillState
            },
            {
                "empty",
                "filled",
            },
        )


if __name__ == "__main__":
    unittest.main()
