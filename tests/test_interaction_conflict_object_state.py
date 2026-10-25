import unittest
from types import SimpleNamespace

from core.interaction.conflict import ConflictEngine
from core.interaction.rule_engine import RuleEngine
from core.interaction.result_state import (
    InteractionConflictRecord,
    InteractionConflictResolutionResult,
    InteractionEffectValue,
)
from universe.universe import Universe


class InteractionConflictObjectStateTests(unittest.TestCase):

    def test_resolver_returns_typed_results(self):
        source = {"light": True}

        resolution = ConflictEngine().resolve([
            {"light": True, "state": source},
            {"light": False, "order": True},
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
                apply=lambda universe, word: {
                    "light": True,
                    "state": {"light": True},
                },
            ),
            SimpleNamespace(
                priority=5,
                active=True,
                apply=lambda universe, word: {
                    "light": False,
                    "birth_allowed": True,
                },
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
        result = ConflictEngine().resolve([None, {}])

        self.assertEqual(result.effects, ())
        self.assertEqual(result.conflicts, ())
        self.assertEqual(
            result.to_dict(),
            {"effects": {}, "conflicts": []},
        )


if __name__ == "__main__":
    unittest.main()
