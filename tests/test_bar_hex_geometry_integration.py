import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from meeting_place.bar_hex_geometry import (
    BarHexGeometry
)


class BarHexGeometryIntegrationTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        bootstrap = UniverseBootstrap(
            UniverseRegistry(),
            self.universe
        )

        bootstrap.run()

        self.meeting_place = (
            self.universe.meeting_place
        )

    def test_meeting_place_owns_bar_hex_geometry(
        self
    ):
        self.assertTrue(
            hasattr(
                self.meeting_place,
                "bar_geometry"
            )
        )

        self.assertIsInstance(
            self.meeting_place.bar_geometry,
            BarHexGeometry
        )

        self.assertEqual(
            self.meeting_place
            .bar_geometry
            .hex_width,
            1000
        )

        self.assertEqual(
            self.meeting_place
            .bar_geometry
            .hex_height,
            1000
        )


if __name__ == "__main__":
    unittest.main()
