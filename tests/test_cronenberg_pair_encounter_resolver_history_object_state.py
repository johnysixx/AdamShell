import unittest
from copy import deepcopy

from quantum.cronenberg_pair_encounter_resolver import (
    CronenbergPairEncounterResolvedEvent,
    CronenbergPairEncounterResolver,
    CronenbergPairResolvedEffect,
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

        self.encounter = {
            "encountered": True,
            "pair_id": (
                "pair-object-state"
            ),
            "participants": [
                self.first.id,
                self.second.id,
            ],
            "location": "shared_kernel",
            "universe_tick": 7,
        }

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
            result["name"],
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

        with self.assertRaises(
            TypeError
        ):
            effect.result[
                "first_alive"
            ] = False

        self.assertTrue(
            effect.result[
                "first_alive"
            ]
        )

    def test_boundary_snapshot_is_detached(
        self
    ):
        result = self.resolve()

        event = (
            self.resolver
            .history[-1]
        )

        result[
            "participants"
        ][0] = "changed"

        result[
            "selected_effects"
        ][0] = "changed"

        result[
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
            .result[
                "first_alive"
            ]
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
