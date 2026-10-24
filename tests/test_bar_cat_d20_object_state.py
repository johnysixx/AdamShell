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
    CatD20TurnEvent,
    CatD20CanonicalProfilePreparedEvent,
    CatD20CanonicalOrigin,
    CatD20GibManifestedEvent,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from meeting_place.cat_d20_turn_state import (
    CatD20TurnResult,
)
from meeting_place.cat_d20_gib_manifestation_state import (
    CatD20GibManifestationResult,
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
        state = result.cat.cat_d20

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
            bar.welcome_cat_d20().cat
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
        stored = (
            state.turn_history[0]
        )

        self.assertIsInstance(
            stored,
            CatD20TurnEvent,
        )

        self.assertIsInstance(
            event,
            CatD20TurnResult,
        )

        self.assertEqual(
            stored.value,
            event.value
        )

        self._assert_object_only(
            event,
            "value"
        )

        self._assert_object_only(
            stored,
            "value"
        )

        secret = (
            bar.cat_d20_secret_history[-1]
        )

        quantum = (
            bar.universe
            .quantum_events[-1]
        )

        self.assertIsInstance(
            secret,
            CatD20TurnEvent,
        )

        self.assertIsInstance(
            quantum,
            CatD20TurnEvent,
        )

        self.assertIsNot(
            stored,
            secret,
        )

        self.assertIsNot(
            secret,
            quantum,
        )

    def test_canonical_profile_is_object(
        self
    ):
        bar = self._bar()
        cat = (
            bar.welcome_cat_d20().cat
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
        self.assertIsInstance(
            event,
            CatD20CanonicalProfilePreparedEvent,
        )

        self.assertIsInstance(
            event.profile,
            CatD20Profile,
        )

        self.assertEqual(
            profile.to_dict(),
            event.profile.to_dict()
        )

        self._assert_object_only(
            event,
            "profile"
        )

        secret = (
            bar.cat_d20_secret_history[-1]
        )

        quantum = (
            bar.universe
            .quantum_events[-1]
        )

        self.assertIsInstance(
            secret,
            CatD20CanonicalProfilePreparedEvent,
        )

        self.assertIsInstance(
            quantum,
            CatD20CanonicalProfilePreparedEvent,
        )

        self._assert_object_only(
            secret,
            "profile"
        )

        self.assertEqual(
            secret.profile.color,
            "black"
        )

        self.assertEqual(
            quantum.target_name,
            "pazuzu"
        )

        self.assertIsNot(
            secret,
            quantum,
        )

        snapshot = event.to_dict()

        snapshot[
            "profile"
        ][
            "color"
        ] = "changed"

        self.assertEqual(
            event.profile.color,
            "black"
        )

        self.assertEqual(
            profile.color,
            "black"
        )

        self.assertEqual(
            secret.profile.color,
            "black"
        )

    def test_gib_manifestation_uses_object_history(
        self
    ):
        bar = self._bar()

        bar.welcome_cat_d20()

        bar.cat_d20_prepare_pazuzu_profile()

        prepared = (
            bar.cat_d20_prepare_pazuzu_profile()
        )

        self.assertIsInstance(
            prepared,
            CatD20CanonicalProfilePreparedEvent,
        )

        self.assertEqual(
            prepared.target_name,
            "gib"
        )

        result = (
            bar.manifest_gib_from_cat_d20(
                prepared
            )
        )

        self.assertIsInstance(
            result,
            CatD20GibManifestationResult,
        )

        gib = result.cat

        self.assertTrue(
            result.created
        )

        self._assert_object_only(
            result,
            "cat"
        )

        self.assertEqual(
            gib.name,
            "gib"
        )

        self.assertIsInstance(
            gib.canonical_origin,
            CatD20CanonicalOrigin,
        )

        self._assert_object_only(
            gib.canonical_origin,
            "base_profile"
        )

        self.assertEqual(
            gib.canonical_origin
            .base_profile
            .fur_length,
            "short"
        )

        self.assertEqual(
            gib.canonical_origin
            .mutation_trait,
            "fur_length"
        )

        self.assertEqual(
            gib.canonical_origin
            .mutation_from,
            "short"
        )

        self.assertEqual(
            gib.canonical_origin
            .mutation_to,
            "long"
        )

        secret = (
            bar.cat_d20_secret_history[-1]
        )

        quantum = (
            bar.universe
            .quantum_events[-1]
        )

        self.assertIsInstance(
            secret,
            CatD20GibManifestedEvent,
        )

        self.assertIsInstance(
            quantum,
            CatD20GibManifestedEvent,
        )

        self._assert_object_only(
            secret,
            "profile"
        )

        self.assertEqual(
            secret.profile.fur_length,
            "long"
        )

        self.assertTrue(
            secret.all_dice_rotation_requested
        )

        self.assertIsNot(
            secret,
            quantum,
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assertEqual(
            result.profile.fur_length,
            "long"
        )

        self.assertEqual(
            secret.profile.fur_length,
            "long"
        )

        self.assertEqual(
            gib.canonical_origin
            .base_profile
            .fur_length,
            "short"
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
                CatD20TurnEvent(
                    cat="cat_d20",
                    box="cat_d20_box",
                    previous_value=None,
                    value=17,
                    turn_number=1,
                )
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
            state.turn_history[0].value,
            17
        )
        self.assertEqual(
            state.canonical_profile.color,
            "black"
        )

        with self.assertRaises(
            TypeError
        ):
            CatD20State(
                turn_history=[
                    {
                        "value": 17,
                    }
                ]
            )


if __name__ == "__main__":
    unittest.main()
