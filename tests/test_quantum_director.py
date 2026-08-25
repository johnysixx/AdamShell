import unittest

from quantum.director import QuantumDirector
from universe.universe import Universe
from multiverse import UniverseRegistry
from idea_universe import IdeaUniverse
from gods.gods import Gods
from universe.bootstraps.idea_genesis_bootstrap import (
    IdeaGenesisBootstrap
)


def make_director(universe):
    gods = Gods(
        universe
    )

    god = gods.create_god(
        name="god",
        role="creator_entity"
    )

    director = QuantumDirector(
        universe=universe,
        god=god,
        gods=gods
    )

    return director, god, gods

class QuantumDirectorTests(unittest.TestCase):

    def test_director_observes_first_primordial_star_and_records_it(
        self
    ):
        from quantum.director import QuantumDirector

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
        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        director, god, gods = make_director(
            universe
        )

        star = (
            idea_universe
            .create_primordial_star()
        )

        director.observe(
            {
                "event": "primordial_idea_star_created",
                "subject": star
            }
        )

        self.assertEqual(
            director.layer,
            "quantum_layer"
        )

        self.assertEqual(
            director.zone,
            "stable_zone"
        )

        self.assertEqual(
            len(director.research_book),
            1
        )

        self.assertEqual(
            director.research_book[0][
                "event"
            ],
            "primordial_idea_star_created"
        )



    def test_director_records_star_explosion_and_primordial_nebula_birth(
        self
    ):
        from quantum.director import QuantumDirector

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
        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        director, god, gods = make_director(
            universe
        )

        result = (
            idea_universe
            .run_primordial_stellar_epoch(
                star_count=1
            )
        )

        star = result["stars"][0]
        nebula = result["primordial_nebula"]

        director.observe_star_explosion(
            star=star,
            remnant=result["remnants"][0]
        )

        director.observe_nebula_birth(
            nebula=nebula
        )

        self.assertEqual(
            len(director.research_book),
            2
        )

        self.assertEqual(
            director.research_book[0]["event"],
            "primordial_idea_star_exploded"
        )

        self.assertEqual(
            director.research_book[1]["event"],
            "primordial_nebula_created"
        )

        self.assertIs(
            director.research_book[1]["subject"],
            nebula
        )



    def test_director_identifies_liquid_hydrocarbons_in_nebula(
        self
    ):
        from quantum.director import QuantumDirector
        from idea_universe.primordial_nebula import PrimordialNebula

        universe = Universe()

        director, god, gods = make_director(
            universe
        )

        nebula = PrimordialNebula(
            source_remnants=[]
        )

        nebula.elemental_potentials[
            "hydrocarbons"
        ] = 5.0

        nebula.size = 10.0
        nebula.form_liquid_hydrocarbons()

        result = director.study_nebula(
            nebula
        )

        self.assertEqual(
            result["finding"],
            "liquid_hydrocarbons_identified"
        )

        self.assertEqual(
            result["amount"],
            5.0
        )

        self.assertIn(
            "liquid_hydrocarbons_identified",
            director.knowledge
        )



    def test_director_invents_mining_only_after_identifying_liquid_hydrocarbons(
        self
    ):
        from quantum.director import QuantumDirector
        from idea_universe.primordial_nebula import PrimordialNebula

        universe = Universe()

        director, god, gods = make_director(
            universe
        )

        nebula = PrimordialNebula(
            source_remnants=[]
        )

        with self.assertRaises(
            RuntimeError
        ):
            director.invent_mining_method(
                nebula
            )

        nebula.elemental_potentials[
            "hydrocarbons"
        ] = 10.0

        nebula.size = 100.0
        nebula.form_liquid_hydrocarbons()

        director.study_nebula(
            nebula
        )

        result = director.invent_mining_method(
            nebula
        )

        self.assertEqual(
            result["invention"],
            "liquid_hydrocarbon_mining"
        )

        self.assertIn(
            "liquid_hydrocarbon_mining",
            director.knowledge
        )

        self.assertEqual(
            result["mining_limit_rule"],
            "maximum_10_percent_of_growth"
        )



    def test_director_can_mine_after_inventing_mining_method(
        self
    ):
        from quantum.director import QuantumDirector
        from idea_universe.primordial_nebula import PrimordialNebula

        universe = Universe()

        director, god, gods = make_director(
            universe
        )

        nebula = PrimordialNebula(
            source_remnants=[]
        )

        nebula.size = 100.0

        nebula.elemental_potentials[
            "hydrocarbons"
        ] = 130.0

        nebula.form_liquid_hydrocarbons()

        nebula.record_liquid_hydrocarbon_level(
            100.0
        )

        nebula.record_liquid_hydrocarbon_level(
            130.0
        )

        director.study_nebula(
            nebula
        )

        director.invent_mining_method(
            nebula
        )

        result = director.mine_nebula(
            nebula=nebula,
            amount=3.0
        )

        self.assertEqual(
            result["mined"],
            3.0
        )

        self.assertEqual(
            nebula.current_liquid_hydrocarbon_level,
            127.0
        )

        self.assertEqual(
            result["material"],
            "liquid_hydrocarbons"
        )

        self.assertEqual(
            result["miner"],
            "director"
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







