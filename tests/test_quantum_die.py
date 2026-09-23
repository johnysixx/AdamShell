import unittest

from core.entity.quantum_die import QuantumDieRollEvent
from universe.universe import Universe


class SequenceRng:

    def __init__(self, values):
        self.values = iter(values)

    def randint(self, minimum, maximum):
        value = next(self.values)

        if value < minimum or value > maximum:
            raise ValueError(
                f"Test roll {value} is outside "
                f"{minimum}..{maximum}."
            )

        return value


class QuantumDieTests(unittest.TestCase):

    def test_roll_history_uses_object_state(
        self
    ):
        universe = Universe()
        rng = SequenceRng(
            [7]
        )

        result = universe.quantum_die.roll(
            rng=rng
        )

        event = (
            universe
            .quantum_die
            .history[0]
        )

        self.assertIsInstance(
            event,
            QuantumDieRollEvent,
        )

        self.assertEqual(
            event.die,
            "quantum_d20",
        )
        self.assertEqual(
            event.value,
            7,
        )
        self.assertEqual(
            event.roll_number,
            1,
        )
        self.assertEqual(
            event.visibility,
            "universe_only",
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

        with self.assertRaises(TypeError):
            _ = event["value"]

        snapshot = event.to_dict()

        snapshot["value"] = 99

        self.assertEqual(
            event.value,
            7,
        )

        self.assertEqual(
            result["value"],
            7,
        )

    def test_sequence_creates_two_quantum_pairs(self):
        universe = Universe()
        rng = SequenceRng(
            [1, 20, 7, 20]
        )

        results = [
            universe.quantum_die.roll(
                rng=rng
            )
            for _ in range(4)
        ]

        resolution_names = [
            result[
                "resolution"
            ][
                "resolution"
            ][
                "result"
            ]
            for result in results
        ]

        self.assertEqual(
            resolution_names,
            [
                "single_cronenberg_manifested",
                (
                    "existing_cronenberg_"
                    "counterpart_manifested"
                ),
                "single_cronenberg_manifested",
                (
                    "existing_cronenberg_"
                    "counterpart_manifested"
                )
            ]
        )

        self.assertEqual(
            universe.quantum_die.roll_count,
            4
        )

        self.assertEqual(
            universe.quantum_die_resolver
            .public_state[
                "resolution_count"
            ],
            4
        )

        self.assertEqual(
            len(universe.cronenbergs),
            4
        )

        pair_groups = {}

        for cronenberg in universe.cronenbergs:
            quantum_state = (
                cronenberg.quantum_state
            )

            pair_id = quantum_state.pair_id

            self.assertIsNotNone(pair_id)

            self.assertTrue(
                quantum_state.entangled
            )

            self.assertTrue(
                quantum_state.counterpart_manifested
            )

            pair_groups.setdefault(
                pair_id,
                []
            ).append(cronenberg)

        self.assertEqual(
            len(pair_groups),
            2
        )

        for pair in pair_groups.values():
            self.assertEqual(
                len(pair),
                2
            )

            first, second = pair

            self.assertEqual(
                {
                    first.quantum_state.spin,
                    second.quantum_state.spin
                },
                {
                    0.5,
                    -0.5
                }
            )

            self.assertEqual(
                first.quantum_state.counterpart_id,
                second.id
            )

            self.assertEqual(
                second.quantum_state.counterpart_id,
                first.id
            )


if __name__ == "__main__":
    unittest.main()