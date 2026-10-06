import unittest

from cats.cat_group_innovation_creation_state import (
    CatGroupInnovationCreatedEvent,
    CatGroupInnovationCreationDeniedResult,
)
from cats.cat_group_innovation_system import (
    CatGroupInnovationSystem,
)
from cats.cat_group_innovation_trial_state import (
    CatGroupInnovationTrialDeniedResult,
    CatGroupInnovationTrialResult,
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
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


class CatGroupInnovationResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.founder = (
            self.cats.create_cat(
                name="founder",
                color="black",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        created_group = (
            self.groups.create_group(
                self.founder,
                name="innovation_group",
            )
        )

        self.group_id = (
            created_group.group_id
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

        self.innovations = (
            CatGroupInnovationSystem(
                self.groups
            )
        )

    def contribute_source(
        self,
        knowledge_id,
        confidence=1.0,
    ):
        self.knowledge.contribute(
            self.group_id,
            self.founder,
            knowledge_id=knowledge_id,
            content={
                "source": knowledge_id,
            },
            category="practice",
            confidence=confidence,
            verified=True,
        )

    def contribute_sources(
        self,
        first_confidence=1.0,
        second_confidence=1.0,
    ):
        self.contribute_source(
            "first_source",
            confidence=first_confidence,
        )

        self.contribute_source(
            "second_source",
            confidence=second_confidence,
        )

    def create_innovation(
        self,
        name="combined_practice",
        parent_innovation_id=None,
    ):
        return (
            self.innovations.combine(
                self.group_id,
                [
                    "first_source",
                    "second_source",
                ],
                name=name,
                category="practice",
                procedure={
                    "steps": [
                        "one",
                        "two",
                    ],
                },
                parent_innovation_id=
                    parent_innovation_id,
            )
        )

    def assert_not_mapping(
        self,
        result,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "name"
            ]

    def test_duplicate_sources_return_denied_object(
        self
    ):
        self.contribute_source(
            "first_source"
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        history_before = len(
            group.history
        )

        result = (
            self.innovations.combine(
                self.group_id,
                [
                    "first_source",
                    "first_source",
                ],
                name="duplicate_sources",
                category="practice",
                procedure={
                    "steps": []
                },
            )
        )

        self.assertIsInstance(
            result,
            CatGroupInnovationCreationDeniedResult,
        )

        self.assertFalse(
            result.created
        )

        self.assertEqual(
            result.name,
            "cat_group_innovation_denied",
        )

        self.assertEqual(
            result.reason,
            "at_least_two_knowledge_sources_required",
        )

        self.assertIsNone(
            result.missing
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assertEqual(
            len(group.innovations),
            0,
        )

        self.assertEqual(
            len(group.history),
            history_before,
        )

        self.assert_not_mapping(
            result
        )

    def test_missing_source_returns_denied_object(
        self
    ):
        self.contribute_source(
            "first_source"
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        history_before = len(
            group.history
        )

        result = (
            self.innovations.combine(
                self.group_id,
                [
                    "first_source",
                    "missing_source",
                ],
                name="missing_source_test",
                category="practice",
                procedure={
                    "steps": []
                },
            )
        )

        self.assertIsInstance(
            result,
            CatGroupInnovationCreationDeniedResult,
        )

        self.assertFalse(
            result.created
        )

        self.assertEqual(
            result.reason,
            "missing_knowledge",
        )

        self.assertEqual(
            result.missing,
            "missing_source",
        )

        self.assertEqual(
            len(group.innovations),
            0,
        )

        self.assertEqual(
            len(group.history),
            history_before,
        )

        self.assert_not_mapping(
            result
        )

    def test_combine_returns_creation_event_object(
        self
    ):
        self.contribute_sources(
            first_confidence=0.8,
            second_confidence=1.0,
        )

        result = (
            self.create_innovation()
        )

        self.assertIsInstance(
            result,
            CatGroupInnovationCreatedEvent,
        )

        self.assertTrue(
            result.created
        )

        self.assertEqual(
            result.name,
            "cat_group_innovation_created",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.innovation_name,
            "combined_practice",
        )

        self.assertEqual(
            result.sources,
            (
                "first_source",
                "second_source",
            ),
        )

        self.assertIsInstance(
            result.sources,
            tuple,
        )

        self.assertAlmostEqual(
            result.confidence,
            0.63,
        )

        self.assert_not_mapping(
            result
        )

    def test_combine_creates_domain_and_knowledge_records(
        self
    ):
        self.contribute_sources()

        procedure = {
            "steps": [
                "one",
                "two",
            ],
        }

        result = (
            self.innovations.combine(
                self.group_id,
                [
                    "first_source",
                    "second_source",
                ],
                name="combined_practice",
                category="practice",
                procedure=procedure,
            )
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        innovation = (
            group.innovations[
                result.innovation_id
            ]
        )

        self.assertEqual(
            innovation.innovation_id,
            result.innovation_id,
        )

        self.assertEqual(
            innovation.source_knowledge,
            [
                "first_source",
                "second_source",
            ],
        )

        self.assertEqual(
            innovation.procedure,
            procedure,
        )

        self.assertIsNot(
            innovation.procedure,
            procedure,
        )

        record = (
            group.knowledge[
                result.innovation_id
            ]
        )

        self.assertIsInstance(
            record,
            CatGroupKnowledgeRecord,
        )

        self.assertEqual(
            record.source_type,
            "innovation",
        )

        transmission = (
            record.transmission_path[
                0
            ]
        )

        self.assertIsInstance(
            transmission,
            CatGroupKnowledgeTransmission,
        )

        self.assertEqual(
            transmission.type,
            "innovation",
        )

        self.assertEqual(
            transmission.group,
            self.group_id,
        )

    def test_creation_history_is_serialized_boundary(
        self
    ):
        self.contribute_sources()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        result = (
            self.create_innovation()
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

        self.assertIsInstance(
            stored[
                "sources"
            ],
            list,
        )

        stored[
            "sources"
        ].append(
            "changed"
        )

        self.assertEqual(
            result.sources,
            (
                "first_source",
                "second_source",
            ),
        )

        fresh = (
            result.to_dict()
        )

        self.assertEqual(
            fresh[
                "sources"
            ],
            [
                "first_source",
                "second_source",
            ],
        )

    def test_parent_innovation_is_registered_in_tree(
        self
    ):
        self.contribute_sources()

        parent = (
            self.create_innovation(
                name="parent_innovation",
            )
        )

        child = (
            self.create_innovation(
                name="child_innovation",
                parent_innovation_id=
                    parent.innovation_id,
            )
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        parent_state = (
            group.innovation_tree[
                parent.innovation_id
            ]
        )

        child_state = (
            group.innovation_tree[
                child.innovation_id
            ]
        )

        self.assertEqual(
            child_state.parent,
            parent.innovation_id,
        )

        self.assertEqual(
            child_state.generation,
            1,
        )

        self.assertIn(
            child.innovation_id,
            parent_state.children,
        )

        self.assertEqual(
            group.innovations[
                child.innovation_id
            ].generation,
            1,
        )

    def test_unknown_trial_returns_denied_object(
        self
    ):
        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        history_before = len(
            group.history
        )

        result = (
            self.innovations.trial(
                self.group_id,
                "missing_innovation",
                success=True,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupInnovationTrialDeniedResult,
        )

        self.assertFalse(
            result.tested
        )

        self.assertEqual(
            result.name,
            "cat_group_innovation_trial_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_innovation",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assertEqual(
            len(group.history),
            history_before,
        )

        self.assert_not_mapping(
            result
        )

    def test_successful_trial_returns_object_and_updates_state(
        self
    ):
        self.contribute_sources()

        created = (
            self.create_innovation()
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        innovation = (
            group.innovations[
                created.innovation_id
            ]
        )

        knowledge = (
            group.knowledge[
                created.innovation_id
            ]
        )

        history_before = len(
            group.history
        )

        result = (
            self.innovations.trial(
                self.group_id,
                created.innovation_id,
                success=True,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupInnovationTrialResult,
        )

        self.assertTrue(
            result.tested
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            result.name,
            "cat_group_innovation_trial",
        )

        self.assertEqual(
            result.innovation_id,
            created.innovation_id,
        )

        self.assertEqual(
            innovation.successful_trials,
            1,
        )

        self.assertEqual(
            innovation.failed_trials,
            0,
        )

        self.assertEqual(
            knowledge.verification_count,
            1,
        )

        self.assertEqual(
            knowledge.contradiction_count,
            0,
        )

        self.assertEqual(
            knowledge.confidence,
            innovation.confidence,
        )

        self.assertEqual(
            len(group.history),
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

    def test_failed_trial_returns_object_and_updates_state(
        self
    ):
        self.contribute_sources()

        created = (
            self.create_innovation()
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        innovation = (
            group.innovations[
                created.innovation_id
            ]
        )

        knowledge = (
            group.knowledge[
                created.innovation_id
            ]
        )

        result = (
            self.innovations.trial(
                self.group_id,
                created.innovation_id,
                success=False,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupInnovationTrialResult,
        )

        self.assertFalse(
            result.success
        )

        self.assertEqual(
            innovation.successful_trials,
            0,
        )

        self.assertEqual(
            innovation.failed_trials,
            1,
        )

        self.assertAlmostEqual(
            innovation.confidence,
            0.5,
        )

        self.assertAlmostEqual(
            result.confidence,
            0.5,
        )

        self.assertEqual(
            knowledge.verification_count,
            0,
        )

        self.assertEqual(
            knowledge.contradiction_count,
            1,
        )

    def test_repeated_success_verifies_innovation_and_knowledge(
        self
    ):
        self.contribute_sources()

        created = (
            self.create_innovation()
        )

        first = (
            self.innovations.trial(
                self.group_id,
                created.innovation_id,
                success=True,
            )
        )

        second = (
            self.innovations.trial(
                self.group_id,
                created.innovation_id,
                success=True,
            )
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        innovation = (
            group.innovations[
                created.innovation_id
            ]
        )

        knowledge = (
            group.knowledge[
                created.innovation_id
            ]
        )

        self.assertFalse(
            first.verified
        )

        self.assertTrue(
            second.verified
        )

        self.assertTrue(
            innovation.verified
        )

        self.assertTrue(
            knowledge.verified
        )

        self.assertEqual(
            innovation.successful_trials,
            2,
        )

        self.assertEqual(
            knowledge.verification_count,
            2,
        )

    def test_results_are_immutable(
        self
    ):
        denied_creation = (
            self.innovations.combine(
                self.group_id,
                [],
                name="denied",
                category="practice",
                procedure={},
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_creation.reason = "changed"

        denied_trial = (
            self.innovations.trial(
                self.group_id,
                "missing",
                success=True,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_trial.reason = "changed"

        self.contribute_sources()

        created = (
            self.create_innovation()
        )

        with self.assertRaises(
            AttributeError
        ):
            created.innovation_id = "changed"

        trial = (
            self.innovations.trial(
                self.group_id,
                created.innovation_id,
                success=True,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            trial.confidence = 0.0


if __name__ == "__main__":
    unittest.main()
