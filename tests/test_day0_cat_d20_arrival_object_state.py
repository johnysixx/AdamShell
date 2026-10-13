import unittest

from genesis.day0_cat_d20_arrival_state import (
    BartenderSuggestsInvitingBouncerEvent,
    CatD20ArrivesDuringJudgeDiscussionEvent,
    CatD20DiscussionArrivalResult,
    CatD20ScratchedEvent,
    CatD20SocialState,
    CatD20WelcomeEventState,
    CatD20WelcomeResultState,
    TwoJudgePanelAcceptedEvent,
)
from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarWagerDecisionMethod,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0CatD20ArrivalObjectStateTests(
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

    def test_cat_d20_arrival_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_cat_d20_arrival()
        )

        arrival = result[
            "cat_d20"
        ]

        self.assertIsInstance(
            arrival,
            CatD20DiscussionArrivalResult,
        )

        self.assertIsInstance(
            arrival.arrival,
            CatD20WelcomeResultState,
        )

        self.assertIsInstance(
            arrival.arrival.event,
            CatD20WelcomeEventState,
        )

        self.assertIsInstance(
            arrival.event,
            CatD20ArrivesDuringJudgeDiscussionEvent,
        )

        self.assertIs(
            arrival.cat,
            scene.cat_d20,
        )

        self.assertIs(
            arrival.arrival.cat,
            arrival.cat,
        )

        self.assertEqual(
            arrival.arrival.name,
            "cat_d20_arrival_completed",
        )

        self.assertTrue(
            arrival.arrival.created
        )

        self._assert_object_only(
            arrival,
            "cat",
        )

        self._assert_object_only(
            arrival.arrival,
            "name",
        )

        self._assert_object_only(
            arrival.event,
            "cat",
        )

    def test_second_arrival_preserves_cat_identity(
        self
    ):
        scene = self._scene()

        first = (
            scene.advance_to_cat_d20_arrival()
            ["cat_d20"]
        )

        second = (
            scene
            .cat_d20_arrives_during_judge_discussion()
        )

        self.assertIs(
            second.cat,
            first.cat,
        )

        self.assertFalse(
            second.arrival.created
        )

        self.assertEqual(
            second.arrival.name,
            "cat_d20_already_present",
        )

        self._assert_object_only(
            second,
            "arrival",
        )

    def test_panel_acceptance_is_object_state(
        self
    ):
        scene = self._scene()

        scene.advance_to_cat_d20_arrival()

        event = (
            scene
            .wager_participants_accept_two_judge_panel()
        )

        wager = (
            scene.serpent_lilith_drink_wager
        )

        self.assertIsInstance(
            event,
            TwoJudgePanelAcceptedEvent,
        )

        self.assertEqual(
            event.accepted_by,
            (
                "lilith",
                "god",
                "serpent",
            ),
        )

        self.assertEqual(
            event.judges,
            (
                "bartender",
                "bouncer",
            ),
        )

        self.assertTrue(
            wager.tasting_panel_proposal.accepted
        )

        self.assertIsInstance(
            wager.decision_method,
            BarWagerDecisionMethod,
        )

        self.assertEqual(
            wager.decision_method.type,
            "tasting_panel",
        )

        self._assert_object_only(
            event,
            "accepted_by",
        )

    def test_bouncer_invitation_is_object_state(
        self
    ):
        scene = self._scene()

        scene.advance_to_cat_d20_arrival()
        scene.wager_participants_accept_two_judge_panel()

        event = (
            scene
            .bartender_suggests_inviting_bouncer_inside()
        )

        self.assertIsInstance(
            event,
            BartenderSuggestsInvitingBouncerEvent,
        )

        self.assertEqual(
            event.invite,
            "bouncer",
        )

        self.assertEqual(
            event.purpose,
            "agree_on_wager_judging",
        )

        self.assertFalse(
            event.bouncer_entered
        )

        self._assert_object_only(
            event,
            "invite",
        )

    def test_cat_d20_scratches_and_social_state_are_objects(
        self
    ):
        scene = self._scene()

        scene.advance_to_cat_d20_arrival()

        events = (
            scene.everyone_scratches_cat_d20()
        )

        self.assertIsInstance(
            events,
            tuple,
        )

        self.assertEqual(
            tuple(
                event.scratched_by
                for event in events
            ),
            (
                "serpent",
                "lilith",
                "god",
                "bartender",
            ),
        )

        for event in events:
            self.assertIsInstance(
                event,
                CatD20ScratchedEvent,
            )

            self._assert_object_only(
                event,
                "scratched_by",
            )

        social_state = (
            scene.cat_d20.social_state
        )

        self.assertIsInstance(
            social_state,
            CatD20SocialState,
        )

        self.assertEqual(
            social_state.scratched_by,
            (
                "serpent",
                "lilith",
                "god",
                "bartender",
            ),
        )

        self._assert_object_only(
            social_state,
            "scratched_by",
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        scene = self._scene()

        scene.advance_to_garfield_arrival()

        arrival = next(
            event
            for event in scene.history
            if (
                isinstance(
                    event,
                    dict,
                )
                and event["name"]
                == (
                    "cat_d20_arrives_during_"
                    "judge_discussion"
                )
            )
        )

        accepted = next(
            event
            for event in scene.history
            if (
                isinstance(
                    event,
                    dict,
                )
                and event["name"]
                == (
                    "wager_participants_accept_"
                    "two_judge_panel"
                )
            )
        )

        scratch = next(
            event
            for event in scene.history
            if (
                isinstance(
                    event,
                    dict,
                )
                and event["name"]
                == "cat_d20_scratched"
            )
        )

        self.assertEqual(
            arrival["cat"],
            "cat_d20",
        )

        self.assertEqual(
            accepted["judges"],
            [
                "bartender",
                "bouncer",
            ],
        )

        self.assertEqual(
            scratch["scratched_by"],
            "serpent",
        )


if __name__ == "__main__":
    unittest.main()
