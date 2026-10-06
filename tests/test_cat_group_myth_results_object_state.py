import unittest

from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
)
from cats.cat_group_myth_creation_state import (
    CatGroupMythCreatedEvent,
    CatGroupMythCreationDeniedResult,
)
from cats.cat_group_myth_retelling_state import (
    CatGroupMythRetoldResult,
    CatGroupMythRetellingDeniedResult,
)
from cats.cat_group_myth_system import (
    CatGroupMythSystem,
)
from cats.cat_group_myth_telling_state import (
    CatGroupMythToldResult,
    CatGroupMythTellingDeniedResult,
)
from cats.cat_group_myth_verification_state import (
    CatGroupMythVerificationDeniedResult,
    CatGroupMythVerificationResult,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_myth_lineage_state import (
    CatMythLineageState,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupMythResultsObjectStateTests(
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

        self.listener = (
            self.cats.create_cat(
                name="listener",
                color="white",
                fur_length="short",
            )
        )

        self.target_founder = (
            self.cats.create_cat(
                name="target_founder",
                color="gray",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        self.group_id = (
            self.groups.create_group(
                self.founder,
                name="myth_group",
            ).group_id
        )

        self.target_group_id = (
            self.groups.create_group(
                self.target_founder,
                name="target_group",
            ).group_id
        )

        self.groups.add_member(
            self.group_id,
            self.listener,
            self.cats.cats,
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

        self.myths = (
            CatGroupMythSystem(
                self.groups
            )
        )

    def contribute_source(
        self,
        knowledge_id="danger_scent",
        confidence=0.8,
        verified=True,
    ):
        self.knowledge.contribute(
            self.group_id,
            self.founder,
            knowledge_id=knowledge_id,
            content={
                "aroma": "cronenberg",
                "danger": True,
            },
            category="danger",
            confidence=confidence,
            verified=verified,
        )

    def create_myth(
        self,
        knowledge_id="danger_scent",
    ):
        return (
            self.myths.create_from_knowledge(
                self.group_id,
                knowledge_id,
                title="The Scent",
                interpretation={
                    "claim":
                        "the scent predicts danger"
                },
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

    def test_unknown_knowledge_returns_creation_denied_object(
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
            self.myths.create_from_knowledge(
                self.group_id,
                "missing_knowledge",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythCreationDeniedResult,
        )

        self.assertFalse(
            result.created
        )

        self.assertEqual(
            result.reason,
            "unknown_knowledge",
        )

        self.assertEqual(
            result.name,
            "cat_group_myth_creation_denied",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assertEqual(
            len(group.myths),
            0,
        )

        self.assertEqual(
            len(group.history),
            history_before,
        )

        self.assert_not_mapping(
            result
        )

    def test_creation_returns_event_and_domain_myth(
        self
    ):
        self.contribute_source()

        interpretation = {
            "claim":
                "the scent predicts danger"
        }

        result = (
            self.myths.create_from_knowledge(
                self.group_id,
                "danger_scent",
                title="The Scent",
                interpretation=interpretation,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythCreatedEvent,
        )

        self.assertTrue(
            result.created
        )

        self.assertEqual(
            result.name,
            "cat_group_myth_created",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.source_knowledge,
            "danger_scent",
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        myth = (
            group.myths[
                result.myth_id
            ]
        )

        self.assertEqual(
            myth.title,
            "The Scent",
        )

        self.assertEqual(
            myth.interpretation,
            interpretation,
        )

        self.assertIsNot(
            myth.interpretation,
            interpretation,
        )

        self.assertFalse(
            myth.verified
        )

        self.assertAlmostEqual(
            myth.credibility,
            0.6,
        )

        self.assert_not_mapping(
            result
        )

    def test_creation_registers_lineage_object(
        self
    ):
        self.contribute_source()

        result = (
            self.create_myth()
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        lineage = (
            group.myth_lineages[
                result.myth_id
            ]
        )

        self.assertIsInstance(
            lineage,
            CatMythLineageState,
        )

        self.assertEqual(
            lineage.root_myth,
            result.myth_id,
        )

        self.assertEqual(
            lineage.versions,
            [
                result.myth_id
            ],
        )

        myth = (
            group.myths[
                result.myth_id
            ]
        )

        self.assertEqual(
            myth.lineage_root,
            result.myth_id,
        )

        self.assertIsNone(
            myth.parent_version
        )

        self.assertEqual(
            myth.generation,
            0,
        )

    def test_creation_history_is_detached_object_event(
        self
    ):
        self.contribute_source()

        group = self.groups.groups[
            self.group_id
        ]

        result = self.create_myth()

        stored = group.history[
            -1
        ]

        self.assertIsInstance(
            stored,
            CatGroupMythCreatedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assertEqual(
            stored.myth_id,
            result.myth_id,
        )

        self.assertFalse(
            hasattr(
                stored,
                "to_dict",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            stored.myth_id = "changed"

        self.assertEqual(
            result.source_knowledge,
            "danger_scent",
        )

    def test_unknown_myth_returns_retelling_denied_object(
        self
    ):
        result = (
            self.myths.retell(
                self.group_id,
                self.target_group_id,
                "missing_myth",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythRetellingDeniedResult,
        )

        self.assertFalse(
            result.retold
        )

        self.assertEqual(
            result.reason,
            "unknown_myth",
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

    def test_transformed_retelling_returns_object_and_descendant(
        self
    ):
        self.contribute_source()

        created = (
            self.create_myth()
        )

        transformation = {
            "claim":
                "all strange boxes are dangerous"
        }

        result = (
            self.myths.retell(
                self.group_id,
                self.target_group_id,
                created.myth_id,
                transformation=
                    transformation,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythRetoldResult,
        )

        self.assertTrue(
            result.retold
        )

        self.assertTrue(
            result.transformed
        )

        self.assertNotEqual(
            result.myth_id,
            created.myth_id,
        )

        self.assertEqual(
            result.parent_myth_id,
            created.myth_id,
        )

        self.assertEqual(
            result.root_myth_id,
            created.myth_id,
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        target = (
            self.groups.groups[
                self.target_group_id
            ]
        )

        copied = (
            target.myths[
                result.myth_id
            ]
        )

        self.assertEqual(
            copied.parent_version,
            created.myth_id,
        )

        self.assertEqual(
            copied.generation,
            1,
        )

        self.assertEqual(
            copied.transformations,
            1,
        )

        self.assertEqual(
            copied.interpretation,
            transformation,
        )

        self.assertIsNot(
            copied.interpretation,
            transformation,
        )

        lineage = (
            target.myth_lineages[
                result.root_myth_id
            ]
        )

        self.assertIsInstance(
            lineage,
            CatMythLineageState,
        )

        self.assertIn(
            result.myth_id,
            lineage.versions,
        )

        self.assertEqual(
            lineage.children[
                created.myth_id
            ],
            [
                result.myth_id
            ],
        )

        self.assert_not_mapping(
            result
        )

    def test_untransformed_retelling_preserves_myth_identity(
        self
    ):
        self.contribute_source()

        created = (
            self.create_myth()
        )

        result = (
            self.myths.retell(
                self.group_id,
                self.target_group_id,
                created.myth_id,
            )
        )

        self.assertTrue(
            result.retold
        )

        self.assertFalse(
            result.transformed
        )

        self.assertEqual(
            result.myth_id,
            created.myth_id,
        )

        target_myth = (
            self.groups.groups[
                self.target_group_id
            ].myths[
                result.myth_id
            ]
        )

        self.assertEqual(
            target_myth.generation,
            0,
        )

        self.assertEqual(
            target_myth.retellings,
            1,
        )

        self.assertEqual(
            target_myth.transmission_path,
            [
                self.group_id,
                self.target_group_id,
            ],
        )

    def test_unknown_myth_returns_telling_denied_object(
        self
    ):
        result = (
            self.myths.tell_members(
                self.group_id,
                self.cats.cats,
                "missing_myth",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythTellingDeniedResult,
        )

        self.assertFalse(
            result.told
        )

        self.assertEqual(
            result.reason,
            "unknown_myth",
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

    def test_tell_members_returns_object_and_personal_copies(
        self
    ):
        self.contribute_source()

        created = (
            self.create_myth()
        )

        group_myth = (
            self.groups.groups[
                self.group_id
            ].myths[
                created.myth_id
            ]
        )

        result = (
            self.myths.tell_members(
                self.group_id,
                self.cats.cats,
                created.myth_id,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythToldResult,
        )

        self.assertTrue(
            result.told
        )

        self.assertIsInstance(
            result.listeners,
            tuple,
        )

        self.assertIn(
            self.founder.name,
            result.listeners,
        )

        self.assertIn(
            self.listener.name,
            result.listeners,
        )

        for cat in (
            self.founder,
            self.listener,
        ):
            personal = (
                cat.knowledge
                .heard_group_myths[
                    created.myth_id
                ]
            )

            self.assertIsNot(
                personal,
                group_myth,
            )

            self.assertEqual(
                personal.heard_from_group,
                self.group_id,
            )

            self.assertFalse(
                personal.personally_verified
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

    def test_unknown_myth_returns_verification_denied_object(
        self
    ):
        result = (
            self.myths.verify_against_knowledge(
                self.group_id,
                "missing_myth",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythVerificationDeniedResult,
        )

        self.assertFalse(
            result.verified
        )

        self.assertEqual(
            result.reason,
            "unknown_myth",
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

    def test_missing_source_returns_verification_denied_object(
        self
    ):
        self.contribute_source()

        created = (
            self.create_myth()
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        del group.knowledge[
            "danger_scent"
        ]

        result = (
            self.myths.verify_against_knowledge(
                self.group_id,
                created.myth_id,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythVerificationDeniedResult,
        )

        self.assertEqual(
            result.reason,
            "source_knowledge_missing",
        )

        self.assertFalse(
            result.verified
        )

    def test_verification_returns_object_and_updates_myth(
        self
    ):
        self.contribute_source(
            confidence=0.95,
            verified=True,
        )

        created = (
            self.create_myth()
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        myth = (
            group.myths[
                created.myth_id
            ]
        )

        self.assertFalse(
            myth.verified
        )

        result = (
            self.myths.verify_against_knowledge(
                self.group_id,
                created.myth_id,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythVerificationResult,
        )

        self.assertTrue(
            result.verified
        )

        self.assertTrue(
            myth.verified
        )

        self.assertAlmostEqual(
            result.credibility,
            0.95,
        )

        self.assertAlmostEqual(
            myth.credibility,
            0.95,
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

    def test_unverified_knowledge_still_returns_verification_result(
        self
    ):
        self.contribute_source(
            confidence=0.8,
            verified=False,
        )

        created = (
            self.create_myth()
        )

        result = (
            self.myths.verify_against_knowledge(
                self.group_id,
                created.myth_id,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMythVerificationResult,
        )

        self.assertFalse(
            result.verified
        )

        self.assertAlmostEqual(
            result.credibility,
            0.6,
        )

    def test_results_are_immutable(
        self
    ):
        denied_creation = (
            self.myths.create_from_knowledge(
                self.group_id,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_creation.reason = "changed"

        denied_retelling = (
            self.myths.retell(
                self.group_id,
                self.target_group_id,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_retelling.reason = "changed"

        denied_telling = (
            self.myths.tell_members(
                self.group_id,
                self.cats.cats,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_telling.reason = "changed"

        denied_verification = (
            self.myths.verify_against_knowledge(
                self.group_id,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied_verification.reason = "changed"

        self.contribute_source()

        created = (
            self.create_myth()
        )

        with self.assertRaises(
            AttributeError
        ):
            created.myth_id = "changed"

        retold = (
            self.myths.retell(
                self.group_id,
                self.target_group_id,
                created.myth_id,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            retold.credibility = 0.0

        told = (
            self.myths.tell_members(
                self.group_id,
                self.cats.cats,
                created.myth_id,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            told.listeners = ()

        verified = (
            self.myths.verify_against_knowledge(
                self.group_id,
                created.myth_id,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            verified.credibility = 0.0


if __name__ == "__main__":
    unittest.main()
