import unittest

from gods import Gods
from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.entity_bootstrap import (
    EntityBootstrap,
)
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap,
)


class EntityBootstrapCanonicalGodObjectStateTests(
    unittest.TestCase
):

    def _prepared(self):
        universe = Universe()

        gods = Gods(universe)
        god = gods.create_god(
            name="god",
            role="librarian",
        )

        universe.gods = gods
        universe.god = god
        universe.world["god"] = god

        bootstrap = EntityBootstrap(
            universe,
            None,
            None,
        )

        return universe, gods, god, bootstrap

    def test_reuses_real_universe_bootstrap_god(self):
        universe = Universe()

        UniverseBootstrap(
            UniverseRegistry(),
            universe,
        ).run()

        original = universe.god
        gods = universe.gods
        library = universe.library

        bootstrap = EntityBootstrap(
            universe,
            universe.idea_universe,
            None,
        )

        bootstrap._create_god()

        self.assertIs(bootstrap.god, original)
        self.assertIs(bootstrap.gods, gods)
        self.assertIs(universe.world["god"], original)
        self.assertIs(library.librarian, original)

        self.assertEqual(original.role, "librarian")
        self.assertTrue(library.god_present)
        self.assertTrue(original.book_created)

        self.assertEqual(
            sum(
                item is original
                for item in gods.gods
            ),
            1,
        )

    def test_world_decoy_cannot_override_god(self):
        universe, gods, god, bootstrap = (
            self._prepared()
        )

        decoy = {
            "name": "god",
            "type": "god",
            "role": "librarian",
        }

        universe.world["god"] = decoy

        bootstrap._create_god()

        self.assertIs(bootstrap.god, god)
        self.assertIs(universe.god, god)
        self.assertIs(universe.world["god"], god)
        self.assertIsNot(universe.world["god"], decoy)
        self.assertIs(bootstrap.gods, gods)

    def test_missing_god_does_not_use_world_fallback(
        self
    ):
        universe, _, god, bootstrap = self._prepared()

        universe.god = None
        universe.world["god"] = god

        with self.assertRaisesRegex(
            RuntimeError,
            "Canonical God must exist",
        ):
            bootstrap._create_god()

        self.assertIsNone(universe.god)
        self.assertIsNone(bootstrap.god)
        self.assertIs(universe.world["god"], god)

    def test_missing_gods_layer_is_rejected(self):
        universe, _, god, bootstrap = self._prepared()

        universe.gods = None

        with self.assertRaisesRegex(
            RuntimeError,
            "Gods layer must exist",
        ):
            bootstrap._create_god()

        self.assertIs(universe.god, god)
        self.assertIs(universe.world["god"], god)

    def test_invalid_canonical_god_type_is_rejected(
        self
    ):
        universe, _, god, bootstrap = self._prepared()

        god.type = "cat"

        with self.assertRaisesRegex(
            RuntimeError,
            "Canonical God is invalid",
        ):
            bootstrap._create_god()

        self.assertIs(universe.god, god)
        self.assertIs(universe.world["god"], god)

    def test_non_librarian_god_is_rejected(self):
        universe, _, god, bootstrap = self._prepared()

        god.role = "creator_entity"

        with self.assertRaisesRegex(
            RuntimeError,
            "Canonical God must currently",
        ):
            bootstrap._create_god()

        self.assertIs(universe.god, god)
        self.assertIs(universe.world["god"], god)

    def test_canonical_god_does_not_read_world_get(
        self
    ):
        class WorldWithoutGet(dict):

            def get(self, key, default=None):
                raise AssertionError(
                    "EntityBootstrap must not use world.get"
                )

        universe, _, god, bootstrap = self._prepared()

        universe.world = WorldWithoutGet(
            universe.world
        )

        bootstrap._create_god()

        self.assertIs(bootstrap.god, god)
        self.assertIs(universe.world["god"], god)

    def test_reusing_canonical_god_is_idempotent(self):
        universe, gods, god, bootstrap = (
            self._prepared()
        )

        before_count = len(gods.gods)

        bootstrap._create_god()
        first = bootstrap.god

        bootstrap._create_god()
        second = bootstrap.god

        self.assertIs(first, god)
        self.assertIs(second, god)

        self.assertEqual(
            len(gods.gods),
            before_count,
        )

        self.assertIs(
            universe.world["god"],
            god,
        )


if __name__ == "__main__":
    unittest.main()
