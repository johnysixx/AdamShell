import unittest
from types import SimpleNamespace

from core.interaction.conflict import ConflictEngine
from core.interaction.rule_engine import RuleEngine
from core.interaction.rules.light import LightRule
from core.interaction.rules.space import SpaceRule
from core.interaction.rules.deep import DeepRule
from core.interaction.result_state import (
    InteractionConflictRecord,
    InteractionConflictResolutionResult,
    InteractionEffectValue,
    InteractionRuleEffect,
)
from universe.universe import Universe


class InteractionConflictObjectStateTests(unittest.TestCase):

    def test_builtin_rules_return_object_effects(self):
        cases = (
            (
                LightRule(),
                "LetThereBeLight",
                {
                    "state": {"light": True},
                    "manifest": "Light",
                    "birth_allowed": True,
                },
            ),
            (
                SpaceRule(),
                "LetThereBeSpace",
                {
                    "space": True,
                    "chaos": False,
                    "order": True,
                },
            ),
            (
                DeepRule(),
                "LetThereBeDeep",
                {
                    "deep": True,
                },
            ),
        )

        for rule, word_name, expected in cases:
            with self.subTest(rule=rule.name):
                result = rule.apply(
                    None,
                    SimpleNamespace(name=word_name),
                )

                self.assertIsInstance(
                    result,
                    InteractionRuleEffect,
                )

                self.assertEqual(
                    result.rule_name,
                    rule.name,
                )

                self.assertTrue(all(
                    isinstance(
                        item,
                        InteractionEffectValue,
                    )
                    for item in result.effects
                ))

                values = {
                    item.key: item.value
                    for item in result.effects
                }

                self.assertEqual(
                    values,
                    expected,
                )

                snapshot = result.to_dict()

                self.assertEqual(
                    snapshot["rule_name"],
                    rule.name,
                )

                self.assertEqual(
                    {
                        item["key"]: item["value"]
                        for item in snapshot["effects"]
                    },
                    expected,
                )

    def test_nonmatching_rules_return_none(self):
        word = SimpleNamespace(
            name="UnknownWord",
        )

        for rule in (
            LightRule(),
            SpaceRule(),
            DeepRule(),
        ):
            with self.subTest(rule=rule.name):
                self.assertIsNone(
                    rule.apply(None, word)
                )

    def test_rule_effect_rejects_mapping_components(self):
        with self.assertRaises(TypeError):
            InteractionRuleEffect(
                rule_name="invalid",
                effects=(
                    {
                        "key": "light",
                        "value": True,
                    },
                ),
            )

        with self.assertRaises(TypeError):
            InteractionRuleEffect(
                rule_name="invalid",
                effects=(object(),),
            )

    def test_conflict_engine_rejects_legacy_effects(self):
        for legacy in (
            {"light": True},
            {},
            [],
        ):
            with self.subTest(
                legacy_type=type(legacy).__name__
            ):
                with self.assertRaises(TypeError):
                    ConflictEngine().resolve(
                        [legacy]
                    )

    def test_rule_effect_export_is_detached(self):
        source = {"light": True}

        result = InteractionRuleEffect(
            rule_name="light",
            effects=(
                InteractionEffectValue(
                    key="state",
                    value=source,
                ),
            ),
        )

        source["light"] = False

        self.assertTrue(
            result.effects[0].value["light"]
        )

        snapshot = result.to_dict()

        snapshot["effects"][0][
            "value"
        ]["light"] = False

        self.assertTrue(
            result.effects[0].value["light"]
        )

        self.assertTrue(
            result.to_dict()["effects"][0][
                "value"
            ]["light"]
        )

        with self.assertRaises(TypeError):
            _ = result["effects"]

    def test_rule_engine_accepts_builtin_object_effects(self):
        engine = RuleEngine()

        registered = []
        created = []

        universe = SimpleNamespace(
            register_conflicts=lambda conflicts:
                registered.extend(conflicts),
        )

        engine._creation = SimpleNamespace(
            apply=lambda universe, payload:
                created.append(payload),
        )

        result = engine.apply(
            universe,
            SimpleNamespace(
                name="LetThereBeLight",
            ),
        )

        self.assertIsInstance(
            result,
            InteractionConflictResolutionResult,
        )

        self.assertEqual(
            result.conflicts,
            (),
        )

        self.assertEqual(
            registered,
            [],
        )

        self.assertEqual(
            created[0],
            {
                "state": {"light": True},
                "manifest": "Light",
                "birth_allowed": True,
            },
        )

        created[0]["state"]["light"] = False

        self.assertTrue(
            result.to_dict()["effects"][
                "state"
            ]["light"]
        )

    def test_resolver_returns_typed_results(self):
        source = {"light": True}

        resolution = ConflictEngine().resolve([
            InteractionRuleEffect(
                rule_name="first",
                effects=(
                    InteractionEffectValue(
                        "light",
                        True,
                    ),
                    InteractionEffectValue(
                        "state",
                        source,
                    ),
                ),
            ),
            InteractionRuleEffect(
                rule_name="second",
                effects=(
                    InteractionEffectValue(
                        "light",
                        False,
                    ),
                    InteractionEffectValue(
                        "order",
                        True,
                    ),
                ),
            ),
        ])

        self.assertIsInstance(
            resolution,
            InteractionConflictResolutionResult,
        )
        self.assertTrue(all(
            isinstance(item, InteractionEffectValue)
            for item in resolution.effects
        ))

        self.assertEqual(
            tuple(item.key for item in resolution.effects),
            ("light", "state", "order"),
        )

        conflict = resolution.conflicts[0]

        self.assertIsInstance(
            conflict,
            InteractionConflictRecord,
        )
        self.assertEqual(conflict.key, "light")
        self.assertEqual(conflict.old, True)
        self.assertEqual(conflict.new, False)
        self.assertEqual(conflict.strength, 1)

        source["light"] = False

        snapshot = resolution.to_dict()

        self.assertEqual(
            snapshot["effects"]["state"],
            {"light": True},
        )
        self.assertFalse(
            snapshot["effects"]["light"]
        )

        snapshot["effects"]["state"]["light"] = False
        snapshot["conflicts"][0]["old"] = False

        second = resolution.to_dict()

        self.assertTrue(
            second["effects"]["state"]["light"]
        )
        self.assertTrue(
            second["conflicts"][0]["old"]
        )

        with self.assertRaises(TypeError):
            _ = resolution["effects"]

        with self.assertRaises(TypeError):
            _ = conflict["key"]

    def test_rule_engine_uses_typed_resolution(self):
        engine = RuleEngine()

        engine._rules = [
            SimpleNamespace(
                priority=10,
                active=True,
                apply=lambda universe, word: (
                    InteractionRuleEffect(
                        rule_name="first",
                        effects=(
                            InteractionEffectValue(
                                "light",
                                True,
                            ),
                            InteractionEffectValue(
                                "state",
                                {"light": True},
                            ),
                        ),
                    )
                ),
            ),
            SimpleNamespace(
                priority=5,
                active=True,
                apply=lambda universe, word: (
                    InteractionRuleEffect(
                        rule_name="second",
                        effects=(
                            InteractionEffectValue(
                                "light",
                                False,
                            ),
                            InteractionEffectValue(
                                "birth_allowed",
                                True,
                            ),
                        ),
                    )
                ),
            ),
        ]

        registered = []
        created = []

        universe = SimpleNamespace(
            register_conflicts=lambda conflicts:
                registered.extend(conflicts),
        )

        engine._creation = SimpleNamespace(
            apply=lambda universe, payload:
                created.append(payload),
        )

        result = engine.apply(
            universe,
            SimpleNamespace(name="test_word"),
        )

        self.assertIsInstance(
            result,
            InteractionConflictResolutionResult,
        )
        self.assertEqual(len(result.conflicts), 1)
        self.assertIs(
            registered[0],
            result.conflicts[0],
        )

        self.assertFalse(created[0]["light"])
        self.assertTrue(created[0]["birth_allowed"])
        self.assertEqual(
            created[0]["state"],
            {"light": True},
        )

        created[0]["state"]["light"] = False

        self.assertTrue(
            result.to_dict()["effects"]["state"]["light"]
        )

    def test_universe_conflict_history_uses_objects(self):
        universe = Universe()
        universe.threshold = 100
        universe.conflict_pressure = 1

        spawned = []

        universe.create_entity = (
            lambda name, streght=1:
                spawned.append(name)
        )

        conflict = InteractionConflictRecord(
            key="light",
            old=False,
            new=True,
        )

        universe.register_conflicts((conflict,))

        self.assertIs(
            universe.conflict_history[-1],
            conflict,
        )
        self.assertEqual(
            universe.conflict_pressure,
            2,
        )
        self.assertEqual(
            spawned,
            ["LightEcho"],
        )

    def test_universe_rejects_mapping_conflicts(self):
        universe = Universe()

        with self.assertRaises(TypeError):
            universe.register_conflicts((
                {"key": "light", "old": False, "new": True},
            ))

        self.assertEqual(
            universe.conflict_history,
            [],
        )
        self.assertEqual(
            universe.conflict_pressure,
            0,
        )

    def test_empty_conflict_resolution(self):
        result = ConflictEngine().resolve([
            None,
            InteractionRuleEffect(
                rule_name="empty",
                effects=(),
            ),
        ])

        self.assertEqual(result.effects, ())
        self.assertEqual(result.conflicts, ())
        self.assertEqual(
            result.to_dict(),
            {"effects": {}, "conflicts": []},
        )


if __name__ == "__main__":
    unittest.main()
