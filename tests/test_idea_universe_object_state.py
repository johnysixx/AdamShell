import unittest

from gods.gods import Gods
from idea_universe import IdeaUniverse
from idea_universe.idea_universe_state import IdeaUniverseState
from multiverse import UniverseRegistry
from universe.bootstraps.idea_genesis_bootstrap import (
    IdeaGenesisBootstrap,
)
from universe.universe import Universe


class IdeaUniverseObjectStateTests(unittest.TestCase):

    def _idea_universe(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        idea_universe = IdeaUniverse(universe)

        return universe, idea_universe

    def _genesis(self):
        universe, idea_universe = self._idea_universe()
        genesis = IdeaGenesisBootstrap(
            universe=universe,
            idea_universe=idea_universe,
            gods=Gods(universe),
        )

        return universe, idea_universe, genesis

    def test_state_is_object_only(self):
        state = IdeaUniverseState()

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
            _ = state["tick_count"]

    def test_initial_values_are_preserved(self):
        _, idea_universe = self._idea_universe()
        state = idea_universe.idea_universe_state

        self.assertIs(idea_universe.state, state)
        self.assertEqual(state.status, "created")
        self.assertFalse(state.part_of_physics)
        self.assertEqual(state.tick_count, 0)
        self.assertFalse(state.stellar_epoch_started)
        self.assertFalse(state.heavenly_lights_created)
        self.assertFalse(state.heaven_ordered)
        self.assertFalse(
            state.celestial_stations_established
        )
        self.assertFalse(state.divine_order_established)
        self.assertFalse(state.aquatic_life_archetype)
        self.assertFalse(state.flying_life_archetype)
        self.assertFalse(state.land_life_archetype)

    def test_scalar_interface_mutates_same_state_object(self):
        _, idea_universe = self._idea_universe()
        state = idea_universe.idea_universe_state

        idea_universe.tick_count = 3
        idea_universe.stellar_epoch_started = True
        idea_universe.heaven_ordered = True
        idea_universe.divine_order_established = True

        self.assertIs(idea_universe.idea_universe_state, state)
        self.assertEqual(state.tick_count, 3)
        self.assertTrue(state.stellar_epoch_started)
        self.assertTrue(state.heaven_ordered)
        self.assertTrue(state.divine_order_established)

    def test_genesis_days_mutate_same_state_object(self):
        _, idea_universe, genesis = self._genesis()
        state = idea_universe.idea_universe_state

        genesis.run()
        genesis.let_there_be_light()
        genesis.let_there_be_space()
        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()
        genesis.let_there_be_life_in_waters_and_sky()
        genesis.let_there_be_land_life()

        self.assertIs(idea_universe.idea_universe_state, state)
        self.assertTrue(state.heavenly_lights_created)
        self.assertTrue(state.stellar_epoch_started)
        self.assertTrue(state.aquatic_life_archetype)
        self.assertTrue(state.flying_life_archetype)
        self.assertTrue(state.land_life_archetype)

    def test_tick_mutates_same_state_object(self):
        _, idea_universe = self._idea_universe()
        state = idea_universe.idea_universe_state

        result = idea_universe.tick()

        self.assertIs(idea_universe.idea_universe_state, state)
        self.assertEqual(result, 1)
        self.assertEqual(state.tick_count, 1)

    def test_world_stores_state_object_and_dict_boundary(self):
        universe, idea_universe = self._idea_universe()

        self.assertIs(
            universe.world["idea_universe_state"],
            idea_universe.idea_universe_state,
        )
        self.assertIsInstance(
            universe.world["idea_universe"],
            dict,
        )
        self.assertIsInstance(
            universe.world["idea_universe"][
                "idea_universe_state"
            ],
            dict,
        )

    def test_registries_remain_live_boundary_collections(self):
        universe, idea_universe = self._idea_universe()
        boundary = universe.world["idea_universe"]

        self.assertIs(boundary["entities"], idea_universe.entities)
        self.assertIs(boundary["events"], idea_universe.events)
        self.assertIs(
            boundary["starry_sky"],
            idea_universe.starry_sky,
        )
        self.assertIs(
            boundary["primordial_waters"],
            idea_universe.primordial_waters,
        )

    def test_public_state_object_snapshot_is_detached(self):
        _, idea_universe = self._idea_universe()
        idea_universe.stellar_epoch_started = True

        public_state = idea_universe.public_state
        public_state["idea_universe_state"][
            "stellar_epoch_started"
        ] = False

        self.assertTrue(
            idea_universe
            .idea_universe_state
            .stellar_epoch_started
        )

    def test_stellar_epoch_refreshes_world_boundary(self):
        universe, idea_universe, genesis = self._genesis()

        genesis.run()
        genesis.let_there_be_light()
        genesis.let_there_be_space()
        genesis.let_there_be_land_and_vegetation()
        genesis.let_there_be_heavenly_lights()

        result = idea_universe.run_primordial_stellar_epoch()

        self.assertIs(
            universe.world["idea_universe"][
                "primordial_nebula"
            ],
            result["primordial_nebula"],
        )

    def test_to_dict_is_detached_boundary(self):
        state = IdeaUniverseState(
            stellar_epoch_started=True
        )

        snapshot = state.to_dict()
        snapshot["stellar_epoch_started"] = False

        self.assertTrue(state.stellar_epoch_started)


if __name__ == "__main__":
    unittest.main()
