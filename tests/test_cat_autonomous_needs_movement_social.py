import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind


class CatAutonomousNeedsMovementSocialTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

    def make_cat(
        self,
        name,
        x=0.0,
        y=0.0
    ):
        cat = self.cats.create_cat(
            name=name,
            color="black",
            fur_length="short"
        )

        cat.position = {
            "x": x,
            "y": y,
            "z": 0.0
        }

        cat.current_layer = (
            "physical_world"
        )

        return cat

    def test_needs_advance_each_autonomous_tick(
        self
    ):
        cat = self.make_cat(
            "needcat"
        )

        self.cats.tick()

        self.assertEqual(
            cat.needs["tick"],
            1
        )

        self.assertGreater(
            cat.needs["hunger"],
            0.0
        )

    def test_fatigue_biases_mind_toward_rest(
        self
    ):
        cat = self.make_cat(
            "sleepy"
        )

        cat.needs["fatigue"] = 1.0

        observations = (
            self.cats.observe_cat(
                cat
            )
        )

        candidates = CatMind.consider(
            cat,
            observations
        )

        rest = next(
            candidate
            for candidate in candidates
            if candidate["type"]
            == "rest"
        )

        self.assertGreaterEqual(
            rest["score"],
            0.80
        )

    def test_curiosity_can_create_real_world_movement(
        self
    ):
        cat = self.make_cat(
            "walker"
        )

        cat.needs["curiosity"] = 1.0

        before = dict(
            cat.position
        )

        self.cats.tick()

        self.assertNotEqual(
            cat.position,
            before
        )

    def test_social_need_and_proximity_can_create_social_memory(
        self
    ):
        first = self.make_cat(
            "social_a",
            0.0,
            0.0
        )

        second = self.make_cat(
            "social_b",
            0.0,
            0.0
        )

        first.needs["social"] = 1.0

        first.personality[
            "traits"
        ][
            "empathy"
        ] = 1.0

        self.cats.tick()

        self.assertTrue(
            first.social_memory
            or second.social_memory
        )


if __name__ == "__main__":
    unittest.main()
