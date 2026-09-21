import unittest

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
)
from cats.cat_birth_resolver import CatBirthResolver
from cats.cat_trait_dice_mapping import (
    CatTraitDiceMappingResult,
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
        self.assertEqual(
            validation.status,
            "standard_genetics",
        )

        with self.assertRaises(TypeError):
            _ = validation["valid"]

        self.assertFalse(hasattr(validation, "get"))

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

    def test_genetic_conflict_reroll_uses_object_mapping(self):
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
            lambda die_name, rng=None: {
                "name": die_name,
                "raw_value": 1,
                "value": 1,
                "sides": 12,
            }
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

    def test_genetics_to_dict_is_detached_snapshot(self):
        profile = self._profile()
        result = CatBirthGeneticsResult(
            profile=profile,
            validation=CatGeneticsValidation(
                valid=True,
                status="standard_genetics",
                reason=None,
                karyotype="XX",
            ),
        )

        snapshot = result.to_dict()
        snapshot["profile"]["color"] = "black"
        snapshot["validation"]["status"] = "changed"
        snapshot["conflict_history"].append(
            {"attempt": 99}
        )

        self.assertEqual(result.profile.color, "white")
        self.assertEqual(
            result.validation.status,
            "standard_genetics",
        )
        self.assertEqual(result.conflict_history, ())

    def test_create_cat_rejects_legacy_genetics_dict(self):
        profile = self._profile()
        birth = {
            "profile": profile,
            "rolled_profile": profile,
            "canonical": CatCanonicalBirthResolution(
                matched=False,
                occurrence=0,
                identity=None,
                profile=profile,
                special_birth_event=None,
            ),
            "genetics": {
                "valid": True,
                "conflict_count": 0,
                "conflict_history": [],
                "cronenberg_count": 0,
            },
            "trait_dice_mapping": CatTraitDiceMappingResult(
                cat_d20_value=1,
                permutation_index=0,
                die_to_trait={},
                trait_to_die={},
            ),
            "percentile": {
                "die": "d10_percentile",
                "value": 50,
            },
        }

        self.resolver.resolve_profile = (
            lambda rng=None: birth
        )

        with self.assertRaises(TypeError):
            self.resolver.create_cat()


if __name__ == "__main__":
    unittest.main()
