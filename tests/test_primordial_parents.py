import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from idea_universe import IdeaUniverse
from idea_entities import IdeaEntities


class PrimordialParentsTests(unittest.TestCase):

    def test_tiamat_and_apsu_exist_as_primordial_idea_entities(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        idea_entities = IdeaEntities(
            universe
        )

        tiamat = idea_entities.create_idea_entity(
            name="tiamat",
            role="primordial_mother",
            active=True,
            existence_pct=100.0
        )

        apsu = idea_entities.create_idea_entity(
            name="apsu",
            role="primordial_father",
            active=True,
            existence_pct=100.0
        )

        idea_universe.add_entity(
            tiamat
        )

        idea_universe.add_entity(
            apsu
        )

        self.assertIn(
            tiamat,
            idea_universe.entities
        )

        self.assertIn(
            apsu,
            idea_universe.entities
        )

        self.assertEqual(
            tiamat["role"],
            "primordial_mother"
        )

        self.assertEqual(
            apsu["role"],
            "primordial_father"
        )


    def test_idea_genesis_bootstrap_creates_primordial_parents(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        from gods.gods import Gods

        gods = Gods(
            universe
        )

        from universe.bootstraps.idea_genesis_bootstrap import (
            IdeaGenesisBootstrap
        )

        bootstrap = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods
        )

        result = bootstrap.run()

        tiamat = result["tiamat"]
        apsu = result["apsu"]

        self.assertEqual(
            tiamat["type"],
            "god"
        )

        self.assertEqual(
            apsu["type"],
            "god"
        )

        self.assertEqual(
            tiamat["role"],
            "primordial_mother"
        )

        self.assertEqual(
            apsu["role"],
            "primordial_father"
        )

        self.assertEqual(
            tiamat["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            apsu["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            tiamat["existence_by_world"][
                "idea_universe"
            ],
            100.0
        )

        self.assertEqual(
            apsu["existence_by_world"][
                "idea_universe"
            ],
            100.0
        )

    def test_created_god_originates_in_gods_layer(
        self
    ):
        universe = Universe()

        from gods.gods import Gods

        gods = Gods(
            universe
        )

        god = gods.create_god(
            name="god",
            role="creator_entity"
        )

        self.assertEqual(
            god["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            god["existence_by_world"][
                "idea_universe"
            ],
            100.0
        )

        self.assertEqual(
            god["existence_by_world"][
                "eden"
            ],
            0.0
        )


    def test_primordial_parents_have_water_aspects(
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

        result = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods
        ).run()

        tiamat = result["tiamat"]
        apsu = result["apsu"]

        self.assertEqual(
            tiamat["primordial_aspect"],
            "salt_water"
        )

        self.assertEqual(
            apsu["primordial_aspect"],
            "fresh_water"
        )


    def test_primordial_parents_establish_chaotic_waters(
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

        IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods
        ).run()

        nebula = (
            idea_universe
            .primordial_waters
        )

        self.assertTrue(
            nebula.waters
        )

        self.assertTrue(
            nebula.deep
        )

        self.assertTrue(
            nebula.chaos
        )

        self.assertFalse(
            nebula.ordered
        )


    def test_let_there_be_light_starts_order_in_idea_universe(
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

        nebula = (
            idea_universe
            .primordial_waters
        )

        self.assertTrue(
            nebula.chaos
        )

        self.assertFalse(
            getattr(
                nebula,
                "light",
                False
            )
        )

        genesis.let_there_be_light()

        self.assertTrue(
            nebula.light
        )

        self.assertTrue(
            nebula.order_started
        )


    def test_let_there_be_space_allows_primordial_nebula_to_expand(
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

        nebula = (
            idea_universe
            .primordial_waters
        )

        self.assertFalse(
            getattr(
                nebula,
                "space",
                False
            )
        )

        self.assertFalse(
            getattr(
                nebula,
                "can_expand",
                False
            )
        )

        genesis.let_there_be_light()
        genesis.let_there_be_space()

        self.assertTrue(
            nebula.space
        )

        self.assertTrue(
            nebula.can_expand
        )


    def test_let_there_be_space_is_recorded_as_genesis_event(
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

        self.assertIn(
            {
                "kind": "genesis",
                "word": "let_there_be_space"
            },
            idea_universe.events
        )


    def test_day0_bootstrap_creates_tiamat_apsu_and_serpent(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        from meeting_place.meeting_place import MeetingPlace
        from idea_entities import IdeaEntities
        from gods.gods import Gods
        from universe.bootstraps.idea_genesis_bootstrap import (
            IdeaGenesisBootstrap
        )

        meeting_place = MeetingPlace(
            universe
        )

        universe.meeting_place = (
            meeting_place
        )

        idea_universe = IdeaUniverse(
            universe
        )

        gods = Gods(
            universe
        )

        idea_entities = IdeaEntities(
            universe
        )

        result = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods,
            idea_entities=idea_entities
        ).run()

        idea_names = [
            entity["name"]
            for entity in idea_universe.entities
        ]

        bar_names = [
            entity["name"]
            for entity in meeting_place.entities
        ]

        self.assertIn(
            "tiamat",
            idea_names
        )

        self.assertIn(
            "apsu",
            idea_names
        )

        self.assertIn(
            "serpent",
            idea_names
        )

        self.assertIn(
            "tiamat",
            bar_names
        )

        self.assertIn(
            "apsu",
            bar_names
        )

        self.assertIn(
            "serpent",
            bar_names
        )

        self.assertEqual(
            result["serpent"]["type"],
            "idea_entity"
        )


    def test_day0_records_creation_phases_in_order(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        from meeting_place.meeting_place import MeetingPlace
        from gods.gods import Gods
        from idea_entities import IdeaEntities
        from universe.bootstraps.idea_genesis_bootstrap import (
            IdeaGenesisBootstrap
        )

        meeting_place = MeetingPlace(
            universe
        )

        universe.meeting_place = (
            meeting_place
        )

        idea_universe = IdeaUniverse(
            universe
        )

        gods = Gods(
            universe
        )

        idea_entities = IdeaEntities(
            universe
        )

        genesis = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods,
            idea_entities=idea_entities
        )

        genesis.run()

        self.assertEqual(
            genesis.day0_phases,
            [
                "day0_started",
                "primordial_parents_created",
                "serpent_created"
            ]
        )






    def test_day0_contains_god_tiamat_apsu_and_serpent(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        from meeting_place.meeting_place import MeetingPlace
        from gods.gods import Gods
        from idea_entities import IdeaEntities
        from universe.bootstraps.idea_genesis_bootstrap import (
            IdeaGenesisBootstrap
        )

        meeting_place = MeetingPlace(
            universe
        )

        universe.meeting_place = (
            meeting_place
        )

        idea_universe = IdeaUniverse(
            universe
        )

        gods = Gods(
            universe
        )

        idea_entities = IdeaEntities(
            universe
        )

        result = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=gods,
            idea_entities=idea_entities
        ).run()

        god_names = [
            god["name"]
            for god in gods.gods
        ]

        self.assertIn(
            "god",
            god_names
        )

        self.assertIn(
            "tiamat",
            god_names
        )

        self.assertIn(
            "apsu",
            god_names
        )

        self.assertEqual(
            result["god"]["role"],
            "creator_entity"
        )

        self.assertEqual(
            result["god"]["native_world"],
            "gods_layer"
        )


    def test_day3_creates_seas_dry_land_and_vegetation(
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

        waters = (
            idea_universe
            .primordial_waters
        )

        self.assertFalse(
            getattr(
                waters,
                "seas",
                False
            )
        )

        self.assertFalse(
            getattr(
                waters,
                "dry_land",
                False
            )
        )

        self.assertFalse(
            getattr(
                waters,
                "vegetation",
                False
            )
        )

        genesis.let_there_be_land_and_vegetation()

        self.assertTrue(
            waters.seas
        )

        self.assertTrue(
            waters.dry_land
        )

        self.assertTrue(
            waters.vegetation
        )



    def test_day2_requires_day1_light(
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

        with self.assertRaises(
            RuntimeError
        ):
            genesis.let_there_be_space()

        genesis.let_there_be_light()

        result = (
            genesis
            .let_there_be_space()
        )

        self.assertTrue(
            result.space
        )


    def test_day3_requires_day2_space(
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

        with self.assertRaises(
            RuntimeError
        ):
            genesis.let_there_be_land_and_vegetation()

        genesis.let_there_be_space()

        result = (
            genesis
            .let_there_be_land_and_vegetation()
        )

        self.assertTrue(
            result.vegetation
        )



    def test_day5_creates_aquatic_and_flying_life_archetypes(
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

        self.assertFalse(
            getattr(
                idea_universe,
                "aquatic_life_archetype",
                False
            )
        )

        self.assertFalse(
            getattr(
                idea_universe,
                "flying_life_archetype",
                False
            )
        )

        result = (
            genesis
            .let_there_be_life_in_waters_and_sky()
        )

        self.assertTrue(
            idea_universe.aquatic_life_archetype
        )

        self.assertTrue(
            idea_universe.flying_life_archetype
        )

        self.assertEqual(
            result["day"],
            5
        )


    def test_day5_requires_day4_completion(
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

        with self.assertRaises(
            RuntimeError
        ):
            genesis.let_there_be_life_in_waters_and_sky()



    def test_day6_requires_day5_completion(
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

        with self.assertRaises(
            RuntimeError
        ):
            genesis.let_there_be_land_life()


    def test_day6_creates_land_life_archetype(
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
        genesis.let_there_be_life_in_waters_and_sky()

        result = (
            genesis
            .let_there_be_land_life()
        )

        self.assertTrue(
            idea_universe.land_life_archetype
        )

        self.assertEqual(
            result["day"],
            6
        )

        self.assertEqual(
            result["created"],
            "land_life_archetype"
        )


    def test_day6_land_life_requires_day5_completion(
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

        with self.assertRaises(
            RuntimeError
        ):
            genesis.let_there_be_land_life()



    def test_tiamat_and_apsu_bring_forth_lahmu_and_lahamu(
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

        result = genesis.run()

        tiamat = result["tiamat"]
        apsu = result["apsu"]

        children = genesis.bring_forth_first_divine_generation(
            tiamat=tiamat,
            apsu=apsu
        )

        lahmu = children["lahmu"]
        lahamu = children["lahamu"]

        self.assertEqual(
            lahmu["type"],
            "god"
        )

        self.assertEqual(
            lahamu["type"],
            "god"
        )

        self.assertEqual(
            lahmu["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            lahamu["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            lahmu["parents"],
            [
                "apsu",
                "tiamat"
            ]
        )

        self.assertEqual(
            lahamu["parents"],
            [
                "apsu",
                "tiamat"
            ]
        )



    def test_lahmu_and_lahamu_bring_forth_anshar_and_kishar(
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

        result = genesis.run()

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=result["tiamat"],
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anshar = second_generation["anshar"]
        kishar = second_generation["kishar"]

        self.assertEqual(
            anshar["type"],
            "god"
        )

        self.assertEqual(
            kishar["type"],
            "god"
        )

        self.assertEqual(
            anshar["parents"],
            [
                "lahmu",
                "lahamu"
            ]
        )

        self.assertEqual(
            kishar["parents"],
            [
                "lahmu",
                "lahamu"
            ]
        )

        self.assertEqual(
            anshar["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            kishar["native_world"],
            "gods_layer"
        )



    def test_anshar_and_kishar_bring_forth_anu(
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

        result = genesis.run()

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=result["tiamat"],
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anu = (
            genesis
            .bring_forth_anu(
                anshar=second_generation["anshar"],
                kishar=second_generation["kishar"]
            )
        )

        self.assertEqual(
            anu["name"],
            "anu"
        )

        self.assertEqual(
            anu["type"],
            "god"
        )

        self.assertEqual(
            anu["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            anu["parents"],
            [
                "anshar",
                "kishar"
            ]
        )



    def test_anshar_and_kishar_bring_forth_anu(
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

        result = genesis.run()

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=result["tiamat"],
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anu = genesis.bring_forth_anu(
            anshar=second_generation["anshar"],
            kishar=second_generation["kishar"]
        )

        self.assertEqual(
            anu["name"],
            "anu"
        )

        self.assertEqual(
            anu["type"],
            "god"
        )

        self.assertEqual(
            anu["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            anu["parents"],
            [
                "anshar",
                "kishar"
            ]
        )



    def test_anu_brings_forth_ea_with_nudimmud_epithet(
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

        result = genesis.run()

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=result["tiamat"],
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anu = genesis.bring_forth_anu(
            anshar=second_generation["anshar"],
            kishar=second_generation["kishar"]
        )

        ea = genesis.bring_forth_ea(
            anu=anu
        )

        self.assertEqual(
            ea["name"],
            "ea"
        )

        self.assertEqual(
            ea["type"],
            "god"
        )

        self.assertEqual(
            ea["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            ea["parents"],
            [
                "anu"
            ]
        )

        self.assertIn(
            "nudimmud",
            ea["epithets"]
        )



    def test_damkina_exists_as_goddess_before_marduk_manifestation(
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

        result = genesis.run()

        damkina = (
            genesis
            .bring_forth_damkina()
        )

        self.assertEqual(
            damkina["name"],
            "damkina"
        )

        self.assertEqual(
            damkina["type"],
            "god"
        )

        self.assertEqual(
            damkina["native_world"],
            "gods_layer"
        )

        self.assertEqual(
            damkina["role"],
            "mother_of_marduk"
        )



    def test_ea_and_damkina_manifest_existing_god_as_marduk(
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

        result = genesis.run()

        god = result["god"]

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=result["tiamat"],
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anu = genesis.bring_forth_anu(
            anshar=second_generation["anshar"],
            kishar=second_generation["kishar"]
        )

        ea = genesis.bring_forth_ea(
            anu=anu
        )

        damkina = genesis.bring_forth_damkina()

        god_count_before = len(
            gods.gods
        )

        marduk = genesis.manifest_marduk(
            god=god,
            ea=ea,
            damkina=damkina
        )

        self.assertIs(
            marduk["mask_of"],
            god
        )

        self.assertEqual(
            marduk["name"],
            "marduk"
        )

        self.assertEqual(
            marduk["role"],
            "divine_champion"
        )

        self.assertEqual(
            marduk["parents"],
            [
                "ea",
                "damkina"
            ]
        )

        self.assertEqual(
            len(gods.gods),
            god_count_before
        )

        self.assertNotIn(
            "parents",
            god
        )



    def test_marduk_must_receive_divine_authority_before_confronting_tiamat(
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

        result = genesis.run()

        god = result["god"]

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=result["tiamat"],
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anu = genesis.bring_forth_anu(
            anshar=second_generation["anshar"],
            kishar=second_generation["kishar"]
        )

        ea = genesis.bring_forth_ea(
            anu=anu
        )

        damkina = genesis.bring_forth_damkina()

        marduk = genesis.manifest_marduk(
            god=god,
            ea=ea,
            damkina=damkina
        )

        self.assertFalse(
            marduk.get(
                "divine_authority_granted",
                False
            )
        )

        with self.assertRaises(
            RuntimeError
        ):
            genesis.confront_tiamat(
                marduk=marduk,
                tiamat=result["tiamat"]
            )

        authority = (
            genesis
            .grant_marduk_divine_authority(
                marduk=marduk
            )
        )

        self.assertTrue(
            marduk["divine_authority_granted"]
        )

        self.assertEqual(
            authority["title"],
            "king_of_the_gods"
        )



    def test_marduk_defeats_tiamat_without_creating_new_god(
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

        result = genesis.run()

        god = result["god"]
        tiamat = result["tiamat"]

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=tiamat,
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anu = genesis.bring_forth_anu(
            anshar=second_generation["anshar"],
            kishar=second_generation["kishar"]
        )

        ea = genesis.bring_forth_ea(
            anu=anu
        )

        damkina = genesis.bring_forth_damkina()

        marduk = genesis.manifest_marduk(
            god=god,
            ea=ea,
            damkina=damkina
        )

        genesis.grant_marduk_divine_authority(
            marduk=marduk
        )

        god_count_before = len(
            gods.gods
        )

        outcome = genesis.defeat_tiamat(
            marduk=marduk,
            tiamat=tiamat
        )

        self.assertEqual(
            outcome["event"],
            "tiamat_defeated"
        )

        self.assertEqual(
            outcome["actor_mask"],
            "marduk"
        )

        self.assertIs(
            outcome["actor"],
            god
        )

        self.assertEqual(
            tiamat["state"],
            "defeated"
        )

        self.assertEqual(
            len(gods.gods),
            god_count_before
        )



    def test_marduk_orders_cosmos_after_defeating_tiamat(
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

        result = genesis.run()

        god = result["god"]
        tiamat = result["tiamat"]

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=tiamat,
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anu = genesis.bring_forth_anu(
            anshar=second_generation["anshar"],
            kishar=second_generation["kishar"]
        )

        ea = genesis.bring_forth_ea(
            anu=anu
        )

        damkina = genesis.bring_forth_damkina()

        marduk = genesis.manifest_marduk(
            god=god,
            ea=ea,
            damkina=damkina
        )

        genesis.grant_marduk_divine_authority(
            marduk=marduk
        )

        genesis.defeat_tiamat(
            marduk=marduk,
            tiamat=tiamat
        )

        result = genesis.order_cosmos_from_tiamat(
            marduk=marduk,
            tiamat=tiamat
        )

        self.assertTrue(
            idea_universe.heaven_ordered
        )

        self.assertTrue(
            idea_universe.celestial_stations_established
        )

        self.assertEqual(
            result["event"],
            "cosmos_ordered_from_tiamat"
        )

        self.assertEqual(
            result["actor_mask"],
            "marduk"
        )



    def test_cosmic_order_can_have_genesis_and_mesopotamian_witnesses(
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

        result = genesis.run()

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=result["tiamat"],
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anu = genesis.bring_forth_anu(
            anshar=second_generation["anshar"],
            kishar=second_generation["kishar"]
        )

        ea = genesis.bring_forth_ea(
            anu=anu
        )

        damkina = genesis.bring_forth_damkina()

        marduk = genesis.manifest_marduk(
            god=result["god"],
            ea=ea,
            damkina=damkina
        )

        genesis.grant_marduk_divine_authority(
            marduk=marduk
        )

        genesis.defeat_tiamat(
            marduk=marduk,
            tiamat=result["tiamat"]
        )

        mesopotamian = (
            genesis
            .order_cosmos_from_tiamat(
                marduk=marduk,
                tiamat=result["tiamat"]
            )
        )

        genesis.let_there_be_light()
        genesis.let_there_be_space()
        genesis.let_there_be_land_and_vegetation()
        genesis_view = (
            genesis
            .let_there_be_heavenly_lights()
        )

        event = genesis.record_cosmic_order_witnesses(
            genesis_view=genesis_view,
            mesopotamian_view=mesopotamian
        )

        self.assertEqual(
            event["event"],
            "cosmic_order_established"
        )

        self.assertEqual(
            set(event["witnesses"].keys()),
            {
                "genesis",
                "mesopotamian"
            }
        )

        self.assertEqual(
            event["witnesses"]["genesis"]["event"],
            "heavenly_lights_created"
        )

        self.assertEqual(
            event["witnesses"]["mesopotamian"]["event"],
            "cosmos_ordered_from_tiamat"
        )



    def test_marduk_establishes_divine_order_after_cosmic_order(
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

        result = genesis.run()

        first_generation = (
            genesis
            .bring_forth_first_divine_generation(
                tiamat=result["tiamat"],
                apsu=result["apsu"]
            )
        )

        second_generation = (
            genesis
            .bring_forth_second_divine_generation(
                lahmu=first_generation["lahmu"],
                lahamu=first_generation["lahamu"]
            )
        )

        anu = genesis.bring_forth_anu(
            anshar=second_generation["anshar"],
            kishar=second_generation["kishar"]
        )

        ea = genesis.bring_forth_ea(
            anu=anu
        )

        damkina = genesis.bring_forth_damkina()

        marduk = genesis.manifest_marduk(
            god=result["god"],
            ea=ea,
            damkina=damkina
        )

        genesis.grant_marduk_divine_authority(
            marduk=marduk
        )

        genesis.defeat_tiamat(
            marduk=marduk,
            tiamat=result["tiamat"]
        )

        genesis.order_cosmos_from_tiamat(
            marduk=marduk,
            tiamat=result["tiamat"]
        )

        order = genesis.establish_divine_order(
            marduk=marduk,
            gods=[
                anu,
                ea,
                damkina,
                first_generation["lahmu"],
                first_generation["lahamu"],
                second_generation["anshar"],
                second_generation["kishar"]
            ]
        )

        self.assertTrue(
            idea_universe.divine_order_established
        )

        self.assertEqual(
            order["event"],
            "divine_order_established"
        )

        self.assertEqual(
            order["actor_mask"],
            "marduk"
        )

        self.assertGreaterEqual(
            len(order["assignments"]),
            1
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

































