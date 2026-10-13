import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_garfield_manifestation_state import (
    GarfieldArrivalResult,
    GarfieldArrivesAtBarEvent,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    CatD20GarfieldTargetPreparedEvent,
    CatD20Profile,
)
from meeting_place.cat_arrival_state import (
    CatBarArrivalResult,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0GarfieldManifestationObjectStateTests(
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

    def test_prepared_target_returns_object_event(
        self
    ):
        scene = self._scene()

        scene.advance_to_cat_d20_arrival()
        scene.wager_participants_accept_two_judge_panel()
        scene.bartender_suggests_inviting_bouncer_inside()
        scene.everyone_scratches_cat_d20()

        event = (
            scene
            .cat_d20_sets_next_birth_to_garfield()
        )

        self.assertIsInstance(
            event,
            CatD20GarfieldTargetPreparedEvent,
        )

        self.assertIsInstance(
            event.profile,
            CatD20Profile,
        )

        self.assertEqual(
            event.target_name,
            "garfield",
        )

        self.assertEqual(
            event.profile.color,
            "orange",
        )

        self._assert_object_only(
            event,
            "target_name",
        )

        self._assert_object_only(
            event.profile,
            "color",
        )

    def test_prepared_event_history_is_detached(
        self
    ):
        scene = self._scene()

        scene.advance_to_cat_d20_arrival()

        returned = (
            scene
            .cat_d20_sets_next_birth_to_garfield()
        )

        stored = next(
            event
            for event in scene.history
            if isinstance(
                event,
                CatD20GarfieldTargetPreparedEvent,
            )
        )

        self.assertIsNot(
            returned,
            stored,
        )

        returned.profile.color = (
            "changed"
        )

        self.assertEqual(
            stored.profile.color,
            "orange",
        )

    def test_manifestation_uses_profile_object(
        self
    ):
        scene = self._scene()

        scene.advance_to_cat_d20_arrival()

        prepared = (
            scene
            .cat_d20_sets_next_birth_to_garfield()
        )

        result = (
            scene
            .garfield_arrives_from_cat_d20_setting()
        )

        self.assertIsInstance(
            result,
            GarfieldArrivalResult,
        )

        self.assertIsInstance(
            result.profile,
            CatD20Profile,
        )

        self.assertEqual(
            result.profile,
            prepared.profile,
        )

        self.assertIsNot(
            result.profile,
            prepared.profile,
        )

        self.assertEqual(
            result.profile.color,
            "orange",
        )

        self.assertEqual(
            result.profile.pattern,
            "tabby",
        )

        self._assert_object_only(
            result,
            "profile",
        )

        self._assert_object_only(
            result.profile,
            "color",
        )

    def test_garfield_arrival_result_is_object_graph(
        self
    ):
        scene = self._scene()

        scene.advance_to_cat_d20_arrival()
        scene.cat_d20_sets_next_birth_to_garfield()

        result = (
            scene
            .garfield_arrives_from_cat_d20_setting()
        )

        self.assertIsInstance(
            result,
            GarfieldArrivalResult,
        )

        self.assertIsInstance(
            result.event,
            GarfieldArrivesAtBarEvent,
        )

        self.assertIsInstance(
            result.ordinary_arrival,
            CatBarArrivalResult,
        )

        self.assertIs(
            result.event.arrival,
            result.ordinary_arrival,
        )

        self.assertIs(
            result.garfield,
            scene.garfield,
        )

        self.assertEqual(
            result.garfield.name,
            "garfield",
        )

        self._assert_object_only(
            result.event,
            "created",
        )

        self._assert_object_only(
            result.ordinary_arrival,
            "entered",
        )

    def test_history_serializes_garfield_arrival(
        self
    ):
        scene = self._scene()

        scene.advance_to_cat_d20_arrival()
        scene.cat_d20_sets_next_birth_to_garfield()
        result = (
            scene
            .garfield_arrives_from_cat_d20_setting()
        )

        history_event = next(
            event
            for event in scene.history
            if (
                isinstance(
                    event,
                    dict,
                )
                and event["name"]
                == "garfield_arrives_at_bar"
            )
        )

        self.assertIsInstance(
            history_event["arrival"],
            dict,
        )

        self.assertEqual(
            history_event["cat"],
            "garfield",
        )

        self.assertEqual(
            history_event["arrival"]["cat"],
            "garfield",
        )

        self.assertEqual(
            history_event["created"],
            result.event.created,
        )


if __name__ == "__main__":
    unittest.main()
