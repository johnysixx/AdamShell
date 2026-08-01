import unittest

from universe.universe import Universe


class CronenbergPopulationStatisticsTests(
    unittest.TestCase
):

    def test_population_pressure_levels(self):
        universe = Universe()

        statistics = (
            universe
            .cronenberg_population_statistics
        )

        self.assertEqual(
            statistics.classify_pressure(0),
            "low"
        )

        self.assertEqual(
            statistics.classify_pressure(4.99),
            "low"
        )

        self.assertEqual(
            statistics.classify_pressure(5.0),
            "elevated"
        )

        self.assertEqual(
            statistics.classify_pressure(9.99),
            "elevated"
        )

        self.assertEqual(
            statistics.classify_pressure(10.0),
            "high"
        )

        self.assertEqual(
            statistics.classify_pressure(19.99),
            "high"
        )

        self.assertEqual(
            statistics.classify_pressure(20.0),
            "critical"
        )

        empty_snapshot = statistics.snapshot()

        self.assertEqual(
            empty_snapshot[
                "population_pressure_level"
            ],
            "low"
        )

        original = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("test"),
                "test",
                "pressure_level"
            )
        )

        universe.create_cronenberg_quantum_counterpart(
            original
        )

        pair_snapshot = statistics.snapshot()

        self.assertAlmostEqual(
            pair_snapshot[
                "population_pressure"
            ],
            5.0
        )

        self.assertEqual(
            pair_snapshot[
                "population_pressure_level"
            ],
            "elevated"
        )

    def test_population_pressure_and_delta(self):
        universe = Universe()

        statistics = (
            universe
            .cronenberg_population_statistics
        )

        first_record = (
            statistics.record_snapshot()
        )

        self.assertEqual(
            first_record["snapshot"][
                "population_pressure"
            ],
            0
        )

        self.assertEqual(
            first_record["delta"][
                "population_pressure_delta"
            ],
            0
        )

        original = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("test"),
                "test",
                "population_pressure"
            )
        )

        universe.create_cronenberg_quantum_counterpart(
            original
        )

        second_record = (
            statistics.record_snapshot()
        )

        self.assertEqual(
            second_record["snapshot"][
                "active_count"
            ],
            2
        )

        self.assertEqual(
            second_record["snapshot"][
                "active_quantum_pair_count"
            ],
            1
        )

        self.assertAlmostEqual(
            second_record["snapshot"][
                "total_active_energy"
            ],
            2.0
        )

        self.assertAlmostEqual(
            second_record["snapshot"][
                "population_pressure"
            ],
            5.0
        )

        self.assertAlmostEqual(
            second_record["delta"][
                "population_pressure_delta"
            ],
            5.0
        )

    def test_universe_tick_records_population_delta(self):
        universe = Universe()

        universe.tick_universe()

        self.assertEqual(
            len(
                universe
                .cronenberg_population_statistics
                .history
            ),
            1
        )

        first_record = (
            universe
            .cronenberg_population_statistics
            .last_record
        )

        self.assertEqual(
            first_record["tick"],
            1
        )

        self.assertEqual(
            first_record["snapshot"][
                "total_count"
            ],
            0
        )

        universe.create_cronenberg_from_quantum_error(
            RuntimeError("test"),
            "test",
            "population_tick_delta"
        )

        universe.tick_universe()

        statistics = (
            universe
            .cronenberg_population_statistics
        )

        self.assertEqual(
            len(statistics.history),
            2
        )

        second_record = statistics.last_record

        self.assertEqual(
            second_record["tick"],
            2
        )

        self.assertEqual(
            second_record["snapshot"][
                "total_count"
            ],
            1
        )

        self.assertEqual(
            second_record["delta"][
                "total_count_delta"
            ],
            1
        )

        self.assertEqual(
            second_record["delta"][
                "active_count_delta"
            ],
            1
        )

        self.assertAlmostEqual(
            second_record["delta"][
                "total_active_size_delta"
            ],
            1.1
        )

        self.assertAlmostEqual(
            second_record["delta"][
                "total_active_energy_delta"
            ],
            0.95
        )

    def test_empty_and_single_population(self):
        universe = Universe()

        empty = (
            universe
            .cronenberg_population_statistics
            .public_state
        )

        self.assertEqual(
            empty["total_count"],
            0
        )

        self.assertEqual(
            empty["active_count"],
            0
        )

        self.assertEqual(
            empty["standalone_active_count"],
            0
        )

        cronenberg = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("test"),
                "test",
                "population_statistics"
            )
        )

        state = (
            universe
            .cronenberg_population_statistics
            .public_state
        )

        self.assertEqual(
            state["total_count"],
            1
        )

        self.assertEqual(
            state["active_count"],
            1
        )

        self.assertEqual(
            state["inactive_count"],
            0
        )

        self.assertEqual(
            state["standalone_active_count"],
            1
        )

        self.assertEqual(
            state["active_quantum_pair_count"],
            0
        )

        self.assertAlmostEqual(
            state["total_active_size"],
            cronenberg.size
        )

        self.assertAlmostEqual(
            state["total_active_energy"],
            cronenberg.energy
        )


if __name__ == "__main__":
    unittest.main()