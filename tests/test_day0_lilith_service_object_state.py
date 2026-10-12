import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_lilith_service_state import (
    BartenderLearnsLilithDrinkResult,
    DrinkIngredientRequestState,
    LilithCorrectsVodkaWithLemonEvent,
    LilithDrinkEffectAppliedResult,
    LilithDrinkRevisionResult,
    LilithDrinkServiceResult,
    LilithJoinsSerpentAtTableEvent,
    LilithRequestedRecipeState,
    LilithRequestsSecondSugarCubeEvent,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0LilithServiceObjectStateTests(
    unittest.TestCase
):

    def _scene(self):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        return Day0FirstBarShift(
            universe=universe,
            meeting_place=MeetingPlace(
                universe
            ),
            library=Library(
                universe
            ),
            gods=Gods(
                universe
            ),
            idea_entities=IdeaEntities(
                universe
            ),
        )

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
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
            _ = value[key]

    def _prepare_for_lilith_service(
        self,
    ):
        scene = self._scene()

        scene.advance_to_lilith_entry()
        scene.lilith_orders_vodka_with_lemon()
        scene.serpent_and_lilith_begin_conversation()
        scene.play_serpent_lilith_first_conversation()
        scene.serpent_and_lilith_agree_on_table()
        scene.serpent_moves_from_bar_to_existing_table()
        scene.bartender_returns_with_lemon()

        return scene

    def test_correction_uses_typed_recipe_request(
        self
    ):
        scene = (
            self._prepare_for_lilith_service()
        )

        scene.bartender_makes_vodka_with_lemon()

        event = (
            scene
            .lilith_corrects_vodka_with_lemon()
        )

        self.assertIsInstance(
            event,
            LilithCorrectsVodkaWithLemonEvent,
        )

        self.assertIsInstance(
            event.requested_recipe,
            LilithRequestedRecipeState,
        )

        self.assertEqual(
            event.requested_recipe.lemon,
            "whole",
        )

        self._assert_object_only(
            event.requested_recipe,
            "lemon",
        )

    def test_learned_recipe_result_is_object_only(
        self
    ):
        scene = (
            self._prepare_for_lilith_service()
        )

        scene.bartender_makes_vodka_with_lemon()
        scene.lilith_corrects_vodka_with_lemon()

        result = (
            scene
            .bartender_learns_lilith_drink()
        )

        self.assertIsInstance(
            result,
            BartenderLearnsLilithDrinkResult,
        )

        self.assertEqual(
            result.recipe.name,
            "lilith",
        )

        self.assertEqual(
            result.learned.drink,
            "lilith",
        )

        self._assert_object_only(
            result,
            "recipe",
        )

    def test_effect_result_is_object_only(
        self
    ):
        scene = (
            self._prepare_for_lilith_service()
        )

        scene.bartender_makes_vodka_with_lemon()
        scene.lilith_corrects_vodka_with_lemon()
        scene.bartender_learns_lilith_drink()

        result = (
            scene.apply_lilith_drink_effect(
                scene.lilith
            )
        )

        self.assertIsInstance(
            result,
            LilithDrinkEffectAppliedResult,
        )

        self.assertEqual(
            result.energy_j,
            1.0,
        )

        self._assert_object_only(
            result,
            "energy_j",
        )

    def test_service_and_revision_results_are_objects(
        self
    ):
        scene = (
            self._prepare_for_lilith_service()
        )

        scene.bartender_makes_vodka_with_lemon()
        scene.lilith_corrects_vodka_with_lemon()
        scene.bartender_learns_lilith_drink()

        service = (
            scene
            .bartender_hands_lilith_drink_and_receipt()
        )

        request = (
            scene
            .lilith_tastes_and_requests_second_sugar_cube()
        )

        revision = (
            scene
            .bartender_adds_second_sugar_cube()
        )

        self.assertIsInstance(
            service,
            LilithDrinkServiceResult,
        )

        self.assertIsInstance(
            request,
            LilithRequestsSecondSugarCubeEvent,
        )

        self.assertIsInstance(
            request.request,
            DrinkIngredientRequestState,
        )

        self.assertIsInstance(
            revision,
            LilithDrinkRevisionResult,
        )

        self.assertIs(
            revision.drink,
            service.drink,
        )

        self.assertEqual(
            revision.recipe
            .ingredients["sugar"]
            .shots,
            2,
        )

        self._assert_object_only(
            service,
            "drink",
        )
        self._assert_object_only(
            request,
            "request",
        )
        self._assert_object_only(
            revision,
            "recipe",
        )

    def test_table_join_event_is_object_only(
        self
    ):
        scene = (
            self._prepare_for_lilith_service()
        )

        scene.bartender_makes_vodka_with_lemon()
        scene.lilith_corrects_vodka_with_lemon()
        scene.bartender_learns_lilith_drink()
        scene.bartender_hands_lilith_drink_and_receipt()
        scene.lilith_tastes_and_requests_second_sugar_cube()
        scene.bartender_adds_second_sugar_cube()

        event = (
            scene
            .lilith_joins_serpent_at_existing_table()
        )

        self.assertIsInstance(
            event,
            LilithJoinsSerpentAtTableEvent,
        )

        self.assertEqual(
            event.companion,
            "serpent",
        )

        self.assertEqual(
            scene.lilith.bar_state.location,
            "table",
        )

        self._assert_object_only(
            event,
            "companion",
        )


if __name__ == "__main__":
    unittest.main()
