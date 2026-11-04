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

    def test_direct_constructor_captures_metadata(self):
        external = {
            "preferences": {
                "notes": ["original"],
            },
        }

        entity = SocialEntity(
            name="direct_guest",
            type="human",
            metadata=external,
        )

        self.assertIsNot(
            entity.metadata,
            external,
        )

        self.assertIsNot(
            entity.metadata["preferences"],
            external["preferences"],
        )

        external["preferences"][
            "notes"
        ].append("external_change")

        self.assertEqual(
            entity.metadata["preferences"]["notes"],
            ["original"],
        )

        self.assertEqual(
            entity.to_dict()["metadata"][
                "preferences"
            ]["notes"],
            ["original"],
        )

    def test_direct_entities_do_not_share_metadata(self):
        shared = {
            "preferences": {
                "notes": ["original"],
            },
        }

        first = SocialEntity(
            name="first",
            type="human",
            metadata=shared,
        )

        second = SocialEntity(
            name="second",
            type="human",
            metadata=shared,
        )

        first.metadata["preferences"][
            "notes"
        ].append("first_only")

        self.assertEqual(
            first.metadata["preferences"]["notes"],
            ["original", "first_only"],
        )

        self.assertEqual(
            second.metadata["preferences"]["notes"],
            ["original"],
        )

        self.assertEqual(
            shared["preferences"]["notes"],
            ["original"],
        )

        self.assertIsNot(
            first.metadata["preferences"],
            second.metadata["preferences"],
        )

    def test_direct_constructor_keeps_typed_references(self):
        from core.entity.world_existence_state import (
            WorldExistenceState,
        )

        existence = WorldExistenceState.of(
            root_universe=70.0,
        )

        relationships = (
            SocialRelationshipRegistry.from_mapping({
                "lilith": {
                    "affinity": 0.4,
                    "pet_count": 2,
                    "last_interaction": "pet",
                },
            })
        )

        external = {
            "preferences": {
                "notes": ["original"],
            },
        }

        entity = SocialEntity(
            name="typed_direct_guest",
            type="human",
            metadata=external,
            existence_by_world=existence,
            social_relationships=relationships,
        )

        self.assertIs(
            entity.existence_by_world,
            existence,
        )

        self.assertIs(
            entity.social_relationships,
            relationships,
        )

        self.assertIs(
            SocialEntity.from_mapping(entity),
            entity,
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

        self.assertEqual(
            external["preferences"]["notes"],
            ["original"],
        )

        self.assertEqual(
            existence.percent_in("root_universe"),
            70.0,
        )

        self.assertEqual(
            relationships.relationship_for(
                "lilith"
            ).affinity,
            0.4,
        )

    def test_from_mapping_captures_nested_metadata(self):
        source = {
            "name": "imported_entity",
            "type": "human",
            "metadata": {
                "preferences": {
                    "notes": ["original"],
                },
            },
        }

        entity = SocialEntity.from_mapping(source)

        self.assertIsNot(
            entity.metadata,
            source["metadata"],
        )

        self.assertIsNot(
            entity.metadata["preferences"],
            source["metadata"]["preferences"],
        )

        source["metadata"]["preferences"][
            "notes"
        ].append("external_change")

        self.assertEqual(
            entity.metadata["preferences"]["notes"],
            ["original"],
        )

        self.assertEqual(
            entity.to_dict()["metadata"][
                "preferences"
            ]["notes"],
            ["original"],
        )

    def test_imported_entities_do_not_share_metadata(self):
        source = {
            "name": "shared_source",
            "type": "human",
            "metadata": {
                "preferences": {
                    "notes": ["original"],
                },
            },
        }

        first = SocialEntity.from_mapping(source)
        second = SocialEntity.from_mapping(source)

        first.metadata["preferences"][
            "notes"
        ].append("first_only")

        self.assertEqual(
            first.metadata["preferences"]["notes"],
            ["original", "first_only"],
        )

        self.assertEqual(
            second.metadata["preferences"]["notes"],
            ["original"],
        )

        self.assertEqual(
            source["metadata"]["preferences"][
                "notes"
            ],
            ["original"],
        )

        self.assertIsNot(
            first.metadata["preferences"],
            second.metadata["preferences"],
        )

    def test_mapping_import_preserves_typed_state(self):
        from core.entity.world_existence_state import (
            WorldExistenceState,
        )

        source = {
            "name": "typed_guest",
            "type": "human",
            "metadata": {
                "preferences": {
                    "notes": ["original"],
                },
            },
            "existence_by_world": {
                "root_universe": 70.0,
            },
            "social_relationships": {
                "lilith": {
                    "affinity": 0.4,
                    "pet_count": 2,
                    "last_interaction": "pet",
                },
            },
        }

        entity = SocialEntity.from_mapping(source)

        self.assertIsInstance(
            entity.existence_by_world,
            WorldExistenceState,
        )

        self.assertIsInstance(
            entity.social_relationships,
            SocialRelationshipRegistry,
        )

        self.assertIs(
            SocialEntity.from_mapping(entity),
            entity,
        )

        source["metadata"]["preferences"][
            "notes"
        ].append("external_change")

        source["existence_by_world"][
            "root_universe"
        ] = 0.0

        source["social_relationships"][
            "lilith"
        ]["affinity"] = 1.0

        self.assertEqual(
            entity.metadata["preferences"]["notes"],
            ["original"],
        )

        self.assertEqual(
            entity.existence_by_world.percent_in(
                "root_universe"
            ),
            70.0,
        )

        self.assertEqual(
            entity.social_relationships
            .relationship_for("lilith")
            .affinity,
            0.4,
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
