import unittest

from cats.cats import Cats
from cats.cats_state import CatsState
from universe.universe import Universe


class CatsObjectStateTests(unittest.TestCase):

    def _layer(self):
        universe = Universe()
        cats = Cats(universe)

        return universe, cats

    def test_state_is_object_only(self):
        state = CatsState()

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
        _, cats = self._layer()
        state = cats.cats_state

        self.assertIs(cats.state, state)
        self.assertEqual(state.layer_type, "species_layer")
        self.assertEqual(state.status, "created")
        self.assertEqual(state.cats, [])
        self.assertEqual(state.events, [])
        self.assertEqual(state.tick_count, 0)
        self.assertEqual(state.default_idea_energy, 100)
        self.assertEqual(
            state.access_rules,
            {
                "can_access_anywhere": True,
                "access_via": [
                    "boxes",
                    "cat_doors",
                ],
            },
        )

    def test_values_are_owned_by_same_state_object(self):
        _, cats = self._layer()
        state = cats.cats_state

        self.assertIs(cats.cats, state.cats)
        self.assertIs(cats.events, state.events)
        self.assertIs(cats.allowed_colors, state.allowed_colors)
        self.assertIs(cats.allowed_patterns, state.allowed_patterns)
        self.assertIs(
            cats.allowed_eye_colors,
            state.allowed_eye_colors,
        )
        self.assertIs(
            cats.allowed_fur_lengths,
            state.allowed_fur_lengths,
        )
        self.assertIs(cats.allowed_sexes, state.allowed_sexes)
        self.assertIs(cats.access_rules, state.access_rules)

    def test_world_keeps_object_and_dict_boundaries(self):
        universe, cats = self._layer()

        self.assertIs(
            universe.world["cats_state"],
            cats.cats_state,
        )
        self.assertIsInstance(
            universe.world["cats"],
            dict,
        )
        self.assertIsInstance(
            universe.world["cats"]["cats_state"],
            dict,
        )

    def test_public_registries_remain_live_boundaries(self):
        universe, cats = self._layer()
        boundary = universe.world["cats"]

        self.assertIs(boundary["cats"], cats.cats)
        self.assertIs(
            boundary["access_rules"],
            cats.access_rules,
        )
        self.assertIs(
            boundary["allowed_colors"],
            cats.allowed_colors,
        )

    def test_cat_creation_mutates_same_state_object(self):
        universe, cats = self._layer()
        state = cats.cats_state

        cat = cats.create_cat(
            name="black_cat",
            color="black",
            fur_length="short",
        )

        self.assertIs(cats.cats_state, state)
        self.assertEqual(state.cats, [cat])
        self.assertIs(
            universe.world["cats"]["cats"],
            state.cats,
        )
        self.assertEqual(
            universe.world["cats"]["cats_state"]["cats"],
            [cat],
        )

    def test_events_and_tick_mutate_same_state_object(self):
        universe, cats = self._layer()
        state = cats.cats_state
        event = {
            "name": "cat_seen",
        }

        cats.emit_event(event)

        self.assertEqual(state.events, [event])
        self.assertEqual(
            universe.world["cats"]["cats_state"]["events"],
            [event],
        )

        report = cats.tick()

        self.assertIs(cats.cats_state, state)
        self.assertEqual(state.tick_count, 1)
        self.assertEqual(len(state.events), 1)
        self.assertEqual(
            state.events[0]["name"],
            "cats_tick_completed",
        )
        self.assertEqual(report["tick"], 1)
        self.assertEqual(
            universe.world["cats"]["cats_state"]["tick_count"],
            1,
        )

    def test_public_state_snapshot_is_detached(self):
        _, cats = self._layer()
        snapshot = cats.public_state["cats_state"]

        snapshot["events"].append(
            {"name": "changed"}
        )
        snapshot["access_rules"]["access_via"].append(
            "changed"
        )
        snapshot["allowed_colors"].append("changed")
        snapshot["cats"].append(
            {"name": "changed"}
        )

        self.assertEqual(cats.events, [])
        self.assertNotIn(
            "changed",
            cats.access_rules["access_via"],
        )
        self.assertNotIn("changed", cats.allowed_colors)
        self.assertEqual(cats.cats, [])

    def test_to_dict_returns_detached_values(self):
        state = CatsState()
        snapshot = state.to_dict()

        snapshot["events"].append(
            {"name": "changed"}
        )
        snapshot["access_rules"]["access_via"].append(
            "changed"
        )
        snapshot["allowed_patterns"].append("changed")
        snapshot["cats"].append(
            {"name": "changed"}
        )

        self.assertEqual(state.events, [])
        self.assertNotIn(
            "changed",
            state.access_rules["access_via"],
        )
        self.assertNotIn("changed", state.allowed_patterns)
        self.assertEqual(state.cats, [])


if __name__ == "__main__":
    unittest.main()
