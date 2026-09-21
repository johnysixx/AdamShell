import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap,
)
from cats.cat_birth_objects import (
    CatBirthPercentileRoll,
    CatBirthPercentileResult,
)
from cats.cat_birth_resolver import CatBirthResolver


class CatBirthPercentileObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.registry = UniverseRegistry()
        self.universe = Universe()

        (
            self.root_transition,
            self.layers,
            self.idea_universe,
        ) = UniverseBootstrap(
            self.registry,
            self.universe,
        ).run()

        self.bar = self.layers.get("meeting")
        self.bar.welcome_cat_d20()

        self.resolver = CatBirthResolver(
            self.universe,
            self.bar,
        )

    def test_single_percentile_result_is_object_state(self):
        result = CatBirthPercentileResult.single(
            value=70
        )

        self.assertIsInstance(
            result,
            CatBirthPercentileResult,
        )
        self.assertIsInstance(
            result.final_roll,
            CatBirthPercentileRoll,
        )
        self.assertEqual(result.value, 70)
        self.assertEqual(result.die, "d10_percentile")
        self.assertEqual(result.reroll_count, 0)
        self.assertEqual(result.history, (result.final_roll,))

    def test_percentile_objects_have_no_mapping_compatibility(self):
        result = CatBirthPercentileResult.single(
            value=50
        )

        with self.assertRaises(TypeError):
            _ = result["value"]

        with self.assertRaises(AttributeError):
            result.get("value")

        with self.assertRaises(TypeError):
            _ = result.final_roll["value"]

        with self.assertRaises(AttributeError):
            result.final_roll.get("value")

    def test_zero_percentile_builds_object_history_and_rerolls(self):
        cronenberg = object()

        self.universe.create_cronenberg_from_quantum_error = (
            lambda *args, **kwargs: cronenberg
        )
        self.bar.dice_box.rotate_named_die = (
            lambda die_name, rng=None: {
                "die": die_name,
                "value": 40,
            }
        )

        result = self.resolver._resolve_birth_percentile(
            {
                "die": "d10_percentile",
                "value": 0,
            }
        )

        self.assertEqual(result.value, 40)
        self.assertEqual(result.reroll_count, 1)
        self.assertEqual(result.cronenberg_count, 1)
        self.assertEqual(
            result.cronenbergs_created,
            (cronenberg,),
        )
        self.assertEqual(
            tuple(item.value for item in result.history),
            (0, 40),
        )
        self.assertEqual(
            tuple(item.attempt for item in result.history),
            (1, 2),
        )
        self.assertTrue(
            all(
                isinstance(item, CatBirthPercentileRoll)
                for item in result.history
            )
        )

    def test_to_dict_is_detached_snapshot(self):
        first = CatBirthPercentileRoll(
            die="d10_percentile",
            value=0,
            attempt=1,
        )
        second = CatBirthPercentileRoll(
            die="d10_percentile",
            value=60,
            attempt=2,
        )
        result = CatBirthPercentileResult(
            final_roll=second,
            history=(first, second),
        )

        snapshot = result.to_dict()
        snapshot["final_roll"]["value"] = 10
        snapshot["history"][0]["value"] = 90
        snapshot["history"].append(
            {"value": 20}
        )

        self.assertEqual(result.value, 60)
        self.assertEqual(result.history[0].value, 0)
        self.assertEqual(len(result.history), 2)

    def test_result_rejects_legacy_history_dicts(self):
        final_roll = CatBirthPercentileRoll(
            die="d10_percentile",
            value=70,
            attempt=1,
        )

        with self.assertRaises(TypeError):
            CatBirthPercentileResult(
                final_roll=final_roll,
                history=(
                    {
                        "die": "d10_percentile",
                        "value": 70,
                        "attempt": 1,
                    },
                ),
            )


if __name__ == "__main__":
    unittest.main()
