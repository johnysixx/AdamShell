import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from cats.cat_birth_objects import (
    CatBirthProfile,
    CatCanonicalBirthResolution,
    CatBirthGeneticsResult,
    CatGeneticsValidation,
    CatBirthPercentileResult,
)
from cats.cat_birth_resolver import (
    CatBirthResolver
)
from cats.cat_trait_dice_mapping import (
    CatTraitDiceMappingResult,
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
        profile = (
            self.resolver
            .queen_elisabeth_profile
        )

        return {
            "profile": profile,
            "rolled_profile": profile,
            "canonical": (
                CatCanonicalBirthResolution(
                    matched=True,
                    occurrence=2,
                    identity="mia",
                    profile=profile,
                    special_birth_event=(
                        "mia_birth_global_rotation"
                    ),
                )
            ),
            "genetics": CatBirthGeneticsResult(
                profile=profile,
                validation=CatGeneticsValidation(
                    valid=True,
                    status="standard_genetics",
                    reason=None,
                    karyotype="XX",
                ),
            ),
            "trait_dice_mapping": (
                CatTraitDiceMappingResult(
                    cat_d20_value=1,
                    permutation_index=0,
                    die_to_trait={},
                    trait_to_die={},
                )
            ),
            "percentile": (
                CatBirthPercentileResult.single(
                    value=50
                )
            )
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