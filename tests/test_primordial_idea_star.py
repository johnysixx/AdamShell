import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from idea_universe import IdeaUniverse
from gods.gods import Gods
from universe.bootstraps.idea_genesis_bootstrap import (
    IdeaGenesisBootstrap
)


class PrimordialIdeaStarTests(unittest.TestCase):

    def test_primordial_idea_star_requires_space_and_day4(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        gods = Gods(
            universe
        )

        genesis = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods
        )

        genesis.run()

        with self.assertRaises(
            RuntimeError
        ):
            idea_universe.create_primordial_star()

        genesis.let_there_be_light()
        genesis.let_there_be_space()

        with self.assertRaises(
            RuntimeError
        ):
            idea_universe.create_primordial_star()

        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        star = (
            idea_universe
            .create_primordial_star()
        )

        self.assertEqual(
            star.type,
            "primordial_idea_star"
        )

    def test_primordial_idea_star_explodes_into_nebula_remnant(
        self
    ):
        from idea_universe.primordial_idea_star import (
            PrimordialIdeaStar
        )

        star = PrimordialIdeaStar()

        self.assertEqual(
            star.state,
            "created"
        )

        star.ignite()

        self.assertEqual(
            star.state,
            "burning"
        )

        remnant = star.explode()

        self.assertEqual(
            star.state,
            "exploded"
        )

        self.assertEqual(
            remnant["type"],
            "primordial_nebula_remnant"
        )

        self.assertEqual(
            remnant["source"],
            "primordial_idea_star"
        )


    def test_stellar_epoch_starts_only_after_day4_heavenly_lights(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        gods = Gods(
            universe
        )

        genesis = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods
        )

        genesis.run()

        self.assertFalse(
            idea_universe.stellar_epoch_started
        )

        genesis.let_there_be_light()
        genesis.let_there_be_space()

        self.assertFalse(
            idea_universe.stellar_epoch_started
        )

        with self.assertRaises(
            RuntimeError
        ):
            idea_universe.create_primordial_star()

        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        self.assertTrue(
            idea_universe.heavenly_lights_created
        )

        self.assertTrue(
            idea_universe.stellar_epoch_started
        )

        star = (
            idea_universe
            .create_primordial_star()
        )

        self.assertEqual(
            star.type,
            "primordial_idea_star"
        )

    def test_primordial_star_requires_stellar_epoch(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        idea_universe.stellar_epoch_started = False

        with self.assertRaises(
            RuntimeError
        ):
            idea_universe.create_primordial_star()

        idea_universe.stellar_epoch_started = True

        star = (
            idea_universe
            .create_primordial_star()
        )

        self.assertEqual(
            star.type,
            "primordial_idea_star"
        )



    def test_primordial_stellar_epoch_runs_only_after_day4(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        gods = Gods(
            universe
        )

        genesis = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods
        )

        genesis.run()
        genesis.let_there_be_light()
        genesis.let_there_be_space()

        with self.assertRaises(
            RuntimeError
        ):
            idea_universe.run_primordial_stellar_epoch(
                star_count=3
            )

        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        result = (
            idea_universe
            .run_primordial_stellar_epoch(
                star_count=3
            )
        )

        self.assertEqual(
            len(result["stars"]),
            3
        )

        self.assertEqual(
            len(result["remnants"]),
            3
        )

        for star in result["stars"]:
            self.assertEqual(
                star.state,
                "exploded"
            )

    def test_primordial_star_remnant_contains_elemental_potentials(
        self
    ):
        from idea_universe.primordial_idea_star import (
            PrimordialIdeaStar
        )

        star = PrimordialIdeaStar()

        star.ignite()
        remnant = star.explode()

        self.assertIn(
            "elemental_potentials",
            remnant
        )

        self.assertEqual(
            remnant["elemental_potentials"][
                "hydrogen"
            ],
            1.0
        )

        self.assertEqual(
            remnant["elemental_potentials"][
                "carbon"
            ],
            1.0
        )



    def test_primordial_stars_require_day4_heavenly_lights(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        gods = Gods(
            universe
        )

        genesis = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods
        )

        genesis.run()

        genesis.let_there_be_light()
        genesis.let_there_be_space()

        with self.assertRaises(
            RuntimeError
        ):
            idea_universe.create_primordial_star()

        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        star = (
            idea_universe
            .create_primordial_star()
        )

        self.assertIsNotNone(
            star
        )

        self.assertTrue(
            idea_universe.heavenly_lights_created
        )

        self.assertTrue(
            idea_universe.stellar_epoch_started
        )



    def test_day4_heavenly_lights_require_day3_completion(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        gods = Gods(
            universe
        )

        genesis = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods
        )

        genesis.run()
        genesis.let_there_be_light()
        genesis.let_there_be_space()

        with self.assertRaises(
            RuntimeError
        ):
            genesis.let_there_be_heavenly_lights()

        genesis.let_there_be_land_and_vegetation()

        result = (
            genesis
            .let_there_be_heavenly_lights()
        )

        self.assertTrue(
            result
        )

        self.assertTrue(
            idea_universe.heavenly_lights_created
        )

        self.assertTrue(
            idea_universe.stellar_epoch_started
        )


if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()










