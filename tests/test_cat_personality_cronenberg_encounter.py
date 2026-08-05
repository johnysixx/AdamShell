import unittest

from universe.universe import Universe


class FixedRng:

    def __init__(
        self,
        random_value
    ):
        self.random_value = float(
            random_value
        )

    def random(self):
        return self.random_value


class CatPersonalityCronenbergEncounterTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        result = self.universe.manifest_cat(
            name="hunter",
            source="test",
            position={
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        self.cat = result["cat"]

    def create_cronenberg(
        self,
        size
    ):
        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Personality encounter test."
                ),
                source_component="test",
                source_operation=(
                    "personality_encounter"
                )
            )
        )

        cronenberg.position = {
            "x": 1.0,
            "y": 0.0,
            "z": 0.0
        }

        cronenberg.size = float(
            size
        )

        return cronenberg

    def create_route(
        self,
        cronenberg
    ):
        result = (
            self.universe
            .quantum_space
            .plan_direct_cat_route(
                cat_id=self.cat["name"],
                start_position={
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                },
                destination_position=(
                    cronenberg.position
                ),
                destination=cronenberg.id,
                step_size=1.0
            )
        )

        return result["route"]

    def traits(self):
        return self.cat[
            "personality"
        ][
            "traits"
        ]

    def test_successful_hunt_builds_courage(
        self
    ):
        cronenberg = self.create_cronenberg(
            size=0.5
        )

        route = self.create_route(
            cronenberg
        )

        result = (
            self.universe
            .cat_cronenberg_encounter
            .resolve(
                cat=self.cat,
                cronenberg=cronenberg,
                route=route,
                universe=self.universe,
                rng=FixedRng(1.0)
            )
        )

        self.assertEqual(
            result["result"],
            "cronenberg_hunted"
        )

        self.assertAlmostEqual(
            self.traits()["courage"],
            0.54
        )

        self.assertAlmostEqual(
            self.traits()["aggression"],
            0.525
        )

        self.assertAlmostEqual(
            self.traits()["curiosity"],
            0.51
        )

    def test_large_cronenberg_builds_patience(
        self
    ):
        cronenberg = self.create_cronenberg(
            size=2.0
        )

        route = self.create_route(
            cronenberg
        )

        result = (
            self.universe
            .cat_cronenberg_encounter
            .resolve(
                cat=self.cat,
                cronenberg=cronenberg,
                route=route,
                universe=self.universe,
                rng=FixedRng(1.0)
            )
        )

        self.assertEqual(
            result["result"],
            "cat_avoids_cronenberg"
        )

        self.assertAlmostEqual(
            self.traits()["patience"],
            0.53
        )

        self.assertAlmostEqual(
            self.traits()["courage"],
            0.51
        )

    def test_escaped_prey_builds_patience(
        self
    ):
        cronenberg = self.create_cronenberg(
            size=0.8
        )

        route = self.create_route(
            cronenberg
        )

        result = (
            self.universe
            .cat_cronenberg_encounter
            .resolve(
                cat=self.cat,
                cronenberg=cronenberg,
                route=route,
                universe=self.universe,
                rng=FixedRng(0.0)
            )
        )

        self.assertEqual(
            result["result"],
            "cronenberg_escaped"
        )

        self.assertAlmostEqual(
            self.traits()["patience"],
            0.52
        )

        self.assertAlmostEqual(
            self.traits()["curiosity"],
            0.51
        )


if __name__ == "__main__":
    unittest.main()