import unittest

from core.entity.serpent_d20 import (
    SerpentD20,
    SerpentD20HiddenResolutionEvent,
    SerpentD20PublicRollEvent,
    SerpentResolvedConsequence,
)
from idea_entities import IdeaEntities
from universe.universe import Universe
from universe.quantum_tick_result_state import (
    UniverseQuantumTickResult,
)
from quantum.serpent_consequence_executor import (
    SerpentConsequenceExecutor,
)


class FixedSerpentRng:

    def randint(
        self,
        minimum,
        maximum,
    ):
        if maximum == 20:
            return 7

        return minimum

    def random(self):
        return 0.5

    def sample(
        self,
        values,
        count,
    ):
        return list(values)[:count]

    def choice(
        self,
        values,
    ):
        return list(values)[0]

    def shuffle(
        self,
        values,
    ):
        return None


class FakeSerpentUniverse:

    def __init__(self):
        self.result = UniverseQuantumTickResult(
            tick=1,
            collapse_count=1,
            fluctuation=0.01,
            uncertainty=0.005,
            entropy_delta=0.0005,
            entropy_total=0.0005,
        )

    def tick_quantum(self):
        return self.result


class MutableSerializedSerpentOutcome:

    def __init__(self):
        self.metadata = {
            "nested": {
                "notes": ["original"],
            },
        }

    def to_dict(self):
        return {
            "metadata": self.metadata,
        }


class MutableSerializedSerpentRoll(
    SerpentD20PublicRollEvent
):

    def __init__(self):
        super().__init__(
            roll_id="b41_public_roll",
            roller="serpent",
            die="serpent_d20",
            value=7,
            roll_number=1,
            universe_tick=12,
        )

        object.__setattr__(
            self,
            "metadata",
            {
                "history": {
                    "notes": ["original"],
                },
            },
        )

    def to_dict(self):
        snapshot = super().to_dict()
        snapshot["metadata"] = self.metadata
        return snapshot


class SerpentD20ObjectStateTests(
    unittest.TestCase
):

    def test_public_history_uses_object_state(
        self
    ):
        die = SerpentD20()

        result = die.roll_publicly(
            rng=FixedSerpentRng(),
            universe_tick=12,
        )

        event = die.public_history[-1]

        self.assertIsInstance(
            event,
            SerpentD20PublicRollEvent,
        )
        self.assertEqual(
            event.value,
            7,
        )
        self.assertEqual(
            event.universe_tick,
            12,
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

        self.assertIs(
            result,
            event,
        )

        snapshot = result.to_dict()
        snapshot["value"] = 99

        self.assertEqual(
            event.value,
            7,
        )

        state = die.public_state

        state[
            "public_history"
        ][0]["value"] = 99

        self.assertEqual(
            event.value,
            7,
        )

    def test_public_roll_snapshot_detaches_nested_data(self):
        die = SerpentD20()
        event = MutableSerializedSerpentRoll()

        die.record_public_roll(event)

        first = die.public_state
        second = die.public_state

        first["public_history"][0]["metadata"][
            "history"
        ]["notes"].append("snapshot_only")

        self.assertEqual(
            event.metadata["history"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["public_history"][0][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        self.assertEqual(
            die.public_state["public_history"][0][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        self.assertIs(
            die.public_history[0],
            event,
        )

        self.assertIsNot(
            first["public_history"][0][
                "metadata"
            ],
            event.metadata,
        )

        self.assertEqual(
            first["public_history"][0]["value"],
            7,
        )

    def test_public_roll_snapshot_ignores_later_live_changes(self):
        die = SerpentD20()
        event = MutableSerializedSerpentRoll()

        die.record_public_roll(event)

        snapshot = die.public_state

        event.metadata["history"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot["public_history"][0][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        current = die.public_state

        self.assertEqual(
            current["public_history"][0][
                "metadata"
            ]["history"]["notes"],
            ["original", "live_change"],
        )

        snapshot["public_history"].clear()

        self.assertEqual(
            len(die.public_history),
            1,
        )

        self.assertIs(
            die.public_history[0],
            event,
        )

        self.assertEqual(
            die._hidden_history,
            [],
        )

    def test_world_public_roll_snapshot_preserves_identity(self):
        universe = Universe()
        layer = IdeaEntities(universe)

        die = layer.serpent_d20
        event = MutableSerializedSerpentRoll()

        die.record_public_roll(event)

        layer.write_to_world()

        world_snapshot = universe.world[
            "idea_entities"
        ]["serpent_d20"]

        public_snapshot = layer.public_state[
            "serpent_d20"
        ]

        self.assertIs(
            layer.serpent_d20,
            die,
        )

        self.assertIs(
            die.public_history[0],
            event,
        )

        world_snapshot["public_history"][0][
            "metadata"
        ]["history"]["notes"].append(
            "snapshot_only"
        )

        self.assertEqual(
            event.metadata["history"]["notes"],
            ["original"],
        )

        self.assertEqual(
            public_snapshot["public_history"][0][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        event.metadata["history"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            public_snapshot["public_history"][0][
                "metadata"
            ]["history"]["notes"],
            ["original"],
        )

        current = layer.public_state[
            "serpent_d20"
        ]

        self.assertEqual(
            current["public_history"][0][
                "metadata"
            ]["history"]["notes"],
            ["original", "live_change"],
        )

        self.assertEqual(
            world_snapshot["public_history"][0][
                "metadata"
            ]["history"]["notes"],
            ["original", "snapshot_only"],
        )

        self.assertNotIn(
            "_hidden_history",
            world_snapshot,
        )

        self.assertEqual(
            die._hidden_history,
            [],
        )

        self.assertIs(
            die.public_history[0],
            event,
        )

    def test_public_history_rejects_mapping_event(
        self
    ):
        die = SerpentD20()

        with self.assertRaises(TypeError):
            die.record_public_roll(
                {
                    "name": "serpent_d20_rolled",
                }
            )


    def test_hidden_history_uses_object_state(
        self
    ):
        die = SerpentD20()

        public = die.roll_publicly(
            rng=FixedSerpentRng(),
            universe_tick=12,
        )

        event = (
            die._hidden_history[-1]
        )

        self.assertIsInstance(
            event,
            SerpentD20HiddenResolutionEvent,
        )

        self.assertEqual(
            event.roll_id,
            public.roll_id,
        )

        self.assertEqual(
            event.value,
            7,
        )

        self.assertIsInstance(
            event.possible_consequences,
            tuple,
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
            _ = event["roll_id"]

        resolved = (
            die.hidden_resolution_for(
                public.roll_id
            )
        )

        self.assertIs(
            resolved,
            event,
        )

        snapshot = resolved.to_dict()
        snapshot[
            "possible_consequences"
        ].append(
            "changed"
        )

        self.assertNotIn(
            "changed",
            event.possible_consequences,
        )

    def test_hidden_history_rejects_mapping_event(
        self
    ):
        die = SerpentD20()

        with self.assertRaises(TypeError):
            die.record_hidden_resolution(
                {
                    "name": (
                        "serpent_d20_hidden_resolution"
                    ),
                }
            )

    def test_resolved_consequences_use_object_state(
        self
    ):
        die = SerpentD20()

        public = die.roll_publicly(
            rng=FixedSerpentRng(),
        )

        executor = (
            SerpentConsequenceExecutor(
                FakeSerpentUniverse()
            )
        )

        result = (
            executor.execute_hidden_plan(
                die,
                public.roll_id,
            )
        )

        hidden = (
            die._hidden_history[-1]
        )

        consequence = (
            hidden
            .resolved_consequences[0]
        )

        self.assertIsInstance(
            consequence,
            SerpentResolvedConsequence,
        )

        self.assertEqual(
            consequence.consequence,
            "quantum_tick",
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    consequence,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = consequence[
                "consequence"
            ]

        snapshot = result.to_dict()
        snapshot[
            "resolved_consequences"
        ][0][
            "result"
        ][
            "tick"
        ] = 99

        self.assertIsInstance(
            consequence.result,
            UniverseQuantumTickResult,
        )
        self.assertEqual(
            consequence.result.tick,
            1,
        )
        self.assertIs(
            consequence.result,
            executor.universe.result,
        )

    def test_consequence_result_snapshot_is_detached(self):
        outcome = MutableSerializedSerpentOutcome()

        consequence = SerpentResolvedConsequence(
            consequence="custom",
            result=outcome,
        )

        stored = consequence.result

        first = consequence.to_dict()
        second = consequence.to_dict()

        first["result"]["metadata"][
            "nested"
        ]["notes"].append("snapshot_only")

        self.assertEqual(
            stored.metadata["nested"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["result"]["metadata"][
                "nested"
            ]["notes"],
            ["original"],
        )

        self.assertEqual(
            consequence.to_dict()["result"][
                "metadata"
            ]["nested"]["notes"],
            ["original"],
        )

        self.assertEqual(
            first["consequence"],
            "custom",
        )

        self.assertIs(
            consequence.result,
            stored,
        )

        self.assertIsNot(
            first["result"]["metadata"],
            stored.metadata,
        )

        self.assertIsNot(
            stored,
            outcome,
        )

    def test_consequence_snapshot_ignores_live_result_changes(self):
        consequence = SerpentResolvedConsequence(
            consequence="custom",
            result=MutableSerializedSerpentOutcome(),
        )

        stored = consequence.result
        snapshot = consequence.to_dict()

        stored.metadata["nested"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot["result"]["metadata"][
                "nested"
            ]["notes"],
            ["original"],
        )

        current = consequence.to_dict()

        self.assertEqual(
            current["result"]["metadata"][
                "nested"
            ]["notes"],
            ["original", "live_change"],
        )

        snapshot["result"]["metadata"][
            "nested"
        ]["notes"].append("snapshot_only")

        self.assertEqual(
            stored.metadata["nested"]["notes"],
            ["original", "live_change"],
        )

        self.assertIs(
            consequence.result,
            stored,
        )

    def test_hidden_resolution_snapshot_keeps_object_identity(self):
        consequence = SerpentResolvedConsequence(
            consequence="custom",
            result=MutableSerializedSerpentOutcome(),
        )

        stored = consequence.result

        hidden = SerpentD20HiddenResolutionEvent(
            roll_id="b40_hidden_roll",
            value=7,
            fire_threshold_reached=False,
            possible_consequences=("custom",),
            intensity="moderate",
            all_effects_triggered=False,
            resolved_consequences=(consequence,),
        )

        die = SerpentD20()
        die.record_hidden_resolution(hidden)

        self.assertIs(
            die.hidden_resolution_for("b40_hidden_roll"),
            hidden,
        )

        self.assertIs(
            hidden.resolved_consequences[0],
            consequence,
        )

        self.assertIs(
            consequence.result,
            stored,
        )

        first = hidden.to_dict()
        second = hidden.to_dict()

        first["resolved_consequences"][0][
            "result"
        ]["metadata"]["nested"]["notes"].append(
            "snapshot_only"
        )

        self.assertEqual(
            stored.metadata["nested"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["resolved_consequences"][0][
                "result"
            ]["metadata"]["nested"]["notes"],
            ["original"],
        )

        stored.metadata["nested"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            second["resolved_consequences"][0][
                "result"
            ]["metadata"]["nested"]["notes"],
            ["original"],
        )

        current = hidden.to_dict()

        self.assertEqual(
            current["resolved_consequences"][0][
                "result"
            ]["metadata"]["nested"]["notes"],
            ["original", "live_change"],
        )

        self.assertIs(
            die._hidden_history[0],
            hidden,
        )

        self.assertIs(
            hidden.resolved_consequences[0],
            consequence,
        )

        self.assertNotIn(
            "resolved_consequences",
            die.public_state,
        )

    def test_resolved_consequences_reject_mapping_state(
        self
    ):
        die = SerpentD20()

        public = die.roll_publicly(
            rng=FixedSerpentRng(),
        )

        with self.assertRaises(TypeError):
            die.record_resolved_consequences(
                public.roll_id,
                [
                    {
                        "consequence": (
                            "quantum_tick"
                        ),
                        "result": {
                            "tick": 1,
                        },
                    },
                ],
            )


if __name__ == "__main__":
    unittest.main()
