import unittest

from core.entity.social_entity import (
    SocialEntity,
    SocialRelationshipRegistry,
)


class SocialEntityMetadataSnapshotTests(
    unittest.TestCase
):

    def make_entity(self):
        return SocialEntity(
            name="test_entity",
            type="human",
            metadata={
                "preferences": {
                    "notes": ["original"],
                },
            },
        )

    def test_to_dict_detaches_nested_metadata(self):
        entity = self.make_entity()

        first = entity.to_dict()
        second = entity.to_dict()

        first["metadata"]["preferences"][
            "notes"
        ].append("snapshot_only")

        self.assertEqual(
            entity.metadata["preferences"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["metadata"]["preferences"]["notes"],
            ["original"],
        )

        self.assertEqual(
            entity.to_dict()["metadata"][
                "preferences"
            ]["notes"],
            ["original"],
        )

        self.assertIsNot(
            first["metadata"],
            entity.metadata,
        )

        self.assertIsNot(
            first["metadata"]["preferences"],
            entity.metadata["preferences"],
        )

    def test_metadata_snapshot_ignores_later_changes(self):
        entity = self.make_entity()

        snapshot = entity.to_dict()

        entity.metadata["preferences"][
            "notes"
        ].append("live_change")

        self.assertEqual(
            snapshot["metadata"]["preferences"][
                "notes"
            ],
            ["original"],
        )

        self.assertEqual(
            entity.to_dict()["metadata"][
                "preferences"
            ]["notes"],
            ["original", "live_change"],
        )

        self.assertEqual(
            snapshot["name"],
            "test_entity",
        )

    def test_typed_relationship_serialization_is_preserved(self):
        entity = SocialEntity.from_mapping({
            "name": "guest",
            "type": "human",
            "metadata": {
                "preferences": {
                    "notes": ["original"],
                },
            },
            "social_relationships": {
                "lilith": {
                    "affinity": 0.4,
                    "pet_count": 2,
                    "last_interaction": "pet",
                },
            },
        })

        registry = entity.social_relationships

        self.assertIsInstance(
            registry,
            SocialRelationshipRegistry,
        )

        snapshot = entity.to_dict()

        snapshot["metadata"]["preferences"][
            "notes"
        ].append("snapshot_only")

        snapshot["social_relationships"][
            "lilith"
        ]["affinity"] = 1.0

        self.assertEqual(
            entity.metadata["preferences"]["notes"],
            ["original"],
        )

        self.assertIs(
            entity.social_relationships,
            registry,
        )

        self.assertEqual(
            registry.relationship_for("lilith").affinity,
            0.4,
        )

        self.assertEqual(
            entity.to_dict()["social_relationships"][
                "lilith"
            ]["affinity"],
            0.4,
        )

        self.assertEqual(
            entity.to_dict()["metadata"][
                "preferences"
            ]["notes"],
            ["original"],
        )


if __name__ == "__main__":
    unittest.main()
