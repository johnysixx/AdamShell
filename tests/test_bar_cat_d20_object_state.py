import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    CatD20Profile,
    CatD20State,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class FixedD20:

    def __init__(self, value):
        self.value = value

    def randint(self, minimum, maximum):
        return self.value


class BarCatD20ObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key
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
                    mapping_method
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[key]

    def _bar(self):
        universe = Universe()
        universe.universe_registry = (
            UniverseRegistry()
        )
        return MeetingPlace(
            universe
        )

    def _scene(self):
        bar = self._bar()
        universe = bar.universe
        return Day0FirstBarShift(
            universe=universe,
            meeting_place=bar,
            library=Library(universe),
            gods=Gods(universe),
            idea_entities=IdeaEntities(
                universe
            ),
        )

    def test_cat_d20_state_has_no_mapping_api(
        self
    ):
        profile = CatD20Profile(
            color="orange",
            fur_length="short",
            pattern="tabby",
            eye_color="green",
            sex="male",
        )
        state = CatD20State(
            canonical_profile=profile
        )

        self._assert_object_only(
            state,
            "is_cat"
        )
        self._assert_object_only(
            profile,
            "color"
        )

    def test_arriving_cat_uses_object_state(
        self
    ):
        bar = self._bar()
        result = bar.welcome_cat_d20()
        state = result["cat"].cat_d20

        self.assertIsInstance(
            state,
            CatD20State
        )
        self.assertTrue(state.is_cat)
        self.assertFalse(state.is_die)
        self.assertFalse(
            state.can_be_thrown
        )
        self._assert_object_only(
            state,
            "turn_count"
        )

    def test_turn_mutates_same_state_object(
        self
    ):
        bar = self._bar()
        cat = (
            bar.welcome_cat_d20()
            ["cat"]
        )
        state = cat.cat_d20

        event = bar.turn_cat_d20_in_box(
            rng=FixedD20(17)
        )

        self.assertIs(
            cat.cat_d20,
            state
        )
        self.assertEqual(
            state.current_value,
            17
        )
        self.assertEqual(
            state.turn_count,
            1
        )
        self.assertEqual(
            state.turn_history[0][
                "value"
            ],
            event["value"]
        )
        self.assertIsNot(
            state.turn_history[0],
            event
        )

    def test_canonical_profile_is_object(
        self
    ):
        bar = self._bar()
        cat = (
            bar.welcome_cat_d20()
            ["cat"]
        )

        event = (
            bar
            .cat_d20_prepare_pazuzu_profile()
        )
        profile = (
            cat.cat_d20
            .canonical_profile
        )

        self.assertIsInstance(
            profile,
            CatD20Profile
        )
        self.assertEqual(
            profile.to_dict(),
            event["profile"]
        )
        event["profile"]["color"] = (
            "changed"
        )
        self.assertEqual(
            profile.color,
            "black"
        )

    def test_garfield_lifecycle_reuses_state(
        self
    ):
        scene = self._scene()
        scene.advance_to_cat_d20_arrival()
        state = scene.cat_d20.cat_d20

        scene.everyone_scratches_cat_d20()
        scene.cat_d20_sets_next_birth_to_garfield()

        self.assertIs(
            scene.cat_d20.cat_d20,
            state
        )
        self.assertTrue(
            state.garfield_pending
        )
        self.assertIsInstance(
            state.canonical_profile,
            CatD20Profile
        )

        scene.garfield_arrives_from_cat_d20_setting()

        self.assertFalse(
            state.garfield_pending
        )
        self.assertEqual(
            state.last_manifested_target,
            "garfield"
        )

    def test_snapshot_is_detached(
        self
    ):
        profile = CatD20Profile(
            color="black",
            fur_length="short",
            pattern="solid",
            eye_color="gold",
            sex="female",
        )
        state = CatD20State(
            current_value=17,
            turn_count=1,
            turn_history=[
                {
                    "value": 17,
                }
            ],
            canonical_target="garfield",
            canonical_profile=profile,
            garfield_pending=True,
        )

        snapshot = state.to_dict()
        snapshot["turn_history"][0][
            "value"
        ] = 1
        snapshot["canonical_profile"][
            "color"
        ] = "changed"

        self.assertEqual(
            state.turn_history[0][
                "value"
            ],
            17
        )
        self.assertEqual(
            state.canonical_profile.color,
            "black"
        )


if __name__ == "__main__":
    unittest.main()
