import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_adult_vocalization_state import (
    CatAdultVocalizationState,
)
from cats.cat_learning import CatLearning
from cats.development_resolver import (
    CatDevelopmentResolver,
)
from cats.adult_vocalization_resolver import (
    AdultVocalizationResolver,
)


class CatAdultVocalizationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        self.resolver = (
            AdultVocalizationResolver(
                self.universe
            )
        )

        self.mother = (
            self.cats.create_cat(
                name='vocal_mother',
                color='black',
                fur_length='short',
                origin='natural_birth',
            )
        )

        self.kitten = (
            self.cats.create_cat(
                name='vocal_kitten',
                color='white',
                fur_length='short',
                origin=(
                    'kitten_birth_resolver'
                ),
            )
        )

        self.kitten.mother_name = (
            self.mother.name
        )

        self.development.initialize_newborn(
            self.kitten,
            birth_day=0,
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = (
            CatAdultVocalizationState
            .create()
        )

        for name in (
            'get',
            'setdefault',
            '__getitem__',
            '__setitem__',
            'keys',
            'values',
            'items',
            'update',
        ):
            self.assertFalse(
                hasattr(
                    state,
                    name,
                )
            )

    def test_newborn_repertoire_is_object(
        self
    ):
        state = (
            self.kitten
            .learning
            .skills['adult_meowing']
            .vocalizations
        )

        self.assertIsInstance(
            state,
            CatAdultVocalizationState,
        )

        self.assertEqual(
            state.names(),
            CatLearning.ADULT_VOCALIZATIONS,
        )

        self.assertEqual(
            state.learned_count(),
            0,
        )

    def test_manifested_cat_has_complete_object_repertoire(
        self
    ):
        state = (
            self.mother
            .learning
            .skills['adult_meowing']
            .vocalizations
        )

        self.assertIsInstance(
            state,
            CatAdultVocalizationState,
        )

        self.assertTrue(
            state.complete
        )

    def test_resolver_mutates_object_state(
        self
    ):
        state = (
            self.kitten
            .learning
            .skills['adult_meowing']
            .vocalizations
        )

        result = self.resolver.teach(
            teacher=self.mother,
            kitten=self.kitten,
            vocalization='food_request',
            current_day=60,
        )

        self.assertTrue(
            result['taught']
        )

        self.assertTrue(
            state.knows(
                'food_request'
            )
        )

        self.assertEqual(
            state.learned_count(),
            1,
        )

    def test_legacy_mapping_state_is_rejected(
        self
    ):
        skill = (
            self.kitten
            .learning
            .skills['adult_meowing']
        )

        skill.vocalizations = {
            name: False
            for name
            in CatLearning.ADULT_VOCALIZATIONS
        }

        with self.assertRaises(
            TypeError
        ):
            self.resolver.teach(
                teacher=self.mother,
                kitten=self.kitten,
                vocalization='food_request',
                current_day=60,
            )


if __name__ == '__main__':
    unittest.main()
