import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from idea_universe import IdeaUniverse
from idea_universe.primordial_nebula import PrimordialNebula


class PrimordialNebulaTests(unittest.TestCase):

    def test_primordial_nebula_does_not_exist_before_stellar_epoch(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        self.assertIsNone(
            idea_universe.primordial_nebula
        )

        self.assertIsNone(
            idea_universe.state[
                "primordial_nebula"
            ]
        )


    def test_primordial_nebula_starts_empty(
        self
    ):
        nebula = PrimordialNebula()

        self.assertEqual(
            nebula.size,
            0.0
        )

        self.assertEqual(
            nebula.stars,
            []
        )


    def test_idea_universe_starry_sky_contains_primordial_stars_after_stellar_epoch(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        from gods.gods import Gods
        from universe.bootstraps.idea_genesis_bootstrap import (
            IdeaGenesisBootstrap
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
        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        result = (
            idea_universe
            .run_primordial_stellar_epoch(
                star_count=3
            )
        )

        self.assertEqual(
            idea_universe.starry_sky,
            result["stars"]
        )

        self.assertEqual(
            len(
                idea_universe.starry_sky
            ),
            3
        )


    def test_idea_universe_tick_advances_primordial_nebula_after_it_exists(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        from gods.gods import Gods
        from universe.bootstraps.idea_genesis_bootstrap import (
            IdeaGenesisBootstrap
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
        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        idea_universe.run_primordial_stellar_epoch(
            star_count=1
        )

        self.assertEqual(
            idea_universe
            .primordial_nebula
            .tick_count,
            0
        )

        idea_universe.tick()

        self.assertEqual(
            idea_universe
            .primordial_nebula
            .tick_count,
            1
        )


    def test_primordial_nebula_tick_advances_time_without_automatic_growth(
        self
    ):
        nebula = PrimordialNebula()

        self.assertEqual(
            nebula.tick_count,
            0
        )

        self.assertEqual(
            nebula.size,
            0.0
        )

        nebula.tick()

        self.assertEqual(
            nebula.tick_count,
            1
        )

        self.assertEqual(
            nebula.size,
            0.0
        )


    def test_idea_universe_starts_with_primordial_waters_but_without_nebula(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        self.assertIsNotNone(
            idea_universe.primordial_waters
        )

        self.assertIsNone(
            idea_universe.primordial_nebula
        )


    def test_stellar_epoch_creates_primordial_nebula_from_remnants(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        from gods.gods import Gods
        from universe.bootstraps.idea_genesis_bootstrap import (
            IdeaGenesisBootstrap
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
        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        self.assertIsNone(
            idea_universe.primordial_nebula
        )

        result = (
            idea_universe
            .run_primordial_stellar_epoch(
                star_count=3
            )
        )

        self.assertIsNotNone(
            idea_universe.primordial_nebula
        )

        self.assertEqual(
            idea_universe
            .primordial_nebula
            .source_remnant_count,
            3
        )

        self.assertEqual(
            len(
                idea_universe
                .primordial_nebula
                .source_remnants
            ),
            3
        )

        self.assertEqual(
            result["primordial_nebula"],
            idea_universe.primordial_nebula
        )



    def test_primordial_nebula_starts_with_empty_elemental_potentials(
        self
    ):
        from idea_universe.primordial_nebula import (
            PrimordialNebula
        )

        nebula = PrimordialNebula(
            source_remnants=[
                {
                    "type": "primordial_nebula_remnant",
                    "source": "primordial_idea_star"
                }
            ]
        )

        self.assertEqual(
            nebula.elemental_potentials,
            {}
        )

        self.assertEqual(
            nebula.state[
                "elemental_potentials"
            ],
            {}
        )



    def test_primordial_nebula_aggregates_elemental_potentials_from_remnants(
        self
    ):
        from idea_universe.primordial_nebula import (
            PrimordialNebula
        )

        remnants = [
            {
                "type": "primordial_nebula_remnant",
                "source": "primordial_idea_star",
                "elemental_potentials": {
                    "hydrogen": 1.0,
                    "carbon": 1.0
                }
            },
            {
                "type": "primordial_nebula_remnant",
                "source": "primordial_idea_star",
                "elemental_potentials": {
                    "hydrogen": 1.0,
                    "carbon": 1.0
                }
            },
            {
                "type": "primordial_nebula_remnant",
                "source": "primordial_idea_star",
                "elemental_potentials": {
                    "hydrogen": 1.0,
                    "carbon": 1.0
                }
            }
        ]

        nebula = PrimordialNebula(
            source_remnants=remnants
        )

        self.assertEqual(
            nebula.elemental_potentials[
                "hydrogen"
            ],
            3.0
        )

        self.assertEqual(
            nebula.elemental_potentials[
                "carbon"
            ],
            3.0
        )



    def test_primordial_nebula_can_form_hydrocarbon_potential(
        self
    ):
        from idea_universe.primordial_nebula import (
            PrimordialNebula
        )

        nebula = PrimordialNebula(
            source_remnants=[
                {
                    "type": "primordial_nebula_remnant",
                    "source": "primordial_idea_star",
                    "elemental_potentials": {
                        "hydrogen": 2.0,
                        "carbon": 1.0
                    }
                }
            ]
        )

        result = (
            nebula.form_hydrocarbons()
        )

        self.assertEqual(
            result,
            1.0
        )

        self.assertEqual(
            nebula.elemental_potentials[
                "hydrocarbons"
            ],
            1.0
        )



    def test_hydrocarbon_potential_requires_hydrogen_and_carbon(
        self
    ):
        from idea_universe.primordial_nebula import (
            PrimordialNebula
        )

        hydrogen_only = PrimordialNebula(
            source_remnants=[
                {
                    "type": "primordial_nebula_remnant",
                    "source": "primordial_idea_star",
                    "elemental_potentials": {
                        "hydrogen": 1.0
                    }
                }
            ]
        )

        carbon_only = PrimordialNebula(
            source_remnants=[
                {
                    "type": "primordial_nebula_remnant",
                    "source": "primordial_idea_star",
                    "elemental_potentials": {
                        "carbon": 1.0
                    }
                }
            ]
        )

        self.assertEqual(
            hydrogen_only.form_hydrocarbons(),
            0.0
        )

        self.assertNotIn(
            "hydrocarbons",
            hydrogen_only.elemental_potentials
        )

        self.assertEqual(
            carbon_only.form_hydrocarbons(),
            0.0
        )

        self.assertNotIn(
            "hydrocarbons",
            carbon_only.elemental_potentials
        )



    def test_liquid_hydrocarbons_form_only_after_nebula_threshold(
        self
    ):
        from idea_universe.primordial_nebula import (
            PrimordialNebula
        )

        nebula = PrimordialNebula(
            source_remnants=[
                {
                    "type": "primordial_nebula_remnant",
                    "source": "primordial_idea_star",
                    "elemental_potentials": {
                        "hydrogen": 2.0,
                        "carbon": 1.0
                    }
                }
            ]
        )

        nebula.form_hydrocarbons()

        nebula.size = 9.0

        self.assertEqual(
            nebula.form_liquid_hydrocarbons(),
            0.0
        )

        self.assertNotIn(
            "liquid_hydrocarbons",
            nebula.elemental_potentials
        )

        nebula.size = 10.0

        self.assertEqual(
            nebula.form_liquid_hydrocarbons(),
            1.0
        )

        self.assertEqual(
            nebula.elemental_potentials[
                "liquid_hydrocarbons"
            ],
            1.0
        )



    def test_liquid_hydrocarbon_mining_starts_only_after_mining_threshold(
        self
    ):
        from idea_universe.primordial_nebula import (
            PrimordialNebula
        )

        nebula = PrimordialNebula(
            source_remnants=[]
        )

        nebula.size = 99.0

        self.assertFalse(
            nebula.can_mine_liquid_hydrocarbons()
        )

        nebula.size = 100.0

        self.assertTrue(
            nebula.can_mine_liquid_hydrocarbons()
        )



    def test_mining_allows_only_ten_percent_of_liquid_hydrocarbon_growth(
        self
    ):
        from idea_universe.primordial_nebula import (
            PrimordialNebula
        )

        nebula = PrimordialNebula(
            source_remnants=[]
        )

        nebula.size = 100.0

        nebula.record_liquid_hydrocarbon_level(
            100.0
        )

        nebula.record_liquid_hydrocarbon_level(
            130.0
        )

        self.assertEqual(
            nebula.available_liquid_hydrocarbon_mining(),
            3.0
        )



    def test_liquid_hydrocarbon_mining_cannot_exceed_ten_percent_of_growth(
        self
    ):
        from idea_universe.primordial_nebula import (
            PrimordialNebula
        )

        nebula = PrimordialNebula(
            source_remnants=[]
        )

        nebula.size = 100.0

        nebula.record_liquid_hydrocarbon_level(
            100.0
        )

        nebula.record_liquid_hydrocarbon_level(
            130.0
        )

        mined = nebula.mine_liquid_hydrocarbons(
            3.0
        )

        self.assertEqual(
            mined,
            3.0
        )

        self.assertEqual(
            nebula.current_liquid_hydrocarbon_level,
            127.0
        )

        with self.assertRaises(
            RuntimeError
        ):
            nebula.mine_liquid_hydrocarbons(
                1.0
            )


if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()



















