import unittest

from core.entity.cronenberg_system.quantum_state import (
    CronenbergQuantumState
)
from quantum.cronenberg_pair_encounter import (
    CronenbergPairEncounter
)
from quantum.cronenberg_pair_encounter_resolver import (
    CronenbergPairEncounterResolver
)
from universe.universe import Universe


class SpinExchangeRng:

    def random(self):
        return 0.1

    def sample(self, population, count):
        return ["spin_exchange"]


class CronenbergQuantumObjectStateTests(
    unittest.TestCase
):

    def _create_pair(self):
        universe = Universe()
        original = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("test"),
                "test",
                "quantum_object_state",
            )
        )
        counterpart = (
            universe
            .create_cronenberg_quantum_counterpart(
                original
            )["counterpart"]
        )

        return universe, original, counterpart

    def _assert_object_only(self, value):
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

        with self.assertRaises(TypeError):
            _ = value["spin"]

    def test_quantum_state_has_no_mapping_api(
        self
    ):
        state = CronenbergQuantumState()

        self._assert_object_only(state)
        self.assertEqual(state.spin, 0.5)
        self.assertFalse(state.entangled)

    def test_counterpart_pairing_mutates_same_objects(
        self
    ):
        universe = Universe()
        original = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("test"),
                "test",
                "quantum_object_state",
            )
        )
        original_state = original.quantum_state

        counterpart = (
            universe
            .create_cronenberg_quantum_counterpart(
                original
            )["counterpart"]
        )

        self.assertIs(
            original.quantum_state,
            original_state
        )
        self.assertIsInstance(
            counterpart.quantum_state,
            CronenbergQuantumState
        )
        self.assertTrue(original_state.entangled)
        self.assertEqual(
            original_state.counterpart_id,
            counterpart.id
        )
        self.assertEqual(
            counterpart.quantum_state
            .counterpart_id,
            original.id
        )
        self.assertEqual(
            original_state.pair_id,
            counterpart.quantum_state.pair_id
        )
        self.assertEqual(
            {
                original_state.spin,
                counterpart.quantum_state.spin,
            },
            {0.5, -0.5}
        )

    def test_spin_exchange_keeps_state_identity(
        self
    ):
        universe, original, counterpart = (
            self._create_pair()
        )
        original.location = "shared_kernel"
        counterpart.location = "shared_kernel"
        original_state = original.quantum_state
        counterpart_state = (
            counterpart.quantum_state
        )
        encounter = CronenbergPairEncounter().detect(
            original,
            counterpart,
            universe_tick=1,
        )

        CronenbergPairEncounterResolver(
            universe
        ).resolve(
            original,
            counterpart,
            encounter,
            rng=SpinExchangeRng(),
        )

        self.assertIs(
            original.quantum_state,
            original_state
        )
        self.assertIs(
            counterpart.quantum_state,
            counterpart_state
        )
        self.assertEqual(original_state.spin, -0.5)
        self.assertEqual(counterpart_state.spin, 0.5)

    def test_public_state_is_detached_dict(
        self
    ):
        _, original, counterpart = (
            self._create_pair()
        )

        snapshot = original.public_state

        self.assertIsInstance(
            snapshot["quantum_state"],
            dict
        )
        snapshot["quantum_state"][
            "spin"
        ] = 99.0
        snapshot["quantum_state"][
            "counterpart_id"
        ] = "changed"

        self.assertEqual(
            original.quantum_state.spin,
            0.5
        )
        self.assertEqual(
            original.quantum_state.counterpart_id,
            counterpart.id
        )

    def test_pair_consumption_resets_new_state(
        self
    ):
        universe, original, counterpart = (
            self._create_pair()
        )
        original.location = "shared_kernel"
        counterpart.location = "shared_kernel"

        result = (
            universe
            .resolve_quantum_pair_consumption(
                original,
                counterpart,
            )
        )
        recombined = result["recombined"]

        self.assertIsInstance(
            recombined.quantum_state,
            CronenbergQuantumState
        )
        self.assertEqual(
            recombined.quantum_state.spin,
            0.0
        )
        self.assertFalse(
            recombined.quantum_state.entangled
        )
        self.assertIsNone(
            recombined.quantum_state.pair_id
        )
        self.assertFalse(
            original.quantum_state.entangled
        )
        self.assertFalse(
            counterpart.quantum_state.entangled
        )


if __name__ == "__main__":
    unittest.main()
