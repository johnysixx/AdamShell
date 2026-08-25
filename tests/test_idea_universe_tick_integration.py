import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from universe.bootstraps.universe_bootstrap import UniverseBootstrap


class IdeaUniverseTickIntegrationTests(
    unittest.TestCase
):

    def test_bootstrap_attaches_idea_universe_to_universe(
        self
    ):
        universe = Universe()
        registry = UniverseRegistry()

        bootstrap = UniverseBootstrap(
            universe_registry=registry,
            universe=universe
        )

        (
            root_transition,
            layers,
            idea_universe
        ) = bootstrap.run()

        self.assertIs(
            universe.idea_universe,
            idea_universe
        )


    def test_universe_tick_advances_idea_universe(
        self
    ):
        universe = Universe()
        registry = UniverseRegistry()

        bootstrap = UniverseBootstrap(
            universe_registry=registry,
            universe=universe
        )

        (
            root_transition,
            layers,
            idea_universe
        ) = bootstrap.run()

        self.assertEqual(
            idea_universe.tick_count,
            0
        )

        universe.tick_universe()

        self.assertEqual(
            idea_universe.tick_count,
            1
        )


if __name__ == "__main__":
    unittest.main()

