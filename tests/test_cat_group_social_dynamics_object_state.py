import unittest

from cats.cat_group_bonding_state import (
    CatGroupBondEvaluation,
    CatGroupBondReinforcedEvent,
    CatGroupBondReinforcedResult,
)
from cats.cat_group_bonding_system import (
    CatGroupBondingSystem,
)
from cats.cat_group_conflict_state import (
    CatGroupConflictEvent,
    CatGroupEncounterPeacefulResult,
)
from cats.cat_group_conflict_system import (
    CatGroupConflictSystem,
)
from cats.cat_group_hierarchy_state import (
    CatGroupInfluenceRankedEvent,
    CatGroupInfluenceRankEntry,
    CatGroupInfluenceRankingResult,
)
from cats.cat_group_hierarchy_system import (
    CatGroupHierarchySystem,
)
from cats.cat_group_lifecycle_state import (
    CatGroupDissolvedEvent,
    CatGroupLifecycleAdvancedEvent,
    CatGroupLifecycleState,
)
from cats.cat_group_lifecycle_system import (
    CatGroupLifecycleSystem,
)
from cats.cat_group_memory_state import (
    CatGroupBetrayalEvent,
    CatGroupCooperationEvent,
    CatGroupEncounterRememberedResult,
    CatGroupMemoryEventKind,
    CatGroupMemorySignal,
)
from cats.cat_group_memory_system import (
    CatGroupMemorySystem,
)
from cats.cat_group_recruitment_state import (
    CatGroupRecruitmentCompletedResult,
    CatGroupRecruitmentFailedResult,
    CatGroupRecruitmentVote,
    CatGroupRecruitmentVoteEvent,
)
from cats.cat_group_recruitment_system import (
    CatGroupRecruitmentSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_social_objects import (
    CatRelationship,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupSocialDynamicsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short",
        )

        self.second = self.cats.create_cat(
            name="second",
            color="white",
            fur_length="short",
        )

        self.third = self.cats.create_cat(
            name="third",
            color="gray",
            fur_length="short",
        )

        self.candidate = self.cats.create_cat(
            name="candidate",
            color="orange",
            fur_length="short",
        )

        self.other = self.cats.create_cat(
            name="other",
            color="black",
            fur_length="long",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                self.first,
                name="first_group",
            ).group_id
        )

        self.groups.add_member(
            self.first_group,
            self.second,
            self.cats.cats,
        )

        self.groups.add_member(
            self.first_group,
            self.third,
            self.cats.cats,
        )

        self.second_group = (
            self.groups.create_group(
                self.other,
                name="second_group",
            ).group_id
        )

    def assert_not_mapping(
        self,
        value,
        key,
    ):
        for method_name in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    method_name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                key
            ]

    def test_hierarchy_returns_object_ranking(
        self
    ):
        hierarchy = (
            CatGroupHierarchySystem(
                self.groups
            )
        )

        result = hierarchy.rank(
            self.first_group,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupInfluenceRankingResult,
        )

        self.assertIsInstance(
            result.ranking,
            tuple,
        )

        self.assertTrue(
            all(
                isinstance(
                    entry,
                    CatGroupInfluenceRankEntry,
                )
                for entry
                in result.ranking
            )
        )

        self.assert_not_mapping(
            result,
            "ranking",
        )

        self.assert_not_mapping(
            result.ranking[0],
            "cat",
        )

    def test_hierarchy_history_stores_object_event(
        self
    ):
        hierarchy = (
            CatGroupHierarchySystem(
                self.groups
            )
        )

        hierarchy.rank(
            self.first_group,
            self.cats.cats,
        )

        stored = (
            self.groups.groups[
                self.first_group
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupInfluenceRankedEvent,
        )

    def test_bond_evaluation_is_object(
        self
    ):
        bonding = (
            CatGroupBondingSystem(
                self.groups
            )
        )

        result = bonding.evaluate(
            self.first_group,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupBondEvaluation,
        )

        self.assertEqual(
            result.member_count,
            3,
        )

        self.assert_not_mapping(
            result,
            "cohesion",
        )

    def test_bond_reinforcement_uses_object_event_and_result(
        self
    ):
        bonding = (
            CatGroupBondingSystem(
                self.groups
            )
        )

        result = bonding.reinforce(
            self.first_group,
            self.cats.cats,
            amount=0.1,
        )

        self.assertIsInstance(
            result,
            CatGroupBondReinforcedResult,
        )

        stored = (
            self.groups.groups[
                self.first_group
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupBondReinforcedEvent,
        )

        self.assertIsInstance(
            stored.members,
            tuple,
        )

        self.assert_not_mapping(
            result,
            "cohesion",
        )

    def test_recruitment_vote_is_nested_object_graph(
        self
    ):
        recruitment = (
            CatGroupRecruitmentSystem(
                self.groups
            )
        )

        vote = recruitment.vote(
            self.first_group,
            self.candidate,
            self.cats.cats,
            sponsor=self.first,
        )

        self.assertIsInstance(
            vote,
            CatGroupRecruitmentVoteEvent,
        )

        self.assertIsInstance(
            vote.votes,
            tuple,
        )

        self.assertTrue(
            all(
                isinstance(
                    item,
                    CatGroupRecruitmentVote,
                )
                for item
                in vote.votes
            )
        )

        self.assert_not_mapping(
            vote,
            "accepted",
        )

    def test_recruitment_completion_is_object(
        self
    ):
        recruitment = (
            CatGroupRecruitmentSystem(
                self.groups
            )
        )

        result = recruitment.recruit(
            self.first_group,
            self.candidate,
            self.cats.cats,
            sponsor=self.first,
        )

        self.assertIsInstance(
            result,
            CatGroupRecruitmentCompletedResult,
        )

        self.assertTrue(
            result.joined
        )

        self.assertTrue(
            result.join_result.joined
        )

        self.assert_not_mapping(
            result,
            "joined",
        )

    def test_recruitment_veto_returns_failure_object(
        self
    ):
        relation = (
            CatRelationship.create()
        )

        relation.trust = 0.0
        relation.tension = 1.0
        relation.familiarity = 0.8

        self.second.relationships[
            self.candidate.name
        ] = relation

        recruitment = (
            CatGroupRecruitmentSystem(
                self.groups
            )
        )

        result = recruitment.recruit(
            self.first_group,
            self.candidate,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupRecruitmentFailedResult,
        )

        self.assertFalse(
            result.joined
        )

        self.assertIn(
            self.second.name,
            result.vote.vetoes,
        )

    def test_peaceful_encounter_is_object(
        self
    ):
        first = self.groups.groups[
            self.first_group
        ]

        second = self.groups.groups[
            self.second_group
        ]

        first.current_layer = "meeting_place"
        first.current_location = "window"

        second.current_layer = "meeting_place"
        second.current_location = "back_room"

        conflict = (
            CatGroupConflictSystem(
                self.groups
            )
        )

        result = conflict.encounter(
            self.first_group,
            self.second_group,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupEncounterPeacefulResult,
        )

        self.assertFalse(
            result.conflict
        )

        self.assert_not_mapping(
            result,
            "conflict",
        )

    def test_conflict_is_object_and_updates_memory(
        self
    ):
        conflict = (
            CatGroupConflictSystem(
                self.groups
            )
        )

        result = conflict.resolve(
            self.first_group,
            self.second_group,
            self.cats.cats,
            resource="milk",
        )

        self.assertIsInstance(
            result,
            CatGroupConflictEvent,
        )

        self.assertTrue(
            result.conflict
        )

        self.assertIsInstance(
            result.shared_territories,
            tuple,
        )

        first_memory = (
            CatGroupMemorySystem(
                self.groups
            ).relation_memory(
                self.first_group,
                self.second_group,
            )
        )

        self.assertEqual(
            first_memory.conflicts,
            1,
        )

        self.assert_not_mapping(
            result,
            "winner",
        )

    def test_cooperation_memory_event_is_object(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        result = memory.record_cooperation(
            self.first_group,
            self.second_group,
            "shared_hunt",
        )

        self.assertIsInstance(
            result,
            CatGroupCooperationEvent,
        )

        self.assertTrue(
            result.cooperation
        )

        snapshot = memory.relation_memory(
            self.first_group,
            self.second_group,
        )

        self.assertEqual(
            snapshot.cooperations,
            1,
        )

        self.assert_not_mapping(
            result,
            "cooperation",
        )

    def test_direct_memory_signal_returns_object_result(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        result = memory.remember_encounter(
            self.first_group,
            self.second_group,
            CatGroupMemorySignal(
                kind=(
                    CatGroupMemoryEventKind
                    .CONFLICT
                ),
                winner=self.first_group,
                loser=self.second_group,
            ),
        )

        self.assertIsInstance(
            result,
            CatGroupEncounterRememberedResult,
        )

        self.assertTrue(
            result.remembered
        )

        self.assert_not_mapping(
            result,
            "remembered",
        )

    def test_betrayal_memory_event_is_object(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        result = memory.record_betrayal(
            self.first_group,
            self.second_group,
            "territory_seized",
        )

        self.assertIsInstance(
            result,
            CatGroupBetrayalEvent,
        )

        self.assertTrue(
            result.betrayal
        )

        snapshot = memory.relation_memory(
            self.second_group,
            self.first_group,
        )

        self.assertEqual(
            snapshot.betrayals,
            1,
        )

    def test_lifecycle_advance_is_object_event(
        self
    ):
        lifecycle = (
            CatGroupLifecycleSystem(
                self.groups
            )
        )

        result = lifecycle.advance(
            self.first_group,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupLifecycleAdvancedEvent,
        )

        self.assertIsInstance(
            result.state,
            CatGroupLifecycleState,
        )

        self.assert_not_mapping(
            result,
            "state",
        )

    def test_lifecycle_dissolve_is_object_event(
        self
    ):
        lifecycle = (
            CatGroupLifecycleSystem(
                self.groups
            )
        )

        result = lifecycle.dissolve(
            self.first_group,
            self.cats.cats,
            reason="test_dissolve",
        )

        self.assertIsInstance(
            result,
            CatGroupDissolvedEvent,
        )

        self.assertTrue(
            result.dissolved
        )

        self.assertIs(
            self.groups.groups[
                self.first_group
            ].state,
            CatGroupLifecycleState.DISSOLVED,
        )

        self.assert_not_mapping(
            result,
            "dissolved",
        )


if __name__ == "__main__":
    unittest.main()
