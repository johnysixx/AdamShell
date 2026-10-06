import unittest

from cats.cat_group_innovation_creation_state import (
    CatGroupInnovationCreatedEvent,
)
from cats.cat_group_innovation_system import (
    CatGroupInnovationSystem,
)
from cats.cat_group_knowledge_contribution_state import (
    CatGroupKnowledgeContributedEvent,
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
)
from cats.cat_group_knowledge_transmission_state import (
    CatGroupKnowledgeTransmittedEvent,
)
from cats.cat_group_knowledge_verification_state import (
    CatGroupKnowledgeVerifiedEvent,
)
from cats.cat_group_myth_creation_state import (
    CatGroupMythCreatedEvent,
)
from cats.cat_group_myth_system import (
    CatGroupMythSystem,
)
from cats.cat_group_norm_definition_state import (
    CatGroupNormDefinedEvent,
)
from cats.cat_group_norm_system import (
    CatGroupNormSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupCulturalKnowledgeHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name="culture_first",
            color="black",
            fur_length="short",
        )

        self.second = self.cats.create_cat(
            name="culture_second",
            color="white",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                self.first,
                name="first_culture",
            ).group_id
        )

        self.second_group = (
            self.groups.create_group(
                self.second,
                name="second_culture",
            ).group_id
        )

        self.knowledge = CatGroupKnowledgeSystem(
            self.groups
        )

    def assert_object_only(
        self,
        event,
    ):
        for method_name in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    method_name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = event[
                "name"
            ]

    def contribute(
        self,
        knowledge_id="safe_route",
        confidence=1.0,
        verified=True,
    ):
        return self.knowledge.contribute(
            self.first_group,
            self.first,
            knowledge_id,
            {
                "route": "bar_to_library",
            },
            "navigation",
            confidence=confidence,
            verified=verified,
        )

    def test_knowledge_contribution_history_is_object(
        self
    ):
        result = self.contribute()

        stored = (
            self.groups.groups[
                self.first_group
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupKnowledgeContributedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )

    def test_knowledge_transmission_histories_are_objects(
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

        source_event = (
            self.groups.groups[
                self.first_group
            ].history[
                -1
            ]
        )

        target_event = (
            self.groups.groups[
                self.second_group
            ].history[
                -1
            ]
        )

        for event in (
            source_event,
            target_event,
        ):
            self.assertIsInstance(
                event,
                CatGroupKnowledgeTransmittedEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assert_object_only(
                event
            )

        self.assertIsNot(
            source_event,
            target_event,
        )

    def test_knowledge_verification_history_is_object(
        self
    ):
        self.contribute(
            confidence=0.5,
            verified=False,
        )

        result = self.knowledge.verify(
            self.first_group,
            self.first,
            "safe_route",
            confirmed=True,
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
            CatGroupKnowledgeVerifiedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )

    def test_norm_definition_history_is_object(
        self
    ):
        result = CatGroupNormSystem(
            self.groups
        ).define(
            self.first_group,
            "quiet_sleep",
            "social",
            {
                "action": "stay_quiet",
            },
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
            CatGroupNormDefinedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )

    def test_myth_creation_history_is_object(
        self
    ):
        self.contribute(
            knowledge_id="danger_scent",
            confidence=0.8,
        )

        result = CatGroupMythSystem(
            self.groups
        ).create_from_knowledge(
            self.first_group,
            "danger_scent",
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

        self.assert_object_only(
            stored
        )

    def test_innovation_creation_history_is_object(
        self
    ):
        self.contribute(
            knowledge_id="safe_route",
        )

        self.contribute(
            knowledge_id="danger_scent",
        )

        result = CatGroupInnovationSystem(
            self.groups
        ).combine(
            self.first_group,
            [
                "safe_route",
                "danger_scent",
            ],
            name="safe_scent_route",
            category="navigation",
            procedure={
                "rule": "avoid danger scent",
            },
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
            CatGroupInnovationCreatedEvent,
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
            stored.sources,
            (
                "safe_route",
                "danger_scent",
            ),
        )

        self.assert_object_only(
            stored
        )


if __name__ == "__main__":
    unittest.main()
