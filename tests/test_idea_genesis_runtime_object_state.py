import unittest

from gods.gods import Gods
from idea_universe import IdeaUniverse
from idea_universe.idea_genesis_runtime_state import (
    IdeaFirstDivineGenerationResult,
    IdeaGenesisBootstrapResult,
    IdeaGenesisLifeEvent,
    IdeaGenesisWordEvent,
)
from multiverse import UniverseRegistry
from universe.bootstraps.idea_genesis_bootstrap import (
    IdeaGenesisBootstrap,
)
from universe.universe import Universe


class IdeaGenesisRuntimeObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.idea_universe = IdeaUniverse(
            self.universe
        )

        self.gods = Gods(
            self.universe
        )

        self.genesis = IdeaGenesisBootstrap(
            universe=self.universe,
            idea_universe=self.idea_universe,
            gods=self.gods,
        )

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value["name"]

    def test_bootstrap_result_is_object(
        self
    ):
        result = self.genesis.run()

        self.assertIsInstance(
            result,
            IdeaGenesisBootstrapResult,
        )

        self.assertEqual(
            result.god.name,
            "god",
        )

        self.assertEqual(
            result.tiamat.name,
            "tiamat",
        )

        self.assertEqual(
            result.apsu.name,
            "apsu",
        )

        self.assertIsNone(
            result.serpent
        )

        self.assert_object_only(
            result
        )

    def test_genesis_history_keeps_objects(
        self
    ):
        self.genesis.run()

        self.genesis.let_there_be_light()

        self.genesis.let_there_be_space()

        event = (
            self.idea_universe
            .events[-1]
        )

        self.assertIsInstance(
            event,
            IdeaGenesisWordEvent,
        )

        self.assertEqual(
            event.word,
            "let_there_be_space",
        )

        self.assert_object_only(
            event
        )

        snapshot = event.to_dict()

        snapshot["word"] = "changed"

        self.assertEqual(
            event.word,
            "let_there_be_space",
        )

    def test_life_creation_result_is_object(
        self
    ):
        self.genesis.run()

        self.genesis.let_there_be_light()
        self.genesis.let_there_be_space()

        self.genesis.let_there_be_land_and_vegetation()

        self.genesis.let_there_be_heavenly_lights()

        result = (
            self.genesis
            .let_there_be_life_in_waters_and_sky()
        )

        self.assertIsInstance(
            result,
            IdeaGenesisLifeEvent,
        )

        self.assertEqual(
            result.day,
            5,
        )

        self.assertTrue(
            result.aquatic_life_archetype
        )

        self.assertTrue(
            result.flying_life_archetype
        )

        self.assertIs(
            self.idea_universe.events[-1],
            result,
        )

        self.assert_object_only(
            result
        )

    def test_divine_generation_result_is_object(
        self
    ):
        bootstrap = self.genesis.run()

        result = (
            self.genesis
            .bring_forth_first_divine_generation(
                tiamat=bootstrap.tiamat,
                apsu=bootstrap.apsu,
            )
        )

        self.assertIsInstance(
            result,
            IdeaFirstDivineGenerationResult,
        )

        self.assertEqual(
            result.lahmu.name,
            "lahmu",
        )

        self.assertEqual(
            result.lahamu.name,
            "lahamu",
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
