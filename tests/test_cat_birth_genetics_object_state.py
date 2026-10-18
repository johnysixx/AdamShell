import unittest

from cats.cat_genetics_validation_status import (
    CatGeneticsValidationStatus,
)

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap,
)
from cats.cat_birth_objects import (
    CatBirthProfile,
    CatCanonicalBirthResolution,
    CatBirthGeneticsResult,
    CatGeneticConflictResolution,
    CatGeneticsValidation,
    CatBirthPercentileResult,
)
from cats.cat_birth_resolver import CatBirthResolver
from cats.cat_birth_result_state import (
    CatBirthProfileResolvedEvent,
)
from cats.cat_trait_dice_mapping import (
    CatTraitDiceMappingResult,
)
from meeting_place.dice_box import (
    DiceBoxRotationEvent,
)


class CatBirthGeneticsObjectStateTests(unittest.TestCase):

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

    @staticmethod
    def _profile(**changes):
        values = {
            "color": "white",
            "fur_length": "short",
            "pattern": "solid",
            "eye_color": "green",
            "sex": "female",
        }
        values.update(changes)
        return CatBirthProfile(**values)

    def test_genetics_validator_returns_object_state(self):
        validation = self.resolver.genetics_validator.validate(
            self._profile()
        )

        self.assertIsInstance(
            validation,
            CatGeneticsValidation,
        )
        self.assertTrue(validation.valid)
        self.assertEqual(validation.karyotype, "XX")
        self.assertIs(
            validation.status,
            (
                CatGeneticsValidationStatus
                .STANDARD_GENETICS
            ),
        )

        with self.assertRaises(TypeError):
            _ = validation["valid"]

        self.assertFalse(hasattr(validation, "get"))
        self.assertFalse(
            hasattr(
                validation,
                "to_dict",
            )
        )

    def test_genetic_resolution_returns_object_state(self):
        profile = self._profile()
        mapping = CatTraitDiceMappingResult(
            cat_d20_value=1,
            permutation_index=0,
            die_to_trait={},
            trait_to_die={},
        )

        result = self.resolver._resolve_genetic_conflicts(
            profile=profile,
            rolls={},
            mapping=mapping,
        )

        self.assertIsInstance(
            result,
            CatBirthGeneticsResult,
        )
        self.assertIs(result.profile, profile)
        self.assertTrue(result.valid)
        self.assertEqual(result.conflict_count, 0)
        self.assertEqual(result.cronenberg_count, 0)
        self.assertEqual(result.conflict_history, ())

        with self.assertRaises(TypeError):
            _ = result["profile"]

        self.assertFalse(hasattr(result, "get"))
        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

    def test_genetic_conflict_reroll_uses_rotation_object(self):
        profile = self._profile(
            color="tortoiseshell",
            sex="male",
        )
        mapping = CatTraitDiceMappingResult(
            cat_d20_value=1,
            permutation_index=0,
            die_to_trait={"d12": "color"},
            trait_to_die={"color": "d12"},
        )

        self.bar.dice_box.rotate_named_die = (
            lambda die_name, rng=None:
                DiceBoxRotationEvent(
                    name=(
                        "dice_box_die_"
                        "secretly_rotated"
                    ),
                    die=die_name,
                    sides=12,
                    face_value=1,
                    percentile_tens=None,
                    raw_value=1,
                    value=1,
                    is_percentile=False,
                    location="on_bar_counter",
                    removed_from_box=False,
                    visibility=(
                        "secret_bar_dice_event"
                    ),
                    rotated=True,
                )
        )
        self.universe.create_cronenberg_from_quantum_error = (
            lambda *args, **kwargs: object()
        )

        result = self.resolver._resolve_genetic_conflicts(
            profile=profile,
            rolls={},
            mapping=mapping,
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.profile.color, "white")
        self.assertEqual(result.conflict_count, 1)
        self.assertEqual(result.cronenberg_count, 1)
        self.assertIsInstance(
            result.conflict_history[0],
            CatGeneticConflictResolution,
        )
        self.assertEqual(
            result.conflict_history[0].trait,
            "color",
        )

        reroll = (
            result
            .conflict_history[0]
            .reroll
        )

        self.assertIsInstance(
            reroll,
            DiceBoxRotationEvent,
        )

        self.assertEqual(
            reroll.die,
            "d12",
        )

        self.assertEqual(
            reroll.raw_value,
            1,
        )

        self.assertFalse(
            hasattr(
                result.conflict_history[0],
                "to_dict",
            )
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    reroll,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = reroll[
                "raw_value"
            ]

    def test_create_cat_rejects_legacy_genetics_dict(self):
        profile = self._profile()
        birth = CatBirthProfileResolvedEvent(
            profile=profile,
            rolled_profile=profile,
            canonical=CatCanonicalBirthResolution(
                matched=False,
                occurrence=0,
                identity=None,
                profile=profile,
                special_birth_event=None,
            ),
            genetics={
                "valid": True,
                "conflict_count": 0,
                "conflict_history": [],
                "cronenberg_count": 0,
            },
            trait_dice_mapping=CatTraitDiceMappingResult(
                cat_d20_value=1,
                permutation_index=0,
                die_to_trait={},
                trait_to_die={},
            ),
            percentile=(
                CatBirthPercentileResult.single(
                    value=50
                )
            ),
        )

        self.resolver.resolve_profile = (
            lambda rng=None: birth
        )

        with self.assertRaises(TypeError):
            self.resolver.create_cat()


if __name__ == "__main__":
    unittest.main()
