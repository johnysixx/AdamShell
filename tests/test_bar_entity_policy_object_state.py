import unittest
from types import SimpleNamespace

from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.bar_entity_policy import (
    BarEntityPolicy,
)
from meeting_place.bar_entity_policy_state import (
    BarEntityPolicyDecision,
)
from meeting_place.glass_shelf import (
    GlassShelf,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)


class BarEntityPolicyObjectStateTests(
    unittest.TestCase
):

    def assert_not_mapping(
        self,
        state,
    ):
        for name in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
            "__getitem__",
            "__setitem__",
        ):
            self.assertFalse(
                hasattr(
                    state,
                    name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = state[
                "glass_mode"
            ]

    def test_policy_returns_object_state(
        self
    ):
        policy = BarEntityPolicy()

        decision = policy.resolve(
            profile={
                "name": "serpent",
                "type": "idea_entity",
            },
            technical_name="serpent",
        )

        self.assertIsInstance(
            decision,
            BarEntityPolicyDecision,
        )

        self.assertEqual(
            decision.entity_id,
            "serpent",
        )

        self.assertEqual(
            decision.entity_class,
            "special_idea_entity",
        )

        self.assertEqual(
            decision.access_mode,
            "automatic",
        )

        self.assertEqual(
            decision.glass_mode,
            "personal_named",
        )

        self.assertEqual(
            decision.service_mode,
            "standard",
        )

        self.assert_not_mapping(
            decision
        )

    def test_glass_shelf_consumes_policy_object(
        self
    ):
        policy = BarEntityPolicy()
        shelf = GlassShelf()

        decision = policy.resolve(
            profile={
                "name": "newton",
                "type": "idea_entity",
            },
            technical_name="newton",
        )

        glass = (
            shelf
            .register_policy_decision(
                decision
            )
        )

        self.assertEqual(
            decision.entity_class,
            "common_idea_entity",
        )

        self.assertEqual(
            decision.glass_mode,
            "reserved_unnamed",
        )

        self.assertIs(
            shelf.reserved_glasses[0],
            glass,
        )

        self.assertEqual(
            glass.reserved_for,
            "newton",
        )

        with self.assertRaises(
            TypeError
        ):
            shelf.register_policy_decision(
                {
                    "entity_id":
                        "legacy",
                    "glass_mode":
                        "shared",
                }
            )

    def test_universe_stores_policy_object_on_entity(
        self
    ):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        meeting_place = (
            MeetingPlace(
                universe
            )
        )

        entity = SimpleNamespace(
            name="serpent",
            type="idea_entity",
            profile={
                "name": "serpent",
                "type": "idea_entity",
            },
        )

        universe.add_entity(
            entity
        )

        self.assertIsInstance(
            entity.bar_policy,
            BarEntityPolicyDecision,
        )

        self.assertEqual(
            entity
            .bar_policy
            .glass_mode,
            "personal_named",
        )

        self.assertIn(
            "serpent",
            meeting_place
            .glass_shelf
            .personal_glasses,
        )

        glass = (
            meeting_place
            .glass_shelf
            .personal_glasses[
                "serpent"
            ]
        )

        self.assertEqual(
            glass.owner,
            "serpent",
        )

        self.assert_not_mapping(
            entity.bar_policy
        )


if __name__ == "__main__":
    unittest.main()
