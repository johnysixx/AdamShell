import unittest

from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatKnownScentTarget,
)
from cats.cat_mind import CatMind
from cats.cat_perception_state import (
    CatPerceptionState,
)


class CatKnownScentTargetObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="known_scent_cat",
            color="black",
            fur_length="short",
        )

    def test_target_is_clean_object(
        self
    ):
        target = CatKnownScentTarget(
            identity="cat:pazuzu",
            layer="quantum_layer",
            position={
                "x": 1.0,
                "y": 0.0,
                "z": 0.0,
            },
            source_id="trace",
            age_ticks=5,
            freshness=0.9,
            trail_direction=CatScentTrailDirection(
                inferred=True,
            ),
        )

        self.assertFalse(
            hasattr(
                target,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                target,
                "__getitem__",
            )
        )

        self.assertEqual(
            target.identity,
            "cat:pazuzu",
        )

        self.assertEqual(
            target.age_ticks,
            5,
        )

    def test_consider_builds_known_scent_target(
        self
    ):
        from cats.cat_knowledge import (
            CatKnowledge
        )

        self.cat.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }

        self.cat.current_layer = (
            "quantum_layer"
        )

        CatKnowledge.remember_scent_place(
            cat=self.cat,
            layer="quantum_layer",
            position={
                "x": 2.0,
                "y": 0.0,
                "z": 0.0,
            },
            source_id="trace_latest",
            recognized_identity=(
                "cat:pazuzu"
            ),
            components={},
            perceived_intensity=0.8,
            universe_tick=10,
        )

        observations = (
            CatPerceptionState()
        )

        candidates = CatMind.consider(
            self.cat,
            observations,
        )

        scent = next(
            candidate
            for candidate in candidates
            if candidate.type
            == "follow_known_scent"
        )

        self.assertIsInstance(
            scent.target,
            CatKnownScentTarget,
        )

        self.assertEqual(
            scent.target.source_id,
            "trace_latest",
        )

    def test_executor_rejects_mapping_target(
        self
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type="follow_known_scent",
                target={
                    "identity": "cat:pazuzu",
                    "layer": "quantum_layer",
                    "position": {
                        "x": 1.0,
                        "y": 0.0,
                        "z": 0.0,
                    },
                },
                score=1.0,
                reasons=["test"],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertEqual(
            result["reason"],
            "invalid_scent_target",
        )

        self.assertFalse(
            result["executed"]
        )


if __name__ == "__main__":
    unittest.main()
