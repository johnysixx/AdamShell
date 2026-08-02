import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from cats.cat_birth_resolver import (
    CatBirthResolver
)


class FixedMiaRng:

    def randint(
        self,
        minimum,
        maximum
    ):
        return minimum

    def choice(
        self,
        items
    ):
        return list(items)[0]

    def random(self):
        return 0.5

    def sample(
        self,
        items,
        count
    ):
        return list(items)[:count]

    def shuffle(
        self,
        items
    ):
        return None


class CatBirthMiaTests(
    unittest.TestCase
):

    def setUp(self):
        registry = UniverseRegistry()
        self.universe = Universe()

        root, layers, idea = UniverseBootstrap(
            registry,
            self.universe
        ).run()

        self.bar = layers.get(
            "meeting"
        )

        self.bar.welcome_cat_d20()

        self.resolver = CatBirthResolver(
            self.universe,
            self.bar
        )

    def _mia_profile_result(self):
        profile = dict(
            self.resolver
            .queen_elisabeth_profile
        )

        return {
            "profile": profile,
            "rolled_profile": profile,
            "canonical": {
                "matched": True,
                "occurrence": 2,
                "identity": "mia",
                "profile": profile,
                "special_birth_event": (
                    "mia_birth_global_rotation"
                ),
                "woodoo_rebirth": False
            },
            "genetics": {
                "valid": True,
                "conflict_count": 0,
                "conflict_history": [],
                "cronenberg_count": 0
            },
            "trait_dice_mapping": {
                "cat_d20_value": 1,
                "die_to_trait": {},
                "trait_to_die": {}
            },
            "percentile": {
                "die": "d10_percentile",
                "value": 50
            }
        }

    def test_mia_rotates_all_registered_dice(self):
        self.resolver.resolve_profile = (
            lambda rng=None: (
                self._mia_profile_result()
            )
        )

        black_box_before = len(
            self.bar
            .back_room_black_box
            .entries
        )

        result = self.resolver.create_cat(
            rng=FixedMiaRng()
        )

        rotation = result[
            "special_birth_result"
        ]

        self.assertTrue(
            result["created"]
        )

        self.assertEqual(
            result["identity"],
            "mia"
        )

        self.assertEqual(
            rotation["name"],
            "mia_birth_global_rotation"
        )

        self.assertTrue(
            rotation["triggered"]
        )

        self.assertEqual(
            rotation["bar_dice_count"],
            6
        )

        self.assertEqual(
            rotation[
                "registered_d20_count"
            ],
            len(
                self.universe
                .d20_registry
                .artifacts
            )
        )

        self.assertEqual(
            len(
                rotation[
                    "dice_box_rotation"
                ]["results"]
            ),
            6
        )

        self.assertIn(
            rotation,
            self.universe.quantum_events
        )

        self.assertGreater(
            len(
                self.bar
                .back_room_black_box
                .entries
            ),
            black_box_before
        )


if __name__ == "__main__":
    unittest.main()