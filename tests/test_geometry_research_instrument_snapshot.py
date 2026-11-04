import unittest

from research.geometry_research_instrument import (
    GeometryResearchInstrument,
)


class GeometryResearchInstrumentSnapshotTests(
    unittest.TestCase
):

    def test_public_state_detaches_last_measurement(self):
        instrument = GeometryResearchInstrument()

        measurement = instrument.measure({
            "geometry_version": 1,
            "stable_connection_count": 2,
        })

        self.assertIs(
            instrument.last_measurement,
            measurement,
        )

        first = instrument.public_state
        second = instrument.public_state

        first["last_measurement"][
            "geometry_version"
        ] = 99

        self.assertEqual(
            measurement["geometry_version"],
            1,
        )

        self.assertEqual(
            second["last_measurement"][
                "geometry_version"
            ],
            1,
        )

        self.assertEqual(
            instrument.public_state[
                "last_measurement"
            ]["geometry_version"],
            1,
        )

        self.assertIs(
            instrument.measurements[0],
            measurement,
        )

    def test_snapshot_ignores_later_live_changes(self):
        instrument = GeometryResearchInstrument()

        measurement = instrument.measure({
            "geometry_version": 1,
            "stable_connection_count": 2,
        })

        snapshot = instrument.public_state

        measurement[
            "stable_connection_count"
        ] = 7

        self.assertEqual(
            snapshot["last_measurement"][
                "stable_connection_count"
            ],
            2,
        )

        self.assertEqual(
            instrument.public_state[
                "last_measurement"
            ]["stable_connection_count"],
            7,
        )

        instrument.measure({
            "geometry_version": 2,
            "stable_connection_count": 8,
        })

        self.assertEqual(
            snapshot["measurement_count"],
            1,
        )

        self.assertEqual(
            snapshot["last_measurement"][
                "geometry_version"
            ],
            1,
        )

        self.assertEqual(
            instrument.public_state[
                "measurement_count"
            ],
            2,
        )

    def test_empty_and_multiple_measurements(self):
        instrument = GeometryResearchInstrument()

        self.assertEqual(
            instrument.public_state,
            {
                "name": "geometry_research_instrument",
                "type": "research_instrument",
                "measurement_count": 0,
                "last_measurement": None,
            },
        )

        first = instrument.measure({
            "geometry_version": 1,
            "stable_connection_count": 2,
        })

        second = instrument.measure({
            "geometry_version": 2,
            "stable_connection_count": 3,
        })

        snapshot = instrument.public_state

        self.assertEqual(
            snapshot["measurement_count"],
            2,
        )

        self.assertEqual(
            snapshot["last_measurement"],
            {
                "geometry_version": 2,
                "stable_connection_count": 3,
            },
        )

        snapshot["last_measurement"][
            "stable_connection_count"
        ] = 99

        self.assertEqual(
            second["stable_connection_count"],
            3,
        )

        self.assertIs(
            instrument.measurements[0],
            first,
        )

        self.assertIs(
            instrument.measurements[1],
            second,
        )

        self.assertIs(
            instrument.last_measurement,
            second,
        )


if __name__ == "__main__":
    unittest.main()
