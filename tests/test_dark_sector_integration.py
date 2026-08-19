import unittest

from universe.universe import Universe
from universe.dark_sector import DarkSector


class DarkSectorIntegrationTests(
    unittest.TestCase
):

    def test_universe_owns_dark_sector(
        self
    ):
        universe = Universe()

        self.assertIsInstance(
            universe.dark_sector,
            DarkSector
        )

        self.assertEqual(
            universe.dark_sector.dark_energy_j,
            0.0
        )


if __name__ == "__main__":
    unittest.main()
