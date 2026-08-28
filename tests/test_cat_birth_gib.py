import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from universe.bootstraps.entity_bootstrap import (
    EntityBootstrap
)
from cats.cat_birth_resolver import (
    CatBirthResolver
)


class FixedGibRng:

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


class CatBirthGibTests(
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

        self.entity_bootstrap = EntityBootstrap(
            self.universe,
            self.idea_universe,
            self.root_transition
        )

        self.entity_bootstrap._create_serpent()

        self.resolver = CatBirthResolver(
            self.universe,
            self.bar
        )

    @staticmethod
    def _gib_birth():
        rolled_profile = {
            "color": "black",
            "fur_length": "short",
            "pattern": "solid",
            "eye_color": "green",
            "sex": "female"
        }

        resolved_profile = dict(
            rolled_profile
        )

        resolved_profile[
            "fur_length"
        ] = "long"

        return {
            "profile": resolved_profile,
            "rolled_profile": rolled_profile,
            "canonical": {
                "matched": True,
                "occurrence": 2,
                "identity": "gib",
                "profile": resolved_profile,
                "special_birth_event": (
                    "gib_birth_global_resonance"
                )
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
                "value": 70
            }
        }

    def test_second_canonical_birth_creates_gib(self):
        birth = self._gib_birth()

        self.resolver.resolve_profile = (
            lambda rng=None: birth
        )

        registered_names = {
            getattr(
                artifact,
                "name",
                None
            )
            for artifact in (
                self.universe
                .d20_registry
                .artifacts
            )
        }

        result = self.resolver.create_cat(
            rng=FixedGibRng()
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
            "gib"
        )

        self.assertEqual(
            cat.canonical_identity,
            "gib"
        )

        self.assertEqual(
            cat.color,
            "black"
        )

        self.assertEqual(
            cat.fur_length,
            "long"
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
            "gib",
            cat.special_traits
        )

        self.assertIn(
            "canonical_cat_gib",
            cat.special_traits
        )

        self.assertEqual(
            resonance["name"],
            "gib_birth_global_resonance"
        )

        self.assertTrue(
            resonance["triggered"]
        )

        self.assertEqual(
            set(
                resonance[
                    "d20_rotation"
                ][
                    "artifact_names"
                ]
            ),
            registered_names
        )

        self.assertIn(
            "quantum_d20",
            registered_names
        )

        self.assertIn(
            "dice_vial",
            registered_names
        )

        self.assertIn(
            "cat_d20",
            registered_names
        )

        self.assertIn(
            "serpent_d20",
            registered_names
        )

        self.assertEqual(
            resonance[
                "registered_d20_count"
            ],
            len(registered_names)
        )

        self.assertEqual(
            resonance[
                "bar_dice_count"
            ],
            6
        )

        self.assertEqual(
            {
                result["die"]
                for result in resonance[
                    "dice_box_rotation"
                ][
                    "results"
                ]
            },
            {
                "d4",
                "d6",
                "d8",
                "d10",
                "d10_percentile",
                "d12"
            }
        )

    def test_gib_resonance_is_recorded(self):
        birth = self._gib_birth()

        self.resolver.resolve_profile = (
            lambda rng=None: birth
        )

        result = self.resolver.create_cat(
            rng=FixedGibRng()
        )

        resonance = result[
            "special_birth_result"
        ]

        self.assertIn(
            resonance,
            self.universe.quantum_events
        )


if __name__ == "__main__":
    unittest.main()