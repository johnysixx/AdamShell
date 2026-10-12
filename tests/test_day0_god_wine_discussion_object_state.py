import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_god_wine_discussion_state import (
    GodJoinsSerpentLilithTableEvent,
    GodTastesLilithEvent,
    LilithAcidityRevisionResult,
    LilithGivesSerpentLilithTasteEvent,
    SerpentCallsGodToTableEvent,
    SerpentExplainsWineDiscussionEvent,
    WineDiscussionSummaryState,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0GodWineDiscussionObjectStateTests(
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

    def test_god_tasting_event_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_holding_lilith()

        event = (
            scene.god_tastes_lilith()
        )

        self.assertIsInstance(
            event,
            GodTastesLilithEvent,
        )

        self.assertTrue(
            event.effects_applied
        )

        self.assertGreater(
            event.energy_after,
            event.energy_before,
        )

        self._assert_object_only(
            event,
            "effects_applied",
        )

    def test_call_and_join_are_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_first_lilith_taste()

        called = (
            scene
            .serpent_notices_god_and_calls_him_over()
        )

        joined = (
            scene
            .god_joins_serpent_and_lilith_at_table()
        )

        self.assertIsInstance(
            called,
            SerpentCallsGodToTableEvent,
        )

        self.assertIsInstance(
            joined,
            GodJoinsSerpentLilithTableEvent,
        )

        self.assertEqual(
            joined.companions,
            (
                "serpent",
                "lilith",
            ),
        )

        self._assert_object_only(
            called,
            "caller",
        )

        self._assert_object_only(
            joined,
            "companions",
        )

    def test_explanation_has_typed_summary(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_at_table()

        event = (
            scene
            .serpent_explains_wine_discussion_to_god()
        )

        self.assertIsInstance(
            event,
            SerpentExplainsWineDiscussionEvent,
        )

        self.assertIsInstance(
            event.summary,
            WineDiscussionSummaryState,
        )

        self.assertTrue(
            event.summary.fuller_flavor
        )

        self.assertTrue(
            event.summary.sweetness
        )

        self.assertTrue(
            event.summary.bitterness
        )

        self._assert_object_only(
            event,
            "summary",
        )

        self._assert_object_only(
            event.summary,
            "sweetness",
        )

    def test_acidity_revision_result_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_at_table()

        scene.serpent_explains_wine_discussion_to_god()

        result = (
            scene
            .lilith_rejects_bitterness_and_proposes_acidity()
        )

        self.assertIsInstance(
            result,
            LilithAcidityRevisionResult,
        )

        self.assertEqual(
            result.rejection.rejected_property,
            "bitterness",
        )

        self.assertTrue(
            result.idea.desired_property.acidity
        )

        self.assertEqual(
            result.idea.revision.remove,
            "bitterness",
        )

        self.assertEqual(
            result.idea.revision.add,
            "acidity",
        )

        self._assert_object_only(
            result,
            "idea",
        )

    def test_serpent_tasting_event_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_at_table()

        scene.serpent_explains_wine_discussion_to_god()

        scene.lilith_rejects_bitterness_and_proposes_acidity()

        event = (
            scene
            .lilith_gives_serpent_taste_of_lilith()
        )

        self.assertIsInstance(
            event,
            LilithGivesSerpentLilithTasteEvent,
        )

        self.assertEqual(
            event.giver,
            "lilith",
        )

        self.assertEqual(
            event.taster,
            "serpent",
        )

        self.assertTrue(
            event.effects_applied
        )

        self._assert_object_only(
            event,
            "giver",
        )


if __name__ == "__main__":
    unittest.main()
