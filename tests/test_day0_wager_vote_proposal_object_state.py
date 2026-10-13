import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_wager_vote_proposal_state import (
    GodAsksWhoDecidesWagerEvent,
    LilithProposesParticipantVoteEvent,
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


class Day0WagerVoteProposalObjectStateTests(
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

    def test_question_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_wager_vote_proposal()
        )

        event = result.question

        self.assertIsInstance(
            event,
            GodAsksWhoDecidesWagerEvent,
        )

        self.assertEqual(
            event.speaker,
            "god",
        )

        self.assertEqual(
            event.listener,
            "lilith",
        )

        self.assertEqual(
            event.question,
            "who_decides_winner",
        )

        self._assert_object_only(
            event,
            "question",
        )

    def test_vote_proposal_keeps_decision_method_object(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_wager_vote_proposal()
        )

        event = result.proposal

        method = (
            scene
            .serpent_lilith_drink_wager
            .decision_method_proposal
        )

        self.assertIsInstance(
            event,
            LilithProposesParticipantVoteEvent,
        )

        self.assertIsInstance(
            event.decision_method,
            BarWagerDecisionMethod,
        )

        self.assertIs(
            event.decision_method,
            method,
        )

        self.assertEqual(
            method.type,
            "participant_vote",
        )

        self.assertEqual(
            method.voters,
            [
                "serpent",
                "lilith",
                "god",
            ],
        )

        self.assertTrue(
            method.proposed
        )

        self.assertFalse(
            method.accepted
        )

        self._assert_object_only(
            event,
            "decision_method",
        )

        self._assert_object_only(
            method,
            "type",
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        scene = self._scene()

        scene.advance_to_wager_vote_proposal()

        question = next(
            event
            for event in scene.history
            if event["name"]
            == "god_asks_who_will_decide_wager"
        )

        proposal = next(
            event
            for event in scene.history
            if event["name"]
            == "lilith_proposes_participant_vote"
        )

        self.assertIsInstance(
            question,
            dict,
        )

        self.assertEqual(
            question["question"],
            "who_decides_winner",
        )

        self.assertIsInstance(
            proposal,
            dict,
        )

        self.assertIsInstance(
            proposal["decision_method"],
            dict,
        )

        self.assertEqual(
            proposal["decision_method"]["type"],
            "participant_vote",
        )

        self.assertEqual(
            proposal["decision_method"]["voters"],
            [
                "serpent",
                "lilith",
                "god",
            ],
        )


if __name__ == "__main__":
    unittest.main()
