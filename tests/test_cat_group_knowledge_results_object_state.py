import unittest

from cats.cat_group_knowledge_contribution_state import (
    CatGroupKnowledgeContributedEvent,
    CatGroupKnowledgeContributionDeniedResult,
)
from cats.cat_group_knowledge_propagation_state import (
    CatGroupKnowledgePropagatedResult,
    CatGroupKnowledgePropagationDeniedResult,
)
from cats.cat_group_knowledge_sharing_state import (
    CatGroupKnowledgeSharedResult,
    CatGroupKnowledgeShareDeniedResult,
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
)
from cats.cat_group_knowledge_transmission_state import (
    CatGroupKnowledgeTransmittedEvent,
    CatGroupKnowledgeTransmissionDeniedResult,
)
from cats.cat_group_knowledge_verification_state import (
    CatGroupKnowledgeVerificationDeniedResult,
    CatGroupKnowledgeVerifiedEvent,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_social_objects import (
    CatGroupKnowledgeRecord,
    CatGroupKnowledgeTransmission,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupKnowledgeResultsObjectStateTests(
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

        self.outsider = (
            self.cats.create_cat(
                name="outsider",
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

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

    def contribute(
        self,
        confidence=1.0,
        verified=True,
    ):
        return (
            self.knowledge.contribute(
                self.first_group,
                self.first,
                knowledge_id="safe_route",
                content={
                    "route":
                        "bar_to_library",
                },
                category="navigation",
                confidence=confidence,
                verified=verified,
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

    def test_non_member_contribution_returns_denied_object(
        self
    ):
        group = (
            self.groups.groups[
                self.first_group
            ]
        )

        history_before = len(
            group.history
        )

        result = (
            self.knowledge.contribute(
                self.first_group,
                self.outsider,
                "secret",
                {
                    "value": 1
                },
                "test",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgeContributionDeniedResult,
        )

        self.assertFalse(
            result.contributed
        )

        self.assertEqual(
            result.reason,
            "cat_not_group_member",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assertNotIn(
            "secret",
            group.knowledge,
        )

        self.assertEqual(
            len(
                group.history
            ),
            history_before,
        )

        self.assert_not_mapping(
            result
        )

    def test_contribution_returns_typed_event_and_record(
        self
    ):
        result = (
            self.contribute(
                confidence=0.8,
                verified=True,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgeContributedEvent,
        )

        self.assertTrue(
            result.contributed
        )

        self.assertEqual(
            result.knowledge_id,
            "safe_route",
        )

        self.assertAlmostEqual(
            result.confidence,
            0.8,
        )

        group = (
            self.groups.groups[
                self.first_group
            ]
        )

        record = (
            group.knowledge[
                "safe_route"
            ]
        )

        self.assertIsInstance(
            record,
            CatGroupKnowledgeRecord,
        )

        self.assertEqual(
            record.origin_cat,
            self.first.name,
        )

        self.assertIsInstance(
            record.transmission_path[
                0
            ],
            CatGroupKnowledgeTransmission,
        )

        self.assert_not_mapping(
            result
        )

    def test_contribution_history_is_detached_boundary(
        self
    ):
        group = (
            self.groups.groups[
                self.first_group
            ]
        )

        result = (
            self.contribute()
        )

        stored = (
            group.history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            dict,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assertEqual(
            stored,
            result.to_dict(),
        )

        stored[
            "knowledge_id"
        ] = "changed"

        self.assertEqual(
            result.knowledge_id,
            "safe_route",
        )

    def test_unknown_share_returns_denied_object(
        self
    ):
        result = (
            self.knowledge
            .share_with_group_members(
                self.first_group,
                self.cats.cats,
                "missing",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgeShareDeniedResult,
        )

        self.assertFalse(
            result.shared
        )

        self.assertEqual(
            result.reason,
            "unknown_knowledge",
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

    def test_share_returns_typed_result_with_tuple_receivers(
        self
    ):
        self.groups.add_member(
            self.first_group,
            self.outsider,
            self.cats.cats,
        )

        self.contribute()

        result = (
            self.knowledge
            .share_with_group_members(
                self.first_group,
                self.cats.cats,
                "safe_route",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgeSharedResult,
        )

        self.assertTrue(
            result.shared
        )

        self.assertIsInstance(
            result.receivers,
            tuple,
        )

        self.assertIn(
            self.first.name,
            result.receivers,
        )

        self.assertIn(
            self.outsider.name,
            result.receivers,
        )

        received = (
            self.outsider.knowledge
            .group_received_knowledge[
                "safe_route"
            ]
        )

        self.assertFalse(
            received.verified
        )

        self.assertEqual(
            received.received_via,
            "own_group",
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

    def test_missing_transmission_returns_denied_object(
        self
    ):
        result = (
            self.knowledge
            .transmit_between_groups(
                self.first_group,
                self.second_group,
                "missing",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgeTransmissionDeniedResult,
        )

        self.assertFalse(
            result.transmitted
        )

        self.assertEqual(
            result.reason,
            "source_does_not_know",
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

    def test_transmission_returns_event_and_object_path(
        self
    ):
        self.contribute()

        result = (
            self.knowledge
            .transmit_between_groups(
                self.first_group,
                self.second_group,
                "safe_route",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgeTransmittedEvent,
        )

        self.assertTrue(
            result.transmitted
        )

        self.assertEqual(
            result.source_group,
            self.first_group,
        )

        self.assertEqual(
            result.target_group,
            self.second_group,
        )

        self.assertAlmostEqual(
            result.confidence,
            0.88,
        )

        record = (
            self.groups.groups[
                self.second_group
            ].knowledge[
                "safe_route"
            ]
        )

        self.assertFalse(
            record.verified
        )

        transmission = (
            record.transmission_path[
                -1
            ]
        )

        self.assertIsInstance(
            transmission,
            CatGroupKnowledgeTransmission,
        )

        self.assertEqual(
            transmission.source_group,
            self.first_group,
        )

        self.assertEqual(
            transmission.target_group,
            self.second_group,
        )

        self.assert_not_mapping(
            result
        )

    def test_transmission_histories_are_separate_snapshots(
        self
    ):
        self.contribute()

        source = (
            self.groups.groups[
                self.first_group
            ]
        )

        target = (
            self.groups.groups[
                self.second_group
            ]
        )

        result = (
            self.knowledge
            .transmit_between_groups(
                self.first_group,
                self.second_group,
                "safe_route",
            )
        )

        source_event = (
            source.history[
                -1
            ]
        )

        target_event = (
            target.history[
                -1
            ]
        )

        self.assertEqual(
            source_event,
            result.to_dict(),
        )

        self.assertEqual(
            target_event,
            result.to_dict(),
        )

        self.assertIsNot(
            source_event,
            target_event,
        )

        source_event[
            "knowledge_id"
        ] = "changed"

        self.assertEqual(
            target_event[
                "knowledge_id"
            ],
            "safe_route",
        )

        self.assertEqual(
            result.knowledge_id,
            "safe_route",
        )

    def test_unknown_propagation_returns_denied_object(
        self
    ):
        result = (
            self.knowledge
            .propagate_to_members(
                self.first_group,
                self.cats.cats,
                "missing",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgePropagationDeniedResult,
        )

        self.assertFalse(
            result.propagated
        )

        self.assertEqual(
            result.reason,
            "unknown_knowledge",
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

    def test_propagation_returns_typed_result(
        self
    ):
        self.groups.add_member(
            self.first_group,
            self.outsider,
            self.cats.cats,
        )

        self.contribute()

        result = (
            self.knowledge
            .propagate_to_members(
                self.first_group,
                self.cats.cats,
                "safe_route",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgePropagatedResult,
        )

        self.assertTrue(
            result.propagated
        )

        self.assertIsInstance(
            result.receivers,
            tuple,
        )

        self.assertIn(
            self.outsider.name,
            result.receivers,
        )

        received = (
            self.outsider.knowledge
            .group_received_knowledge[
                "safe_route"
            ]
        )

        self.assertEqual(
            received.received_via,
            "group_propagation",
        )

        self.assertFalse(
            received.verified
        )

        self.assert_not_mapping(
            result
        )

    def test_unknown_verification_returns_denied_object(
        self
    ):
        result = (
            self.knowledge.verify(
                self.first_group,
                self.first,
                "missing",
                confirmed=True,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgeVerificationDeniedResult,
        )

        self.assertFalse(
            result.verified
        )

        self.assertEqual(
            result.reason,
            "unknown_knowledge",
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

    def test_confirmed_verification_returns_typed_event(
        self
    ):
        self.contribute(
            confidence=0.5,
            verified=False,
        )

        result = (
            self.knowledge.verify(
                self.first_group,
                self.first,
                "safe_route",
                confirmed=True,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgeVerifiedEvent,
        )

        self.assertEqual(
            result.outcome,
            "confirmed",
        )

        self.assertAlmostEqual(
            result.confidence,
            0.62,
        )

        record = (
            self.groups.groups[
                self.first_group
            ].knowledge[
                "safe_route"
            ]
        )

        self.assertTrue(
            record.verified
        )

        self.assertEqual(
            record.verification_count,
            1,
        )

        self.assert_not_mapping(
            result
        )

    def test_contradiction_returns_event_and_updates_record(
        self
    ):
        self.contribute(
            confidence=0.5,
            verified=True,
        )

        result = (
            self.knowledge.verify(
                self.first_group,
                self.first,
                "safe_route",
                confirmed=False,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupKnowledgeVerifiedEvent,
        )

        self.assertEqual(
            result.outcome,
            "contradicted",
        )

        self.assertAlmostEqual(
            result.confidence,
            0.25,
        )

        record = (
            self.groups.groups[
                self.first_group
            ].knowledge[
                "safe_route"
            ]
        )

        self.assertEqual(
            record.contradiction_count,
            1,
        )

        self.assertFalse(
            record.verified
        )

    def test_verification_history_is_detached_boundary(
        self
    ):
        self.contribute(
            confidence=0.5,
            verified=False,
        )

        group = (
            self.groups.groups[
                self.first_group
            ]
        )

        result = (
            self.knowledge.verify(
                self.first_group,
                self.first,
                "safe_route",
                confirmed=True,
            )
        )

        stored = (
            group.history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            dict,
        )

        self.assertEqual(
            stored,
            result.to_dict(),
        )

        stored[
            "outcome"
        ] = "changed"

        self.assertEqual(
            result.outcome,
            "confirmed",
        )

    def test_results_are_immutable(
        self
    ):
        denied_contribution = (
            self.knowledge.contribute(
                self.first_group,
                self.outsider,
                "missing",
                {},
                "test",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_contribution.reason = (
                "changed"
            )

        denied_share = (
            self.knowledge
            .share_with_group_members(
                self.first_group,
                self.cats.cats,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_share.reason = "changed"

        denied_transmission = (
            self.knowledge
            .transmit_between_groups(
                self.first_group,
                self.second_group,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_transmission.reason = (
                "changed"
            )

        denied_propagation = (
            self.knowledge
            .propagate_to_members(
                self.first_group,
                self.cats.cats,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_propagation.reason = (
                "changed"
            )

        denied_verification = (
            self.knowledge.verify(
                self.first_group,
                self.first,
                "missing",
                confirmed=True,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_verification.reason = (
                "changed"
            )

        contributed = (
            self.contribute()
        )

        with self.assertRaises(
            AttributeError
        ):
            contributed.knowledge_id = (
                "changed"
            )

        shared = (
            self.knowledge
            .share_with_group_members(
                self.first_group,
                self.cats.cats,
                "safe_route",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            shared.receivers = ()

        transmitted = (
            self.knowledge
            .transmit_between_groups(
                self.first_group,
                self.second_group,
                "safe_route",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            transmitted.confidence = 0.0

        propagated = (
            self.knowledge
            .propagate_to_members(
                self.first_group,
                self.cats.cats,
                "safe_route",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            propagated.receivers = ()

        verified = (
            self.knowledge.verify(
                self.first_group,
                self.first,
                "safe_route",
                confirmed=True,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            verified.outcome = "changed"


if __name__ == "__main__":
    unittest.main()
