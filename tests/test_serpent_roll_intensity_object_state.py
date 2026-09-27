import unittest

from quantum.serpent_roll_intensity import (
    SerpentRollIntensity,
)


class SerpentRollIntensityObjectStateTests(
    unittest.TestCase
):

    def test_intensity_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                intensity.value
                for intensity
                in SerpentRollIntensity
            },
            {
                "low",
                "moderate",
                "high",
                "severe",
                "unbounded",
            },
        )


if __name__ == "__main__":
    unittest.main()
