import unittest

from gods.gods import Gods
from idea_universe import IdeaUniverse
from idea_universe.primordial_waters import PrimordialWaters
from idea_universe.primordial_waters_state import (
    PrimordialWatersState,
)
from multiverse import UniverseRegistry
from universe.bootstraps.idea_genesis_bootstrap import (
    IdeaGenesisBootstrap,
)
from universe.universe import Universe


class PrimordialWatersObjectStateTests(unittest.TestCase):

    def _genesis(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        idea_universe = IdeaUniverse(universe)
        genesis = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=Gods(universe),
        )

        return idea_universe, genesis

    def test_state_is_object_only(self):
        state = PrimordialWatersState()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(state, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = state["waters"]

    def test_initial_values_are_preserved(self):
        waters = PrimordialWaters()
        state = waters.primordial_waters_state

        self.assertIs(waters.state, state)
        self.assertFalse(state.waters)
        self.assertFalse(state.deep)
        self.assertFalse(state.chaos)
        self.assertFalse(state.ordered)
        self.assertFalse(state.light)
        self.assertFalse(state.order_started)
        self.assertFalse(state.space)
        self.assertFalse(state.can_expand)
        self.assertFalse(state.seas)
        self.assertFalse(state.dry_land)
        self.assertFalse(state.vegetation)

    def test_scalar_interface_mutates_same_state_object(self):
        waters = PrimordialWaters()
        state = waters.primordial_waters_state

        waters.waters = True
        waters.light = True
        waters.space = True
        waters.vegetation = True

        self.assertIs(waters.primordial_waters_state, state)
        self.assertTrue(state.waters)
        self.assertTrue(state.light)
        self.assertTrue(state.space)
        self.assertTrue(state.vegetation)

    def test_day_zero_mutates_same_state_object(self):
        idea_universe, genesis = self._genesis()
        waters = idea_universe.primordial_waters
        state = waters.primordial_waters_state

        genesis.run()

        self.assertIs(waters.primordial_waters_state, state)
        self.assertTrue(state.waters)
        self.assertTrue(state.deep)
        self.assertTrue(state.chaos)
        self.assertFalse(state.ordered)

    def test_days_one_to_three_mutate_same_state_object(self):
        idea_universe, genesis = self._genesis()
        waters = idea_universe.primordial_waters
        state = waters.primordial_waters_state

        genesis.run()
        genesis.let_there_be_light()
        genesis.let_there_be_space()
        genesis.let_there_be_land_and_vegetation()

        self.assertIs(waters.primordial_waters_state, state)
        self.assertTrue(state.light)
        self.assertTrue(state.order_started)
        self.assertTrue(state.space)
        self.assertTrue(state.can_expand)
        self.assertTrue(state.seas)
        self.assertTrue(state.dry_land)
        self.assertTrue(state.vegetation)

    def test_idea_universe_keeps_same_waters_object(self):
        idea_universe, _ = self._genesis()

        self.assertIs(
            idea_universe.state["primordial_waters"],
            idea_universe.primordial_waters,
        )

    def test_public_state_remains_dict_boundary(self):
        waters = PrimordialWaters()
        waters.waters = True

        public_state = waters.public_state

        self.assertIsInstance(public_state, dict)
        self.assertEqual(
            public_state["name"],
            "primordial_waters",
        )
        self.assertTrue(public_state["waters"])

        public_state["waters"] = False

        self.assertTrue(waters.waters)

    def test_to_dict_is_detached_boundary(self):
        state = PrimordialWatersState(waters=True)

        snapshot = state.to_dict()
        snapshot["waters"] = False

        self.assertTrue(state.waters)


if __name__ == "__main__":
    unittest.main()
