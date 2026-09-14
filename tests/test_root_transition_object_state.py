import unittest
from types import SimpleNamespace

from core.transitions.root_transition import (
    RootTransition,
)
from core.transitions.root_transition_state import (
    RootTransitionState,
)


class RootTransitionObjectStateTests(unittest.TestCase):

    def _entity(
        self,
        name="serpent",
        existence_pct=100.0,
        energy_j=2000.0,
    ):
        return SimpleNamespace(
            name=name,
            existence_pct=existence_pct,
            energy_j=energy_j,
            current_layer="idea_universe",
            root_presence=False,
        )

    def test_state_is_object_only(self):
        state = RootTransitionState()

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
            _ = state["state"]

    def test_initial_values_are_preserved(self):
        state = RootTransitionState()

        self.assertEqual(state.target, "root_universe")
        self.assertEqual(state.status, "created")
        self.assertIsNone(state.creator)
        self.assertEqual(state.existence_cost_pct, 25.0)
        self.assertEqual(state.energy_cost_j, 1000.0)
        self.assertFalse(state.can_enter)

    def test_creation_rejects_invalid_entities(self):
        transition = RootTransition()

        cases = (
            self._entity(name="god"),
            self._entity(existence_pct=99.0),
            self._entity(energy_j=999.0),
        )

        for entity in cases:
            with self.subTest(entity=entity):
                self.assertFalse(
                    transition.create(entity)
                )
                self.assertFalse(
                    hasattr(entity, "root_transition")
                )

    def test_creation_attaches_object_state(self):
        transition = RootTransition()
        entity = self._entity()

        created = transition.create(entity)
        state = entity.root_transition

        self.assertTrue(created)
        self.assertIsInstance(
            state,
            RootTransitionState,
        )
        self.assertEqual(state.target, "root_universe")
        self.assertEqual(state.status, "created")
        self.assertEqual(state.creator, "serpent")
        self.assertEqual(state.existence_cost_pct, 25.0)
        self.assertEqual(state.energy_cost_j, 1000.0)
        self.assertFalse(state.can_enter)
        self.assertEqual(entity.existence_pct, 75.0)
        self.assertEqual(entity.energy_j, 1000.0)

    def test_entry_requires_restored_existence(self):
        transition = RootTransition()
        entity = self._entity()

        transition.create(entity)

        self.assertFalse(
            transition.can_enter(entity)
        )

        entity.existence_pct = 100.0

        self.assertTrue(
            transition.can_enter(entity)
        )

    def test_update_mutates_same_state_object(self):
        transition = RootTransition()
        entity = self._entity()

        transition.create(entity)
        state = entity.root_transition

        self.assertFalse(
            transition.update_entry_status(entity)
        )
        self.assertIs(entity.root_transition, state)
        self.assertFalse(state.can_enter)

        entity.existence_pct = 100.0

        self.assertTrue(
            transition.update_entry_status(entity)
        )
        self.assertIs(entity.root_transition, state)
        self.assertTrue(state.can_enter)

    def test_enter_mutates_same_state_object(self):
        transition = RootTransition()
        entity = self._entity()

        transition.create(entity)
        state = entity.root_transition
        entity.existence_pct = 100.0

        entered = transition.enter(entity)

        self.assertTrue(entered)
        self.assertIs(entity.root_transition, state)
        self.assertEqual(state.status, "used")
        self.assertTrue(state.can_enter)
        self.assertEqual(
            entity.current_layer,
            "root_universe",
        )
        self.assertTrue(entity.root_presence)

    def test_used_transition_cannot_be_entered_again(self):
        transition = RootTransition()
        entity = self._entity()

        transition.create(entity)
        entity.existence_pct = 100.0

        self.assertTrue(transition.enter(entity))
        self.assertFalse(transition.can_enter(entity))
        self.assertFalse(transition.enter(entity))

    def test_to_dict_returns_detached_boundary(self):
        state = RootTransitionState(
            creator="serpent",
        )

        snapshot = state.to_dict()

        self.assertIsInstance(snapshot, dict)
        self.assertEqual(snapshot["state"], "created")

        snapshot["state"] = "changed"
        snapshot["creator"] = "changed"
        snapshot["can_enter"] = True

        self.assertEqual(state.status, "created")
        self.assertEqual(state.creator, "serpent")
        self.assertFalse(state.can_enter)


if __name__ == "__main__":
    unittest.main()
