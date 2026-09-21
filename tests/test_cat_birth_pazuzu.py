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


class FixedPazuzuRng:

    def randint(self, minimum, maximum):
        return min(7, maximum)

    def choice(self, items):
        return items[0]

    def random(self):
        return 0.5

    def sample(self, items, count):
        return list(items)[:count]

    def shuffle(self, items):
        return None


class CatBirthPazuzuTests(
    unittest.TestCase
):

    def setUp(self):
        self.registry = UniverseRegistry()
        self.universe = Universe()

        (
            self.root_transition,
            self.layers,
            self.idea_universe
        ) = UniverseBootstrap(
            self.registry,
            self.universe
        ).run()

        self.bar = self.layers.get(
            "meeting"
        )

        self.bar.welcome_cat_d20()

        self.resolver = CatBirthResolver(
            self.universe,
            self.bar
        )

    @staticmethod
    def _pazuzu_birth():
        profile = CatBirthProfile(
            color="black",
            fur_length="short",
            pattern="solid",
            eye_color="green",
            sex="female",
        )

        return {
            "profile": profile,
            "rolled_profile": profile,
            "canonical": (
                CatCanonicalBirthResolution(
                    matched=True,
                    occurrence=1,
                    identity="pazuzu",
                    profile=profile,
                    special_birth_event=(
                        "pazuzu_birth_dice_resonance"
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
                    value=70
                )
            )
        }

    def test_first_canonical_birth_creates_pazuzu(self):
        birth = self._pazuzu_birth()

        self.resolver.resolve_profile = (
            lambda rng=None: birth
        )

        quantum_rolls_before = (
            self.universe.quantum_die.roll_count
        )

        result = self.resolver.create_cat(
            rng=FixedPazuzuRng()
        )

        cat = result["cat"]
        resonance = result[
            "special_birth_result"
        ]

        self.assertTrue(
            result["created"]
        )

        self.assertEqual(
            cat.name,
            "pazuzu"
        )

        self.assertEqual(
            cat.canonical_identity,
            "pazuzu"
        )

        self.assertEqual(
            cat.color,
            "black"
        )

        self.assertEqual(
            cat.fur_length,
            "short"
        )

        self.assertEqual(
            cat.pattern,
            "solid"
        )

        self.assertEqual(
            cat.eye_color,
            "green"
        )

        self.assertEqual(
            cat.sex,
            "female"
        )

        self.assertIn(
            "pazuzu",
            cat.special_traits
        )

        self.assertIn(
            "canonical_cat_pazuzu",
            cat.special_traits
        )

        self.assertTrue(
            resonance["triggered"]
        )

        self.assertEqual(
            self.universe.quantum_die.roll_count,
            quantum_rolls_before + 1
        )

        self.assertTrue(
            resonance["cat_d20"]["turned"]
        )

        self.assertEqual(
            resonance["dice_vial"]["name"],
            "dice_vial_secret_rotation"
        )

        self.assertTrue(
            resonance["dice_box"]["rotated"]
        )

    def test_pazuzu_birth_resonance_remains_one_time(self):
        birth = self._pazuzu_birth()

        self.resolver.resolve_profile = (
            lambda rng=None: birth
        )

        first = self.resolver.create_cat(
            rng=FixedPazuzuRng()
        )

        second_resonance = (
            self.bar
            .trigger_pazuzu_birth_dice_resonance(
                rng=FixedPazuzuRng()
            )
        )

        self.assertTrue(
            first["special_birth_result"][
                "triggered"
            ]
        )

        self.assertTrue(
            second_resonance[
                "already_triggered"
            ]
        )


if __name__ == "__main__":
    unittest.main()