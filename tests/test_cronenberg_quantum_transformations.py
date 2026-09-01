import unittest

from universe.universe import Universe


class CronenbergQuantumTransformationTests(
    unittest.TestCase
):

    def create_pair(self):
        universe = Universe()

        first = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("test"),
                "test",
                "quantum_transformation"
            )
        )

        second = (
            universe
            .create_cronenberg_quantum_counterpart(
                first
            )["counterpart"]
        )

        first.location = "between_layers"
        second.location = "between_layers"

        return universe, first, second

    def test_quantum_pair_merge(self):
        universe, first, second = (
            self.create_pair()
        )

        first.size = 1.2
        first.energy = 0.8

        second.size = 1.5
        second.energy = 1.1

        result = (
            universe
            .merge_cronenberg_quantum_pair(
                first,
                second
            )
        )

        merged = result["merged"]

        self.assertFalse(first.active)
        self.assertFalse(second.active)

        self.assertEqual(
            first.state,
            "quantum_merged"
        )

        self.assertEqual(
            second.state,
            "quantum_merged"
        )

        self.assertEqual(
            first.location,
            "merged_history"
        )

        self.assertEqual(
            second.location,
            "merged_history"
        )

        self.assertEqual(
            first.merged_into,
            merged.id
        )

        self.assertEqual(
            second.merged_into,
            merged.id
        )

        self.assertTrue(merged.active)

        self.assertEqual(
            merged.state,
            "born_from_quantum_merge"
        )

        self.assertAlmostEqual(
            merged.size,
            2.7
        )

        self.assertAlmostEqual(
            merged.energy,
            1.9
        )

        self.assertEqual(
            merged.quantum_state.spin,
            0.0
        )

        self.assertFalse(
            merged.quantum_state.entangled
        )

        self.assertEqual(
            merged.merged_from,
            [
                first.id,
                second.id
            ]
        )

        ages_before = (
            first.age,
            second.age,
            merged.age
        )

        universe.tick_entities()

        ages_after = (
            first.age,
            second.age,
            merged.age
        )

        self.assertEqual(
            ages_after[0],
            ages_before[0]
        )

        self.assertEqual(
            ages_after[1],
            ages_before[1]
        )

        self.assertEqual(
            ages_after[2],
            ages_before[2] + 1
        )

    def test_quantum_pair_consumption_recombines(self):
        universe, first, second = (
            self.create_pair()
        )

        first.size = 1.2
        first.energy = 0.8

        second.size = 1.5
        second.energy = 1.2

        energy_pool_before = (
            universe.energy_pool
        )

        dark_energy_before = getattr(
            universe,
            "dark_energy",
            0.0
        )

        result = first.consume(second)

        recombined = result["recombined"]
        event = result["event"]

        self.assertFalse(first.active)
        self.assertFalse(second.active)

        self.assertEqual(
            first.state,
            (
                "destroyed_by_"
                "quantum_pair_consumption"
            )
        )

        self.assertEqual(
            second.state,
            (
                "destroyed_by_"
                "quantum_pair_consumption"
            )
        )

        self.assertEqual(
            first.location,
            "quantum_consumption_history"
        )

        self.assertEqual(
            second.location,
            "quantum_consumption_history"
        )

        self.assertEqual(
            first.recombined_into,
            recombined.id
        )

        self.assertEqual(
            second.recombined_into,
            recombined.id
        )

        self.assertTrue(recombined.active)

        self.assertEqual(
            recombined.state,
            (
                "born_from_"
                "quantum_pair_consumption"
            )
        )

        self.assertAlmostEqual(
            recombined.size,
            1.35
        )

        self.assertAlmostEqual(
            recombined.energy,
            0.8
        )

        self.assertEqual(
            recombined.quantum_state.spin,
            0.0
        )

        self.assertTrue(
            recombined.quantum_state.counterpart_potential
        )

        self.assertFalse(
            recombined.quantum_state.counterpart_manifested
        )

        self.assertEqual(
            recombined.recombined_from,
            [
                first.id,
                second.id
            ]
        )

        self.assertAlmostEqual(
            universe.energy_pool
            - energy_pool_before,
            0.7
        )

        self.assertAlmostEqual(
            universe.dark_energy
            - dark_energy_before,
            0.5
        )

        self.assertEqual(
            event["recombined_id"],
            recombined.id
        )

        self.assertAlmostEqual(
            event["combined_size"],
            2.7
        )

        self.assertAlmostEqual(
            event["combined_energy"],
            2.0
        )

        self.assertAlmostEqual(
            event["retained_energy"],
            0.8
        )

        self.assertAlmostEqual(
            event["released_energy"],
            0.7
        )

        self.assertAlmostEqual(
            event["dark_energy_created"],
            0.5
        )


if __name__ == "__main__":
    unittest.main()