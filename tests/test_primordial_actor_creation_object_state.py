import unittest
from unittest.mock import patch

from core.entity.departure_state import EntityDepartureIntent
from core.entity.social_entity import SocialEntity
from gods.god_actor_state import GodCreationLimits, GodDivineAttributes
from gods.gods import Gods
from idea_entities import IdeaEntities
from idea_entities.idea_actor_state import IdeaPrePhysicalAttributes
from universe.universe import Universe


class PrimordialActorCreationObjectStateTests(unittest.TestCase):

    def _assert_object_only(self, value, key):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def test_idea_entity_creation_uses_object_substate(self):
        layer = IdeaEntities(Universe())
        entity = layer.create_idea_entity(
            name="serpent",
            active=True,
            existence_pct=100.0,
        )

        self.assertIsInstance(
            entity.departure_intent,
            EntityDepartureIntent,
        )
        self.assertIsInstance(
            entity.pre_physical_attributes,
            IdeaPrePhysicalAttributes,
        )
        self.assertFalse(
            entity.departure_intent.wants_to_leave
        )
        self.assertTrue(
            entity.pre_physical_attributes.can_exist_before_form
        )
        self.assertTrue(
            entity.pre_physical_attributes.can_hold_will
        )

    def test_god_creation_uses_object_substate(self):
        layer = Gods(Universe())
        god = layer.create_god(
            name="god",
            role="creator_entity",
        )

        self.assertIsInstance(
            god.departure_intent,
            EntityDepartureIntent,
        )
        self.assertIsInstance(
            god.divine_attributes,
            GodDivineAttributes,
        )
        self.assertIsInstance(
            god.creation_limits,
            GodCreationLimits,
        )
        self.assertTrue(god.divine_attributes.aseity)
        self.assertEqual(
            god.divine_attributes.creative_authority,
            "potential",
        )
        self.assertTrue(
            god.creation_limits.limited_by_creative_will
        )

    def test_creation_substates_are_object_only(self):
        idea_entity = IdeaEntities(
            Universe()
        ).create_idea_entity("serpent")
        god = Gods(
            Universe()
        ).create_god("god")

        self._assert_object_only(
            idea_entity.departure_intent,
            "wants_to_leave",
        )
        self._assert_object_only(
            idea_entity.pre_physical_attributes,
            "can_influence",
        )
        self._assert_object_only(
            god.divine_attributes,
            "aseity",
        )
        self._assert_object_only(
            god.creation_limits,
            "limited_by_creative_will",
        )

    def test_departure_intent_changes_through_domain_methods(self):
        intent = EntityDepartureIntent()

        intent.request_departure()
        self.assertTrue(intent.wants_to_leave)

        intent.cancel_departure()
        self.assertFalse(intent.wants_to_leave)

    def test_substate_snapshots_are_detached_dicts(self):
        intent = EntityDepartureIntent()
        attributes = IdeaPrePhysicalAttributes()
        divine = GodDivineAttributes()
        limits = GodCreationLimits()

        intent_snapshot = intent.to_dict()
        attributes_snapshot = attributes.to_dict()
        divine_snapshot = divine.to_dict()
        limits_snapshot = limits.to_dict()

        intent_snapshot["wants_to_leave"] = True
        attributes_snapshot["can_influence"] = False
        divine_snapshot["aseity"] = False
        limits_snapshot["limited_by_creative_will"] = False

        self.assertFalse(intent.wants_to_leave)
        self.assertTrue(attributes.can_influence)
        self.assertTrue(divine.aseity)
        self.assertTrue(limits.limited_by_creative_will)

    def test_factories_do_not_use_social_entity_mapping_constructor(self):
        with patch.object(
            SocialEntity,
            "from_mapping",
            side_effect=AssertionError(
                "mapping constructor must not be used"
            ),
        ):
            idea_entity = IdeaEntities(
                Universe()
            ).create_idea_entity("serpent")
            god = Gods(
                Universe()
            ).create_god("god")

        self.assertEqual(idea_entity.name, "serpent")
        self.assertEqual(god.name, "god")


if __name__ == "__main__":
    unittest.main()
