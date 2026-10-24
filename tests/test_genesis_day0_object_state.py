import unittest

from genesis.day0 import GenesisDay0
from genesis.day0_state import (
    GenesisDay0PrinciplesPresentEvent,
    GenesisDay0State,
)
from idea_entities import IdeaEntities
from idea_entities.prefysical_fire_origin import (
    PrefysicalFireAlreadyBurningResult,
    PrefysicalFireIgnitedResult,
    PrefysicalFireIgnitionFailedResult,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class FixedRng:

    def __init__(self, values):
        self.values = iter(values)

    def randint(self, start, end):
        return next(self.values)

    def random(self):
        return 0.99

    def choice(self, sequence):
        return sequence[0]

    def sample(self, population, k):
        return list(population)[:k]


class GenesisDay0ObjectStateTests(unittest.TestCase):

    def _day0(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        idea_entities = IdeaEntities(universe)

        for name in (
            "serpent",
            "lilith",
            "pazuzu_masculine_principle",
        ):
            universe.world[name] = {
                "name": name,
                "type": "idea_entity",
                "energy_j": 100.0,
            }

        day0 = GenesisDay0(universe, idea_entities)

        return universe, idea_entities, day0

    def test_state_is_object_only(self):
        state = GenesisDay0State()

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
            _ = state["status"]

    def test_initial_values_are_preserved(self):
        _, _, day0 = self._day0()
        state = day0.genesis_day0_state

        self.assertIs(day0.state, state)
        self.assertEqual(state.name, "genesis_day0")
        self.assertEqual(state.status, "principles_required")
        self.assertFalse(state.physical_time_exists)
        self.assertFalse(state.physical_space_exists)
        self.assertEqual(state.history, [])

    def test_principle_verification_mutates_same_object(self):
        _, _, day0 = self._day0()
        state = day0.genesis_day0_state

        event = day0.verify_principles()

        self.assertIs(day0.genesis_day0_state, state)
        self.assertEqual(state.status, "ready_for_fire_origin")
        self.assertIsInstance(
            event,
            GenesisDay0PrinciplesPresentEvent,
        )
        self.assertIs(
            state.history[-1],
            event,
        )

    def test_begin_mutates_same_object(self):
        _, _, day0 = self._day0()
        state = day0.genesis_day0_state

        event = day0.begin_fire_origin()

        self.assertIs(day0.genesis_day0_state, state)
        self.assertEqual(state.status, "seeking_warmth")
        self.assertIs(
            state.history[-1],
            event,
        )
        self.assertEqual(
            len(state.history),
            2,
        )

    def test_failed_attempt_updates_object_status(self):
        _, _, day0 = self._day0()
        state = day0.genesis_day0_state

        result = day0.attempt_fire(
            rng=FixedRng([10, 1])
        )

        self.assertIs(day0.genesis_day0_state, state)
        self.assertEqual(result.result, "fire_not_ignited")
        self.assertEqual(state.status, "seeking_warmth")
        self.assertIs(state.history[-1], result)

    def test_successful_attempt_updates_object_status(self):
        _, _, day0 = self._day0()
        state = day0.genesis_day0_state

        result = day0.attempt_fire(
            rng=FixedRng([20, 1])
        )

        self.assertIs(day0.genesis_day0_state, state)
        self.assertEqual(
            result.result,
            "prefysical_fire_ignited",
        )
        self.assertEqual(state.status, "eternal_fire_exists")
        self.assertIs(state.history[-1], result)

    def test_understanding_fire_updates_same_object(self):
        _, _, day0 = self._day0()
        day0.attempt_fire(rng=FixedRng([20, 1]))
        state = day0.genesis_day0_state

        result = day0.understand_fire()

        self.assertIs(day0.genesis_day0_state, state)
        self.assertEqual(
            state.status,
            "fire_guarded_fuel_search_active",
        )
        self.assertIs(
            state.history[-1],
            result,
        )

    def test_advance_fire_records_history_on_same_object(self):
        _, _, day0 = self._day0()
        day0.attempt_fire(rng=FixedRng([20, 1]))
        state = day0.genesis_day0_state
        before = len(state.history)

        result = day0.advance_fire()

        self.assertIs(day0.genesis_day0_state, state)
        self.assertEqual(len(state.history), before + 1)
        self.assertIs(
            state.history[-1],
            result,
        )

    def test_fire_result_public_state_is_snapshot_boundary(
        self
    ):
        _, _, day0 = self._day0()

        result = day0.attempt_fire(
            rng=FixedRng([10, 1])
        )

        self.assertIsInstance(
            result,
            PrefysicalFireIgnitionFailedResult,
        )
        self.assertIs(
            day0.history[-1],
            result,
        )

        public_state = day0.public_state

        self.assertIsInstance(
            public_state["history"][-1],
            dict,
        )
        self.assertEqual(
            public_state["history"][-1],
            result.to_dict(),
        )
        self.assertIsInstance(
            public_state[
                "genesis_day0_state"
            ]["history"][-1],
            dict,
        )

    def test_repeated_fire_attempt_stays_object_state(
        self
    ):
        _, _, day0 = self._day0()

        ignited = day0.attempt_fire(
            rng=FixedRng([20, 1])
        )

        repeated = day0.attempt_fire(
            rng=FixedRng([])
        )

        self.assertIsInstance(
            ignited,
            PrefysicalFireIgnitedResult,
        )
        self.assertIsInstance(
            repeated,
            PrefysicalFireAlreadyBurningResult,
        )
        self.assertEqual(
            repeated.result,
            "prefysical_eternal_fire_already_burns",
        )
        self.assertEqual(
            day0.status,
            "eternal_fire_exists",
        )
        self.assertIs(
            day0.history[-1],
            repeated,
        )

    def test_public_state_keeps_detached_dict_boundary(self):
        _, _, day0 = self._day0()
        day0.verify_principles()

        public_state = day0.public_state

        self.assertIsInstance(public_state, dict)
        self.assertIsInstance(
            public_state["genesis_day0_state"],
            dict,
        )
        self.assertEqual(
            public_state["state"],
            "ready_for_fire_origin",
        )

        public_state["history"].append("changed")
        public_state["genesis_day0_state"][
            "history"
        ].append("changed")

        self.assertEqual(len(day0.history), 1)

    def test_public_boundary_is_detached_from_object_history(self):
        _, _, day0 = self._day0()
        event = day0.verify_principles()
        state = day0.genesis_day0_state

        self.assertFalse(hasattr(state, "to_dict"))
        self.assertIs(state.history[0], event)

        snapshot = day0.public_state

        snapshot["history"][0][
            "participants"
        ].append("changed")

        snapshot["genesis_day0_state"]["history"][0][
            "participants"
        ].append("changed_again")

        self.assertIs(state.history[0], event)
        self.assertEqual(
            event.participants,
            (
                "serpent",
                "lilith",
                "pazuzu_masculine_principle",
            ),
        )


if __name__ == "__main__":
    unittest.main()
