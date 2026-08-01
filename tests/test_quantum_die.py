import unittest

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

            pair_id = quantum_state[
                "pair_id"
            ]

            self.assertIsNotNone(pair_id)

            self.assertTrue(
                quantum_state[
                    "entangled"
                ]
            )

            self.assertTrue(
                quantum_state[
                    "counterpart_manifested"
                ]
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
                    first.quantum_state[
                        "spin"
                    ],
                    second.quantum_state[
                        "spin"
                    ]
                },
                {
                    0.5,
                    -0.5
                }
            )

            self.assertEqual(
                first.quantum_state[
                    "counterpart_id"
                ],
                second.id
            )

            self.assertEqual(
                second.quantum_state[
                    "counterpart_id"
                ],
                first.id
            )


if __name__ == "__main__":
    unittest.main()