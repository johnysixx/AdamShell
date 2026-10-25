import unittest

from core.entity.quantum_die import (
    QuantumDie,
    QuantumDieRollEvent,
)
from core.entity.quantum_die_roll_result_state import (
    QuantumDieRollResult,
)
from quantum.quantum_die_resolver import (
    QuantumDieResolution,
    QuantumDieResolutionEvent,
)
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

        self.assertIsInstance(
            result,
            QuantumDieRollResult,
        )
        self.assertIs(result.roll_event, event)
        self.assertIs(
            result.resolution_event,
            universe.quantum_die_resolver.history[0],
        )
        self.assertEqual(result.roll_event.value, 7)

        with self.assertRaises(TypeError):
            _ = result["value"]

        exported = result.to_dict()
        self.assertEqual(exported["value"], 7)

        exported["value"] = 99
        self.assertEqual(result.roll_event.value, 7)

    def test_resolver_history_uses_object_state(
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
            .quantum_die_resolver
            .history[0]
        )

        self.assertIsInstance(
            event,
            QuantumDieResolutionEvent,
        )

        self.assertIsInstance(
            event.resolution,
            QuantumDieResolution,
        )

        self.assertEqual(
            event.value,
            7,
        )

        self.assertEqual(
            event.resolution.result,
            "single_cronenberg_manifested",
        )

        for value, key in (
            (
                event,
                "value",
            ),
            (
                event.resolution,
                "result",
            ),
        ):
            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
            ):
                self.assertFalse(
                    hasattr(
                        value,
                        mapping_method,
                    )
                )

            with self.assertRaises(
                TypeError
            ):
                _ = value[key]

        snapshot = event.to_dict()

        snapshot[
            "resolution"
        ][
            "result"
        ] = "changed"

        self.assertEqual(
            event.resolution.result,
            "single_cronenberg_manifested",
        )

        self.assertIs(
            result.resolution_event,
            event,
        )
        self.assertEqual(
            result.resolution_event.resolution.result,
            "single_cronenberg_manifested",
        )

        exported = result.to_dict()
        self.assertEqual(
            exported["resolution"]["resolution"]["result"],
            "single_cronenberg_manifested",
        )

        exported["resolution"]["resolution"]["result"] = (
            "changed"
        )

        self.assertEqual(
            result.resolution_event.resolution.result,
            "single_cronenberg_manifested",
        )

    def test_roll_without_resolver_returns_object(self):
        die = QuantumDie(resolver=None)

        result = die.roll(
            rng=SequenceRng([4])
        )

        self.assertIsInstance(
            result,
            QuantumDieRollResult,
        )
        self.assertIs(
            result.roll_event,
            die.history[0],
        )
        self.assertIsNone(
            result.resolution_event
        )

        self.assertEqual(
            result.to_dict(),
            {
                "die": "quantum_d20",
                "value": 4,
                "roll_number": 1,
                "visibility": "universe_only",
            },
        )

        with self.assertRaises(TypeError):
            _ = result["value"]

    def test_roll_result_rejects_invalid_objects(self):
        with self.assertRaises(TypeError):
            QuantumDieRollResult(
                roll_event={},
            )

        event = QuantumDieRollEvent(
            die="quantum_d20",
            value=4,
            roll_number=1,
        )

        with self.assertRaises(TypeError):
            QuantumDieRollResult(
                roll_event=event,
                resolution_event={},
            )

        mismatch = QuantumDieResolutionEvent(
            die="quantum_d20",
            value=7,
            roll_number=1,
            source="test",
            resolution=QuantumDieResolution(
                result="test_resolution",
            ),
        )

        with self.assertRaises(ValueError):
            QuantumDieRollResult(
                roll_event=event,
                resolution_event=mismatch,
            )

    def test_resolver_rejects_mapping_roll_event(
        self
    ):
        universe = Universe()

        with self.assertRaises(TypeError):
            (
                universe
                .quantum_die_resolver
                .resolve(
                    {
                        "die": "quantum_d20",
                        "value": 7,
                        "roll_number": 1,
                    }
                )
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
            result.resolution_event.resolution.result
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