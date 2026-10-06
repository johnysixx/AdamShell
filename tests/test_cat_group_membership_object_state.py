import unittest

from cats.cat_group_membership_state import (
    CatGroupCandidateEvaluation,
    CatGroupJoinDeniedResult,
    CatGroupJoinSkippedResult,
    CatJoinedGroupEvent,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_social_objects import (
    CatRelationship,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupMembershipObjectStateTests(
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

        self.groups = CatGroupSystem(
            self.cats
        )

        created = self.groups.create_group(
            self.first,
            name="bar_cats",
        )

        self.group_id = (
            created.group_id
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

    def test_candidate_evaluation_returns_object(
        self
    ):
        result = (
            self.groups
            .evaluate_candidate(
                self.group_id,
                self.second,
                self.cats.cats,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupCandidateEvaluation,
        )

        self.assertTrue(
            result.accepted
        )

        self.assertEqual(
            result.reason,
            "socially_accepted",
        )

        self.assertEqual(
            result.member_count,
            1,
        )

        self.assert_not_mapping(
            result,
            "accepted",
        )

    def test_hostile_candidate_evaluation_is_object(
        self
    ):
        relation = CatRelationship.create()

        relation.familiarity = 0.5
        relation.trust = 0.1
        relation.affiliation = 0.0
        relation.tension = 0.9

        self.first.relationships[
            self.second.name
        ] = relation

        result = (
            self.groups
            .evaluate_candidate(
                self.group_id,
                self.second,
                self.cats.cats,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupCandidateEvaluation,
        )

        self.assertFalse(
            result.accepted
        )

        self.assertEqual(
            result.reason,
            "group_social_rejection",
        )

        self.assertEqual(
            result.hostile_members,
            1,
        )

        self.assert_not_mapping(
            result,
            "reason",
        )

    def test_rejected_join_returns_object(
        self
    ):
        relation = CatRelationship.create()

        relation.trust = 0.0
        relation.tension = 1.0

        self.first.relationships[
            self.second.name
        ] = relation

        result = self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupJoinDeniedResult,
        )

        self.assertFalse(
            result.joined
        )

        self.assertEqual(
            result.reason,
            "group_social_rejection",
        )

        self.assertFalse(
            self.second.group.member
        )

        self.assert_not_mapping(
            result,
            "joined",
        )

    def test_existing_member_returns_skipped_object(
        self
    ):
        result = self.groups.add_member(
            self.group_id,
            self.first,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupJoinSkippedResult,
        )

        self.assertFalse(
            result.joined
        )

        self.assertEqual(
            result.reason,
            "already_member",
        )

        self.assert_not_mapping(
            result,
            "joined",
        )

    def test_successful_join_returns_event_object(
        self
    ):
        result = self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatJoinedGroupEvent,
        )

        self.assertTrue(
            result.joined
        )

        self.assertEqual(
            result.cat,
            self.second.name,
        )

        self.assertEqual(
            result.member_count,
            2,
        )

        self.assertTrue(
            self.second.group.member
        )

        self.assert_not_mapping(
            result,
            "joined",
        )

    def test_group_history_stores_detached_join_event(
        self
    ):
        result = self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        stored = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatJoinedGroupEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_not_mapping(
            stored,
            "joined",
        )

    def test_cat_social_history_stores_join_event_object(
        self
    ):
        result = self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        stored = (
            self.second
            .social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatJoinedGroupEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_not_mapping(
            stored,
            "joined",
        )

    def test_membership_results_are_frozen(
        self
    ):
        evaluation = (
            self.groups
            .evaluate_candidate(
                self.group_id,
                self.second,
                self.cats.cats,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            evaluation.score = 0.0

        joined = self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        with self.assertRaises(
            AttributeError
        ):
            joined.cat = "changed"


if __name__ == "__main__":
    unittest.main()
