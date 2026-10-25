import unittest
from copy import deepcopy

from quantum.cronenberg_pair_encounter import (
    CronenbergPairSpin,
    CronenbergQuantumPairEncounteredEvent,
)
from universe.universe import Universe
from universe.quantum_tick_result_state import (
    UniverseQuantumTickResult,
)
from quantum.cronenberg_pair_encounter_resolver import (
    CronenbergQuantumTickEffectResult,
    CronenbergPairEncounterResolvedEvent,
    CronenbergPairEncounterResolver,
    CronenbergPairResolvedEffect,
    CronenbergPairSurvivalResult,
)


class FakeCronenberg:

    def __init__(
        self,
        entity_id
    ):
        self.id = entity_id
        self.is_alive = True


class FixedEffectRng:

    def random(self):
        return 0.1

    def sample(
        self,
        population,
        count
    ):
        return [
            "both_survive"
        ]


class CronenbergPairEncounterResolverHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.resolver = (
            CronenbergPairEncounterResolver(
                object()
            )
        )

        self.first = FakeCronenberg(
            "first"
        )

        self.second = FakeCronenberg(
            "second"
        )

        self.encounter = (
            CronenbergQuantumPairEncounteredEvent(
                pair_id="pair-object-state",
                participants=(
                    self.first.id,
                    self.second.id,
                ),
                location="shared_kernel",
                universe_tick=7,
                spins=(
                    CronenbergPairSpin(
                        participant_id=self.first.id,
                        spin=0.5,
                    ),
                    CronenbergPairSpin(
                        participant_id=self.second.id,
                        spin=-0.5,
                    ),
                ),
            )
        )

    def resolve(self):
        return self.resolver.resolve(
            self.first,
            self.second,
            self.encounter,
            rng=FixedEffectRng(),
        )

    def test_history_uses_object_state(
        self
    ):
        result = self.resolve()

        event = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            CronenbergPairEncounterResolvedEvent,
        )

        self.assertEqual(
            event.participants,
            (
                "first",
                "second",
            ),
        )

        self.assertEqual(
            event.selected_effects,
            (
                "both_survive",
            ),
        )

        self.assertEqual(
            len(
                event.resolved_effects
            ),
            1,
        )

        self.assertIsInstance(
            event.resolved_effects[0],
            CronenbergPairResolvedEffect,
        )

        self.assertEqual(
            result.name,
            event.name,
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
            _ = event[
                "pair_id"
            ]

    def test_effect_payload_is_read_only(
        self
    ):
        self.resolve()

        effect = (
            self.resolver
            .history[-1]
            .resolved_effects[0]
        )

        self.assertIsInstance(
            effect.result,
            CronenbergPairSurvivalResult,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    effect.result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = effect.result[
                "first_alive"
            ]

        self.assertTrue(
            effect.result.first_alive
        )

    def test_boundary_snapshot_is_detached(
        self
    ):
        result = self.resolve()

        event = (
            self.resolver
            .history[-1]
        )

        snapshot = result.to_dict()

        snapshot[
            "participants"
        ][0] = "changed"

        snapshot[
            "selected_effects"
        ][0] = "changed"

        snapshot[
            "resolved_effects"
        ][0][
            "result"
        ][
            "first_alive"
        ] = False

        self.assertEqual(
            event.participants,
            (
                "first",
                "second",
            ),
        )

        self.assertEqual(
            event.selected_effects,
            (
                "both_survive",
            ),
        )

        self.assertTrue(
            event
            .resolved_effects[0]
            .result.first_alive
        )

    def test_quantum_tick_effect_preserves_object(
        self
    ):
        universe = Universe()
        universe.enable_quantum_layer()

        resolver = CronenbergPairEncounterResolver(
            universe
        )

        original_tick = universe.tick_quantum
        produced = []

        def capture_tick():
            result = original_tick()
            produced.append(result)
            return result

        universe.tick_quantum = capture_tick

        effect = resolver._quantum_tick()

        self.assertIsInstance(
            effect,
            CronenbergQuantumTickEffectResult,
        )
        self.assertEqual(effect.before_tick, 0)
        self.assertEqual(effect.after_tick, 1)

        self.assertIsInstance(
            effect.tick_result,
            UniverseQuantumTickResult,
        )
        self.assertIs(
            effect.tick_result,
            produced[0],
        )

        snapshot = effect.to_dict()

        self.assertIsInstance(
            snapshot["tick_result"],
            dict,
        )
        self.assertEqual(
            snapshot["tick_result"]["tick"],
            1,
        )

        snapshot["tick_result"]["tick"] = 99

        self.assertEqual(
            effect.tick_result.tick,
            1,
        )

    def test_history_rejects_mapping_and_is_deepcopy_safe(
        self
    ):
        self.resolve()

        event = (
            self.resolver
            .history[-1]
        )

        with self.assertRaises(
            TypeError
        ):
            (
                self.resolver
                .record_resolution(
                    {
                        "name": (
                            "cronenberg_quantum_pair_"
                            "encounter_resolved"
                        ),
                    }
                )
            )

        copied_history = deepcopy(
            self.resolver.history
        )

        self.assertIs(
            copied_history[0],
            event,
        )


if __name__ == "__main__":
    unittest.main()
