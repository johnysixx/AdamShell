import unittest

from universe.universe import Universe
from quantum.cronenberg_pair_encounter import (
    CronenbergPairEncounter
)
from quantum.cronenberg_pair_encounter_resolver import (
    CronenbergPairEncounterResolver
)


class FixedEffectsRng:

    def __init__(self, effects):
        self.effects = list(effects)

    def random(self):
        return 0.1

    def sample(self, population, count):
        return list(self.effects)


class CronenbergQuantumPairTests(unittest.TestCase):

    def create_pair(self):
        universe = Universe()

        original = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("test"),
                "test",
                "quantum_pair"
            )
        )

        counterpart = (
            universe
            .create_cronenberg_quantum_counterpart(
                original
            )["counterpart"]
        )

        return universe, original, counterpart

    def test_counterpart_has_opposite_spin(self):
        universe, original, counterpart = (
            self.create_pair()
        )

        self.assertEqual(
            len(universe.cronenbergs),
            2
        )

        self.assertEqual(
            original.quantum_state["spin"],
            0.5
        )

        self.assertEqual(
            counterpart.quantum_state["spin"],
            -0.5
        )

        self.assertEqual(
            original.quantum_state["pair_id"],
            counterpart.quantum_state["pair_id"]
        )

        self.assertEqual(
            original.quantum_state[
                "counterpart_id"
            ],
            counterpart.id
        )

        self.assertEqual(
            counterpart.quantum_state[
                "counterpart_id"
            ],
            original.id
        )

    def test_pair_encounter_requires_same_location(self):
        _, original, counterpart = (
            self.create_pair()
        )

        detector = CronenbergPairEncounter()

        original.location = "meeting_place"
        counterpart.location = "quantum_layer"

        apart = detector.detect(
            original,
            counterpart,
            universe_tick=1
        )

        self.assertFalse(
            apart["encountered"]
        )

        self.assertEqual(
            apart["reason"],
            "different_location"
        )

        counterpart.location = "meeting_place"

        together = detector.detect(
            original,
            counterpart,
            universe_tick=2
        )

        self.assertTrue(
            together["encountered"]
        )

        self.assertEqual(
            together["pair_id"],
            original.quantum_state["pair_id"]
        )

    def test_spin_exchange(self):
        universe, original, counterpart = (
            self.create_pair()
        )

        original.location = "between_layers"
        counterpart.location = "between_layers"

        encounter = CronenbergPairEncounter().detect(
            original,
            counterpart,
            universe_tick=1
        )

        resolver = (
            CronenbergPairEncounterResolver(
                universe
            )
        )

        resolver.resolve(
            original,
            counterpart,
            encounter,
            rng=FixedEffectsRng(
                ["spin_exchange"]
            )
        )

        self.assertEqual(
            original.quantum_state["spin"],
            -0.5
        )

        self.assertEqual(
            counterpart.quantum_state["spin"],
            0.5
        )

    def test_property_sum(self):
        universe, original, counterpart = (
            self.create_pair()
        )

        original.location = "between_layers"
        counterpart.location = "between_layers"

        original.size = 1.2
        original.energy = 0.8

        counterpart.size = 1.5
        counterpart.energy = 1.1

        encounter = CronenbergPairEncounter().detect(
            original,
            counterpart,
            universe_tick=1
        )

        resolver = (
            CronenbergPairEncounterResolver(
                universe
            )
        )

        resolver.resolve(
            original,
            counterpart,
            encounter,
            rng=FixedEffectsRng(
                ["property_sum"]
            )
        )

        self.assertAlmostEqual(
            original.size,
            2.7
        )

        self.assertAlmostEqual(
            counterpart.size,
            2.7
        )

        self.assertAlmostEqual(
            original.energy,
            1.9
        )

        self.assertAlmostEqual(
            counterpart.energy,
            1.9
        )

    def test_property_equalization(self):
        universe, original, counterpart = (
            self.create_pair()
        )

        original.location = "between_layers"
        counterpart.location = "between_layers"

        original.size = 1.2
        original.energy = 0.8

        counterpart.size = 1.5
        counterpart.energy = 1.1

        encounter = CronenbergPairEncounter().detect(
            original,
            counterpart,
            universe_tick=1
        )

        resolver = (
            CronenbergPairEncounterResolver(
                universe
            )
        )

        resolver.resolve(
            original,
            counterpart,
            encounter,
            rng=FixedEffectsRng(
                ["property_equalization"]
            )
        )

        self.assertAlmostEqual(
            original.size,
            1.35
        )

        self.assertAlmostEqual(
            counterpart.size,
            1.35
        )

        self.assertAlmostEqual(
            original.energy,
            0.95
        )

        self.assertAlmostEqual(
            counterpart.energy,
            0.95
        )


if __name__ == "__main__":
    unittest.main()