import unittest

from genesis.day0_bartender_bouncer_panel_state import (
    BartenderProposesBouncerPanelEvent,
    LilithExplainsWagerToBartenderEvent,
    SerpentObjectsSingleJudgeEvent,
    WagerExplanationState,
)
from genesis.day0_bartender_judge_and_water_state import (
    WagerDecisionMethodSnapshot,
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


class Day0BartenderBouncerPanelObjectStateTests(
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

    def test_lilith_explanation_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bartender_bouncer_panel_proposal()
        )

        event = result[
            "explanation"
        ]

        self.assertIsInstance(
            event,
            LilithExplainsWagerToBartenderEvent,
        )

        self.assertIsInstance(
            event.wager,
            WagerExplanationState,
        )

        self.assertIsInstance(
            event.proposal,
            WagerDecisionMethodSnapshot,
        )

        self.assertEqual(
            event.wager.participants,
            (
                "serpent",
                "lilith",
                "god",
            ),
        )

        self.assertEqual(
            event.wager.contest,
            (
                "wine",
                "mead",
                "beer",
            ),
        )

        self.assertEqual(
            event.proposal.judge,
            "bartender",
        )

        self._assert_object_only(
            event,
            "wager",
        )

        self._assert_object_only(
            event.wager,
            "participants",
        )

        self._assert_object_only(
            event.proposal,
            "judge",
        )

    def test_serpent_objection_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bartender_bouncer_panel_proposal()
        )

        event = result[
            "objection"
        ]

        self.assertIsInstance(
            event,
            SerpentObjectsSingleJudgeEvent,
        )

        self.assertEqual(
            event.single_judge,
            "bartender",
        )

        self.assertEqual(
            event.objection,
            "one_judge_is_not_enough",
        )

        self._assert_object_only(
            event,
            "objection",
        )

    def test_panel_event_uses_detached_snapshot(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bartender_bouncer_panel_proposal()
        )

        event = result[
            "panel"
        ]

        proposal = (
            scene
            .serpent_lilith_drink_wager
            .tasting_panel_proposal
        )

        self.assertIsInstance(
            event,
            BartenderProposesBouncerPanelEvent,
        )

        self.assertIsInstance(
            event.proposal,
            WagerDecisionMethodSnapshot,
        )

        self.assertIsInstance(
            proposal,
            BarWagerDecisionMethod,
        )

        self.assertIsNot(
            event.proposal,
            proposal,
        )

        self.assertEqual(
            event.proposal.type,
            "tasting_panel",
        )

        self.assertEqual(
            event.proposal.judges,
            (
                "bartender",
                "bouncer",
            ),
        )

        self.assertFalse(
            event.proposal.accepted
        )

        self.assertFalse(
            proposal.accepted
        )

        self._assert_object_only(
            event,
            "proposal",
        )

        self._assert_object_only(
            event.proposal,
            "judges",
        )

        self._assert_object_only(
            proposal,
            "judges",
        )

    def test_panel_snapshot_is_detached_from_later_acceptance(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bartender_bouncer_panel_proposal()
        )

        event = result[
            "panel"
        ]

        proposal = (
            scene
            .serpent_lilith_drink_wager
            .tasting_panel_proposal
        )

        proposal.accept(
            participants=[
                "serpent",
                "lilith",
                "god",
            ]
        )

        self.assertTrue(
            proposal.accepted
        )

        self.assertFalse(
            event.proposal.accepted
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        scene = self._scene()

        scene.advance_to_bartender_bouncer_panel_proposal()

        explanation = next(
            event
            for event in scene.history
            if event["name"]
            == (
                "lilith_explains_wager_and_"
                "bartender_judge_proposal"
            )
        )

        panel = next(
            event
            for event in scene.history
            if event["name"]
            == (
                "bartender_proposes_bouncer_"
                "as_second_taster"
            )
        )

        self.assertIsInstance(
            explanation["wager"],
            dict,
        )

        self.assertIsInstance(
            explanation["proposal"],
            dict,
        )

        self.assertEqual(
            explanation["proposal"]["judge"],
            "bartender",
        )

        self.assertIsInstance(
            panel["proposal"],
            dict,
        )

        self.assertEqual(
            panel["proposal"]["judges"],
            [
                "bartender",
                "bouncer",
            ],
        )


if __name__ == "__main__":
    unittest.main()
