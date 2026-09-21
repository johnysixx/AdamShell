import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from idea_universe import IdeaUniverse
from meeting_place.meeting_place import MeetingPlace
from idea_entities import IdeaEntities
from cats.cat_trait_dice_mapping import (
    CatTraitDiceMappingResult,
)


class Day0BarArrivalTests(unittest.TestCase):

    def test_new_idea_entity_arrives_at_bar_after_creation(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        idea_universe = IdeaUniverse(
            universe
        )

        meeting_place = MeetingPlace(
            universe
        )

        idea_entities = IdeaEntities(
            universe
        )

        serpent = idea_entities.create_idea_entity(
            name="serpent",
            role="primordial_serpent",
            active=True,
            existence_pct=100.0
        )

        idea_universe.add_entity(
            serpent
        )

        self.assertIn(
            serpent,
            meeting_place.entities
        )


    def test_pazuzu_birth_arrives_at_bar_during_day0(
        self
    ):
        from universe.bootstraps.universe_bootstrap import (
            UniverseBootstrap
        )
        from cats.cat_birth_objects import (
            CatBirthProfile,
            CatCanonicalBirthResolution,
            CatBirthGeneticsResult,
            CatGeneticsValidation,
        )
        from cats.cat_birth_resolver import (
            CatBirthResolver
        )

        universe = Universe()
        registry = UniverseRegistry()

        (
            root_transition,
            layers,
            idea_universe
        ) = UniverseBootstrap(
            registry,
            universe
        ).run()

        bar = layers.get(
            "meeting"
        )

        bar.welcome_cat_d20()

        resolver = CatBirthResolver(
            universe,
            bar
        )

        profile = CatBirthProfile(
            color="black",
            fur_length="short",
            pattern="solid",
            eye_color="green",
            sex="female",
        )

        birth = {
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
            "percentile": {
                "die": "d10_percentile",
                "value": 70
            }
        }

        resolver.resolve_profile = (
            lambda rng=None: birth
        )

        result = resolver.create_cat()

        pazuzu = result["cat"]

        self.assertTrue(
            result["created"]
        )

        self.assertEqual(
            pazuzu.name,
            "pazuzu"
        )

        self.assertIn(
            pazuzu,
            bar.entities
        )


if __name__ == "__main__":
    unittest.main()

