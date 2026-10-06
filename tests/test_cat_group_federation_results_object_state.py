import unittest

from cats.cat_federation import (
    CatFederation,
)
from cats.cat_group_federation_admission_state import (
    CatFederationAdmissionDeniedResult,
    CatFederationAdmissionSkippedResult,
    CatGroupJoinedFederationEvent,
)
from cats.cat_group_federation_creation_state import (
    CatFederationCreatedResult,
)
from cats.cat_group_federation_knowledge_state import (
    CatFederationKnowledgeDeniedResult,
    CatFederationKnowledgeSharedResult,
)
from cats.cat_group_federation_leave_state import (
    CatFederationLeaveDeniedResult,
    CatGroupLeftFederationResult,
)
from cats.cat_group_federation_system import (
    CatGroupFederationSystem,
)
from cats.cat_group_diplomacy_state import (
    CatGroupDiplomacyState,
    CatGroupMutualRelationResult,
)
from cats.cat_group_memory_state import (
    CatGroupMemoryState,
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


def _mutual_relation_result(
    first_group_id,
    second_group_id,
    mutual_score,
):
    return CatGroupMutualRelationResult(
        first=CatGroupDiplomacyState(
            group_id=first_group_id,
            other_group_id=second_group_id,
            score=mutual_score,
            status="neutral",
            memory=CatGroupMemoryState(),
        ),
        second=CatGroupDiplomacyState(
            group_id=second_group_id,
            other_group_id=first_group_id,
            score=mutual_score,
            status="neutral",
            memory=CatGroupMemoryState(),
        ),
        mutual_score=mutual_score,
    )


class CatGroupFederationResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = (
            self.cats.create_cat(
                name="first",
                color="black",
                fur_length="short",
            )
        )

        self.second = (
            self.cats.create_cat(
                name="second",
                color="white",
                fur_length="short",
            )
        )

        self.third = (
            self.cats.create_cat(
                name="third",
                color="gray",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        self.first_group = (
            self.groups.create_group(
                self.first,
                name="first_group",
            ).group_id
        )

        self.second_group = (
            self.groups.create_group(
                self.second,
                name="second_group",
            ).group_id
        )

        self.third_group = (
            self.groups.create_group(
                self.third,
                name="third_group",
            ).group_id
        )

        self.federations = (
            CatGroupFederationSystem(
                self.groups
            )
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

    def assert_not_mapping(
        self,
        result,
    ):
        for method_name in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    method_name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "name"
            ]

    def create_federation(
        self
    ):
        return (
            self.federations.create(
                self.first_group,
                name="knowledge_union",
            )
        )

    def test_create_returns_typed_result_and_domain_federation(
        self
    ):
        result = (
            self.create_federation()
        )

        self.assertIsInstance(
            result,
            CatFederationCreatedResult,
        )

        self.assertTrue(
            result.created
        )

        self.assertEqual(
            result.name,
            "cat_federation_created",
        )

        self.assertEqual(
            result.founder_group,
            self.first_group,
        )

        federation = (
            self.federations
            .federations[
                result.federation_id
            ]
        )

        self.assertIsInstance(
            federation,
            CatFederation,
        )

        self.assertEqual(
            federation.name,
            "knowledge_union",
        )

        self.assertEqual(
            federation.founder_group,
            self.first_group,
        )

        self.assertEqual(
            federation.groups,
            [
                self.first_group
            ],
        )

        self.assertIn(
            result.federation_id,
            self.groups.groups[
                self.first_group
            ].federations,
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assert_not_mapping(
            result
        )

    def test_existing_member_returns_skipped_object(
        self
    ):
        created = (
            self.create_federation()
        )

        federation = (
            self.federations
            .federations[
                created.federation_id
            ]
        )

        history_before = len(
            federation.history
        )

        result = (
            self.federations.admit(
                created.federation_id,
                self.first_group,
            )
        )

        self.assertIsInstance(
            result,
            CatFederationAdmissionSkippedResult,
        )

        self.assertFalse(
            result.admitted
        )

        self.assertEqual(
            result.name,
            "cat_federation_admission_skipped",
        )

        self.assertEqual(
            result.reason,
            "already_member",
        )

        self.assertEqual(
            federation.groups,
            [
                self.first_group
            ],
        )

        self.assertEqual(
            len(
                federation.history
            ),
            history_before,
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assert_not_mapping(
            result
        )

    def test_negative_diplomacy_returns_denied_object(
        self
    ):
        created = (
            self.create_federation()
        )

        self.federations.diplomacy.mutual_relation = (
            lambda first_group_id, second_group_id:
                _mutual_relation_result(
                    first_group_id,
                    second_group_id,
                    -0.5,
                )
        )

        result = (
            self.federations.admit(
                created.federation_id,
                self.second_group,
            )
        )

        self.assertIsInstance(
            result,
            CatFederationAdmissionDeniedResult,
        )

        self.assertFalse(
            result.admitted
        )

        self.assertEqual(
            result.reason,
            "negative_diplomacy",
        )

        self.assertAlmostEqual(
            result.score,
            -0.5,
        )

        federation = (
            self.federations
            .federations[
                created.federation_id
            ]
        )

        self.assertNotIn(
            self.second_group,
            federation.groups,
        )

        self.assertNotIn(
            created.federation_id,
            self.groups.groups[
                self.second_group
            ].federations,
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assert_not_mapping(
            result
        )

    def test_successful_admission_returns_event(
        self
    ):
        created = (
            self.create_federation()
        )

        result = (
            self.federations.admit(
                created.federation_id,
                self.second_group,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupJoinedFederationEvent,
        )

        self.assertTrue(
            result.admitted
        )

        self.assertEqual(
            result.federation_id,
            created.federation_id,
        )

        self.assertEqual(
            result.group_id,
            self.second_group,
        )

        federation = (
            self.federations
            .federations[
                created.federation_id
            ]
        )

        self.assertIn(
            self.second_group,
            federation.groups,
        )

        self.assertIn(
            created.federation_id,
            self.groups.groups[
                self.second_group
            ].federations,
        )

        self.assert_not_mapping(
            result
        )

    def test_admission_history_stores_immutable_event_object(
        self
    ):
        created = (
            self.create_federation()
        )

        result = (
            self.federations.admit(
                created.federation_id,
                self.second_group,
            )
        )

        federation = (
            self.federations
            .federations[
                created.federation_id
            ]
        )

        stored = (
            federation.history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupJoinedFederationEvent,
        )

        self.assertIs(
            stored,
            result,
        )

        self.assertEqual(
            stored.group_id,
            self.second_group,
        )

        with self.assertRaises(
            AttributeError
        ):
            stored.group_id = "changed"

        self.assertEqual(
            result.group_id,
            self.second_group,
        )

        self.assert_not_mapping(
            stored
        )

    def test_nonmember_source_returns_knowledge_denied_object(
        self
    ):
        created = (
            self.create_federation()
        )

        result = (
            self.federations.share_knowledge(
                created.federation_id,
                self.second_group,
                "safe_route",
            )
        )

        self.assertIsInstance(
            result,
            CatFederationKnowledgeDeniedResult,
        )

        self.assertFalse(
            result.shared
        )

        self.assertEqual(
            result.reason,
            "source_not_member",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assert_not_mapping(
            result
        )

    def test_share_knowledge_returns_typed_result_with_tuple_targets(
        self
    ):
        self.knowledge.contribute(
            self.first_group,
            self.first,
            "safe_route",
            {
                "route":
                    "bar_to_library",
            },
            "navigation",
            confidence=1.0,
        )

        created = (
            self.create_federation()
        )

        self.federations.admit(
            created.federation_id,
            self.second_group,
        )

        self.federations.admit(
            created.federation_id,
            self.third_group,
        )

        result = (
            self.federations.share_knowledge(
                created.federation_id,
                self.first_group,
                "safe_route",
            )
        )

        self.assertIsInstance(
            result,
            CatFederationKnowledgeSharedResult,
        )

        self.assertTrue(
            result.shared
        )

        self.assertIsInstance(
            result.targets,
            tuple,
        )

        self.assertEqual(
            result.targets,
            (
                self.second_group,
                self.third_group,
            ),
        )

        self.assertIn(
            "safe_route",
            self.groups.groups[
                self.second_group
            ].knowledge,
        )

        self.assertIn(
            "safe_route",
            self.groups.groups[
                self.third_group
            ].knowledge,
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assert_not_mapping(
            result
        )

    def test_missing_knowledge_preserves_empty_target_success(
        self
    ):
        created = (
            self.create_federation()
        )

        self.federations.admit(
            created.federation_id,
            self.second_group,
        )

        result = (
            self.federations.share_knowledge(
                created.federation_id,
                self.first_group,
                "missing",
            )
        )

        self.assertIsInstance(
            result,
            CatFederationKnowledgeSharedResult,
        )

        self.assertTrue(
            result.shared
        )

        self.assertEqual(
            result.targets,
            (),
        )

    def test_leave_nonmember_returns_denied_object(
        self
    ):
        created = (
            self.create_federation()
        )

        result = (
            self.federations.leave(
                created.federation_id,
                self.second_group,
            )
        )

        self.assertIsInstance(
            result,
            CatFederationLeaveDeniedResult,
        )

        self.assertFalse(
            result.left
        )

        self.assertEqual(
            result.reason,
            "not_member",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assert_not_mapping(
            result
        )

    def test_leave_returns_typed_result_and_updates_membership(
        self
    ):
        created = (
            self.create_federation()
        )

        self.federations.admit(
            created.federation_id,
            self.second_group,
        )

        result = (
            self.federations.leave(
                created.federation_id,
                self.second_group,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupLeftFederationResult,
        )

        self.assertTrue(
            result.left
        )

        federation = (
            self.federations
            .federations[
                created.federation_id
            ]
        )

        self.assertNotIn(
            self.second_group,
            federation.groups,
        )

        self.assertNotIn(
            created.federation_id,
            self.groups.groups[
                self.second_group
            ].federations,
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assert_not_mapping(
            result
        )

    def test_results_are_immutable(
        self
    ):
        created = (
            self.create_federation()
        )

        with self.assertRaises(
            AttributeError
        ):
            created.federation_id = (
                "changed"
            )

        skipped = (
            self.federations.admit(
                created.federation_id,
                self.first_group,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            skipped.reason = "changed"

        self.federations.diplomacy.mutual_relation = (
            lambda first_group_id, second_group_id:
                _mutual_relation_result(
                    first_group_id,
                    second_group_id,
                    -0.5,
                )
        )

        denied = (
            self.federations.admit(
                created.federation_id,
                self.second_group,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.score = 0.0

        self.federations.diplomacy.mutual_relation = (
            lambda first_group_id, second_group_id:
                _mutual_relation_result(
                    first_group_id,
                    second_group_id,
                    0.0,
                )
        )

        admitted = (
            self.federations.admit(
                created.federation_id,
                self.second_group,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            admitted.group_id = "changed"

        shared = (
            self.federations.share_knowledge(
                created.federation_id,
                self.first_group,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            shared.targets = ()

        left = (
            self.federations.leave(
                created.federation_id,
                self.second_group,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            left.group_id = "changed"


if __name__ == "__main__":
    unittest.main()
