import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
)
from cats.cat_group_innovation_system import (
    CatGroupInnovationSystem,
)
from cats.cat_social_objects import (
    CatGroupKnowledgeRecord,
    CatGroupKnowledgeTransmission,
)


class CatGroupKnowledgeTransmissionObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        universe = Universe()

        self.cats = Cats(
            universe
        )

        self.first_cat = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short",
        )

        self.second_cat = self.cats.create_cat(
            name="second",
            color="white",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                self.first_cat,
                name="first_group",
            )["group_id"]
        )

        self.second_group = (
            self.groups.create_group(
                self.second_cat,
                name="second_group",
            )["group_id"]
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = value["type"]

    def test_record_rejects_mapping_transmission(
        self
    ):
        with self.assertRaises(TypeError):
            CatGroupKnowledgeRecord(
                knowledge_id="legacy",
                transmission_path=[
                    {
                        "type": "legacy",
                    }
                ],
            )

    def test_personal_knowledge_records_object_transmission(
        self
    ):
        self.knowledge.contribute(
            self.first_group,
            self.first_cat,
            knowledge_id="safe_route",
            content={
                "route": "bar_to_library",
            },
            category="navigation",
        )

        record = (
            self.groups
            .groups[self.first_group]
            .knowledge["safe_route"]
        )

        transmission = (
            record.transmission_path[0]
        )

        self.assertIsInstance(
            transmission,
            CatGroupKnowledgeTransmission,
        )

        self.assert_object_only(
            transmission
        )

        self.assertEqual(
            transmission.type,
            "personal_experience",
        )

        self.assertEqual(
            transmission.source,
            self.first_cat.name,
        )

        self.assertEqual(
            transmission.group,
            self.first_group,
        )

        snapshot = record.to_dict()

        snapshot[
            "transmission_path"
        ][0]["source"] = "changed"

        self.assertEqual(
            transmission.source,
            self.first_cat.name,
        )

    def test_group_transmission_appends_object(
        self
    ):
        self.knowledge.contribute(
            self.first_group,
            self.first_cat,
            knowledge_id="safe_route",
            content={
                "route": "bar_to_library",
            },
            category="navigation",
        )

        self.knowledge.transmit_between_groups(
            self.first_group,
            self.second_group,
            "safe_route",
        )

        record = (
            self.groups
            .groups[self.second_group]
            .knowledge["safe_route"]
        )

        transmission = (
            record.transmission_path[-1]
        )

        self.assertIsInstance(
            transmission,
            CatGroupKnowledgeTransmission,
        )

        self.assert_object_only(
            transmission
        )

        self.assertEqual(
            transmission.type,
            "allied_group",
        )

        self.assertEqual(
            transmission.source_group,
            self.first_group,
        )

        self.assertEqual(
            transmission.target_group,
            self.second_group,
        )

    def test_innovation_knowledge_records_object_transmission(
        self
    ):
        for knowledge_id in (
            "first_source",
            "second_source",
        ):
            self.knowledge.contribute(
                self.first_group,
                self.first_cat,
                knowledge_id=knowledge_id,
                content={
                    "source": knowledge_id,
                },
                category="practice",
            )

        result = (
            CatGroupInnovationSystem(
                self.groups
            ).combine(
                self.first_group,
                [
                    "first_source",
                    "second_source",
                ],
                name="combined_practice",
                category="practice",
                procedure={
                    "steps": [
                        "one",
                        "two",
                    ]
                },
            )
        )

        record = (
            self.groups
            .groups[self.first_group]
            .knowledge[
                result["innovation_id"]
            ]
        )

        transmission = (
            record.transmission_path[0]
        )

        self.assertIsInstance(
            transmission,
            CatGroupKnowledgeTransmission,
        )

        self.assert_object_only(
            transmission
        )

        self.assertEqual(
            transmission.type,
            "innovation",
        )

        self.assertEqual(
            transmission.group,
            self.first_group,
        )


if __name__ == "__main__":
    unittest.main()
