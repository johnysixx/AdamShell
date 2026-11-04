from core.entity.social_entity import SocialEntity
import unittest
from types import SimpleNamespace
from universe.cat_recipient_registry import CatRecipientRegistry

class CatRecipientRegistryTests(unittest.TestCase):

    def test_register_and_find_recipient(self):
        registry = CatRecipientRegistry()
        entity = SocialEntity.from_mapping({'id': 'alice', 'name': 'Alice', 'type': 'human', 'needs_cat': True, 'current_layer': 'idea_universe', 'position': {'x': 1.0, 'y': 2.0, 'z': 3.0}})
        registered = registry.register(entity)
        self.assertIs(registered, entity)
        self.assertIs(registry.find('alice'), entity)

    def test_any_entity_can_need_cat(self):
        registry = CatRecipientRegistry()
        entity = SocialEntity.from_mapping({'id': 'strange_entity', 'type': 'idea_entity', 'needs_cat': True})
        registry.register(entity)
        waiting = registry.waiting_for_cat()
        self.assertEqual(waiting, [entity])

    def test_public_state_serializes_object_entities(self):
        registry = CatRecipientRegistry()
        entity = SocialEntity(
            id="alice",
            type="human",
            needs_cat=True,
        )

        registry.register(entity)

        snapshot = registry.public_state

        self.assertEqual(
            snapshot["type"],
            "cat_recipient_registry",
        )

        self.assertEqual(
            snapshot["recipient_count"],
            1,
        )

        self.assertEqual(
            snapshot["recipients"],
            [{
                "id": "alice",
                "type": "human",
                "needs_cat": True,
            }],
        )

        self.assertIs(registry.find("alice"), entity)

    def test_public_state_does_not_mutate_live_objects(self):
        registry = CatRecipientRegistry()
        entity = SocialEntity(
            id="alice",
            type="human",
            needs_cat=True,
        )

        registry.register(entity)
        snapshot = registry.public_state

        snapshot["recipients"][0]["needs_cat"] = False
        snapshot["recipients"].clear()

        self.assertTrue(entity.needs_cat)
        self.assertIs(registry.find("alice"), entity)
        self.assertEqual(len(registry.recipients), 1)

        updated = registry.public_state
        self.assertTrue(
            updated["recipients"][0]["needs_cat"]
        )

    def test_register_rejects_missing_serializer(self):
        registry = CatRecipientRegistry()

        entity = SimpleNamespace(
            id="invalid",
            type="human",
            needs_cat=True,
        )

        with self.assertRaisesRegex(
            TypeError,
            "to_dict",
        ):
            registry.register(entity)

        self.assertEqual(
            registry.recipients,
            [],
        )

        self.assertEqual(
            registry.public_state["recipient_count"],
            0,
        )

    def test_register_rejects_noncallable_serializer(self):
        registry = CatRecipientRegistry()

        entity = SimpleNamespace(
            id="invalid",
            type="human",
            needs_cat=True,
            to_dict=None,
        )

        with self.assertRaisesRegex(
            TypeError,
            "to_dict",
        ):
            registry.register(entity)

        self.assertEqual(
            registry.waiting_for_cat(),
            [],
        )

        self.assertEqual(
            registry.public_state["recipients"],
            [],
        )

    def test_invalid_registration_preserves_valid_recipients(self):
        registry = CatRecipientRegistry()

        valid = SocialEntity(
            id="alice",
            type="human",
            needs_cat=True,
        )

        self.assertIs(
            registry.register(valid),
            valid,
        )

        invalid = SimpleNamespace(
            id="broken",
            type="human",
            needs_cat=True,
        )

        with self.assertRaisesRegex(
            TypeError,
            "to_dict",
        ):
            registry.register(invalid)

        self.assertIs(
            registry.find("alice"),
            valid,
        )

        self.assertEqual(
            registry.waiting_for_cat(),
            [valid],
        )

        self.assertIs(
            registry.register(valid),
            valid,
        )

        self.assertEqual(
            len(registry.recipients),
            1,
        )

        snapshot = registry.public_state

        self.assertEqual(
            snapshot["recipient_count"],
            1,
        )

        self.assertEqual(
            snapshot["recipients"],
            [{
                "id": "alice",
                "type": "human",
                "needs_cat": True,
            }],
        )

    def test_empty_registry_public_state(self):
        registry = CatRecipientRegistry()

        self.assertEqual(
            registry.public_state,
            {
                "type": "cat_recipient_registry",
                "recipient_count": 0,
                "recipients": [],
            },
        )


    def test_nested_snapshot_does_not_mutate_entity(self):
        registry = CatRecipientRegistry()
        entity = SocialEntity(
            id="alice",
            type="human",
            needs_cat=True,
            metadata={
                "preferences": {
                    "milk": ["warm"],
                },
            },
        )

        registry.register(entity)
        snapshot = registry.public_state

        snapshot["recipients"][0][
            "metadata"
        ]["preferences"]["milk"].append("cold")

        self.assertEqual(
            entity.metadata["preferences"]["milk"],
            ["warm"],
        )

        self.assertIs(
            registry.find("alice"),
            entity,
        )

        self.assertEqual(
            registry.public_state["recipients"][0][
                "metadata"
            ]["preferences"]["milk"],
            ["warm"],
        )

    def test_public_snapshots_are_independent(self):
        registry = CatRecipientRegistry()
        entity = SocialEntity(
            id="alice",
            type="human",
            metadata={
                "notes": ["first"],
            },
        )

        registry.register(entity)

        first = registry.public_state
        second = registry.public_state

        first["recipients"][0][
            "metadata"
        ]["notes"].append("changed")

        self.assertEqual(
            second["recipients"][0][
                "metadata"
            ]["notes"],
            ["first"],
        )

        self.assertEqual(
            entity.metadata["notes"],
            ["first"],
        )

if __name__ == '__main__':
    unittest.main()
