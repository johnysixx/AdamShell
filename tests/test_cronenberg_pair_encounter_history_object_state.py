import unittest

from universe.universe import Universe
from quantum.cronenberg_pair_encounter import (
    CronenbergPairEncounter,
    CronenbergPairSpin,
    CronenbergQuantumPairEncounteredEvent,
)


class CronenbergPairEncounterHistoryObjectStateTests(
    unittest.TestCase
):

    def create_pair(self):
        universe = Universe()

        original = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("test"),
                "test",
                "pair_history",
            )
        )

        counterpart = (
            universe
            .create_cronenberg_quantum_counterpart(
                original
            )["counterpart"]
        )

        original.location = (
            "shared_kernel"
        )

        counterpart.location = (
            "shared_kernel"
        )

        return (
            universe,
            original,
            counterpart,
        )

    def test_history_uses_object_state(
        self
    ):
        _, original, counterpart = (
            self.create_pair()
        )

        detector = (
            CronenbergPairEncounter()
        )

        result = detector.detect(
            original,
            counterpart,
            universe_tick=7,
        )

        event = (
            detector.history[-1]
        )

        self.assertIsInstance(
            event,
            CronenbergQuantumPairEncounteredEvent,
        )

        self.assertEqual(
            event.participants,
            (
                original.id,
                counterpart.id,
            ),
        )

        self.assertTrue(
            all(
                isinstance(
                    spin,
                    CronenbergPairSpin,
                )
                for spin
                in event.spins
            )
        )

        self.assertEqual(
            result[
                "spins"
            ][
                original.id
            ],
            original.quantum_state.spin,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = event["pair_id"]

    def test_boundary_snapshot_is_detached(
        self
    ):
        _, original, counterpart = (
            self.create_pair()
        )

        detector = (
            CronenbergPairEncounter()
        )

        result = detector.detect(
            original,
            counterpart,
            universe_tick=8,
        )

        event = (
            detector.history[-1]
        )

        result[
            "participants"
        ][0] = "changed"

        result[
            "spins"
        ][
            original.id
        ] = 99.0

        result[
            "resolution"
        ] = {
            "changed": True,
        }

        self.assertEqual(
            event.participants[0],
            original.id,
        )

        first_spin = next(
            spin
            for spin
            in event.spins
            if (
                spin.participant_id
                == original.id
            )
        )

        self.assertEqual(
            first_spin.spin,
            original.quantum_state.spin,
        )

        self.assertIsNone(
            event.resolution
        )

    def test_universe_resolution_boundary_stays_dict_based(
        self
    ):
        (
            universe,
            original,
            counterpart,
        ) = self.create_pair()

        original.tick = (
            lambda current_universe: None
        )

        counterpart.tick = (
            lambda current_universe: None
        )

        (
            universe
            .cronenberg_pair_encounter_resolver
            .resolve
        ) = (
            lambda **kwargs: {
                "name":
                    "test_resolution",
                "resolved": True,
            }
        )

        events = (
            universe
            .detect_cronenberg_pair_encounters()
        )

        self.assertEqual(
            events[0]["resolution"],
            {
                "name":
                    "test_resolution",
                "resolved": True,
            },
        )

        history_event = (
            universe
            .cronenberg_pair_encounter
            .history[-1]
        )

        self.assertIsInstance(
            history_event,
            CronenbergQuantumPairEncounteredEvent,
        )

        self.assertIsNone(
            history_event.resolution
        )

    def test_history_rejects_mapping_event(
        self
    ):
        detector = (
            CronenbergPairEncounter()
        )

        with self.assertRaises(
            TypeError
        ):
            detector.record_event(
                {
                    "name": (
                        "cronenberg_quantum_pair_"
                        "encountered"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
