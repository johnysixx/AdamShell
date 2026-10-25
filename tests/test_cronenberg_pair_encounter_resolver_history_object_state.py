import unittest
from copy import deepcopy
from types import SimpleNamespace

from universe.cronenberg_quantum_result_state import (
    CronenbergQuantumPairMergedEvent,
    CronenbergQuantumPairMergeResult,
    CronenbergQuantumPairConsumedEvent,
    CronenbergQuantumPairConsumptionResult,
)

from quantum.cronenberg_pair_encounter import (
    CronenbergPairSpin,
    CronenbergQuantumPairEncounteredEvent,
)
from universe.universe import Universe
from quantum.error_boundary import (
    QuantumErrorResult,
)
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

    def test_effect_preserves_domain_result_identity(
        self
    ):
        produced = CronenbergPairSurvivalResult(
            first_alive=True,
            second_alive=True,
            first_id="first",
            second_id="second",
        )

        effect = CronenbergPairResolvedEffect(
            effect="both_survive",
            result=produced,
        )

        self.assertIs(effect.result, produced)
        self.assertIs(deepcopy(effect), effect)

        snapshot = effect.to_dict()

        snapshot["result"]["first_alive"] = False

        self.assertTrue(produced.first_alive)

    def test_effect_rejects_mapping_payloads(
        self
    ):
        for invalid in (
            {},
            {"first_alive": True},
            [1, 2],
            object(),
            None,
        ):
            with self.subTest(
                result_type=type(invalid).__name__
            ):
                with self.assertRaises(TypeError):
                    CronenbergPairResolvedEffect(
                        effect="both_survive",
                        result=invalid,
                    )

    def test_quantum_transformation_exports_only_ids(
        self
    ):
        first = SimpleNamespace(id="first")
        second = SimpleNamespace(id="second")
        merged = SimpleNamespace(id="merged")

        merge_event = CronenbergQuantumPairMergedEvent(
            pair_id="pair_1",
            parents=("first", "second"),
            merged_id="merged",
            merged_size=3.0,
            merged_energy=5.0,
            merged_spin=0.0,
            source="test",
            tick=1,
        )

        merge_result = CronenbergQuantumPairMergeResult(
            first=first,
            second=second,
            merged=merged,
            event=merge_event,
        )

        merge_effect = CronenbergPairResolvedEffect(
            effect="quantum_merge",
            result=merge_result,
        )

        self.assertIs(
            merge_effect.result,
            merge_result,
        )
        self.assertIs(merge_result.merged, merged)

        merge_snapshot = merge_effect.to_dict()

        self.assertEqual(
            merge_snapshot["result"]["first"],
            "first",
        )
        self.assertEqual(
            merge_snapshot["result"]["second"],
            "second",
        )
        self.assertEqual(
            merge_snapshot["result"]["merged"],
            "merged",
        )

        recombined = SimpleNamespace(id="recombined")

        consumption_event = (
            CronenbergQuantumPairConsumedEvent(
                pair_id="pair_1",
                participants=("first", "second"),
                recombined_id="recombined",
                combined_size=3.0,
                recombined_size=1.5,
                combined_energy=5.0,
                retained_energy=2.0,
                released_energy=1.75,
                dark_energy_created=1.25,
                tick=2,
            )
        )

        consumption_result = (
            CronenbergQuantumPairConsumptionResult(
                first=first,
                second=second,
                recombined=recombined,
                event=consumption_event,
            )
        )

        consumption_effect = CronenbergPairResolvedEffect(
            effect="quantum_pair_consumption",
            result=consumption_result,
        )

        self.assertIs(
            consumption_effect.result,
            consumption_result,
        )
        self.assertIs(
            consumption_result.recombined,
            recombined,
        )

        snapshot = consumption_effect.to_dict()

        self.assertEqual(
            snapshot["result"]["first"],
            "first",
        )
        self.assertEqual(
            snapshot["result"]["second"],
            "second",
        )
        self.assertEqual(
            snapshot["result"]["recombined"],
            "recombined",
        )

        snapshot["result"]["recombined"] = "changed"

        self.assertEqual(
            recombined.id,
            "recombined",
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

    def test_quantum_tick_error_preserves_entity_identity(
        self,
    ):
        cronenberg = FakeCronenberg(
            "cronenberg_error"
        )

        error = QuantumErrorResult(
            error_type="RuntimeError",
            error_message="quantum failure",
            cronenberg=cronenberg,
        )

        class ErrorUniverse:
            def __init__(self):
                self.quantum_state = type(
                    "QuantumState",
                    (),
                    {"tick_count": 4},
                )()

            def tick_quantum(self):
                return error

        resolver = CronenbergPairEncounterResolver(
            ErrorUniverse()
        )

        effect = resolver._quantum_tick()

        self.assertEqual(effect.before_tick, 4)
        self.assertEqual(effect.after_tick, 4)

        self.assertIs(
            effect.tick_result,
            error,
        )
        self.assertIs(
            effect.tick_result.cronenberg,
            cronenberg,
        )

        snapshot = effect.to_dict()

        self.assertEqual(
            snapshot["tick_result"]["cronenberg"],
            {"id": "cronenberg_error"},
        )

        snapshot["tick_result"][
            "cronenberg"
        ]["id"] = "changed"

        self.assertEqual(
            cronenberg.id,
            "cronenberg_error",
        )
        self.assertIs(
            effect.tick_result,
            error,
        )

    def test_disabled_quantum_tick_keeps_none(
        self,
    ):
        class DisabledUniverse:
            def __init__(self):
                self.quantum_state = type(
                    "QuantumState",
                    (),
                    {"tick_count": 0},
                )()

            def tick_quantum(self):
                return None

        resolver = CronenbergPairEncounterResolver(
            DisabledUniverse()
        )

        effect = resolver._quantum_tick()

        self.assertEqual(effect.before_tick, 0)
        self.assertEqual(effect.after_tick, 0)
        self.assertIsNone(effect.tick_result)

        self.assertIsNone(
            effect.to_dict()["tick_result"]
        )

    def test_quantum_tick_result_validates_contract(
        self,
    ):
        for invalid in (
            {"tick": 1},
            object(),
        ):
            with self.assertRaises(TypeError):
                CronenbergQuantumTickEffectResult(
                    before_tick=0,
                    after_tick=1,
                    tick_result=invalid,
                )

        with self.assertRaises(ValueError):
            CronenbergQuantumTickEffectResult(
                before_tick=2,
                after_tick=1,
                tick_result=None,
            )

        result = UniverseQuantumTickResult(
            tick=1,
            collapse_count=1,
            fluctuation=0.01,
            uncertainty=0.005,
            entropy_delta=0.0005,
            entropy_total=0.0005,
        )

        with self.assertRaises(ValueError):
            CronenbergQuantumTickEffectResult(
                before_tick=0,
                after_tick=2,
                tick_result=result,
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
