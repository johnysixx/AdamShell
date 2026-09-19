import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_culture_system import (
    CatGroupCultureSystem
)
from cats.cat_cultural_adoption_system import (
    CatCulturalAdoptionSystem
)
from cats.cat_cultural_tradition_evaluation_state import (
    CatCulturalTraditionEvaluationState
)


class CatCulturalTraditionEvaluationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name='evaluation_first',
            color='black',
            fur_length='short',
        )

        self.second = self.cats.create_cat(
            name='evaluation_second',
            color='white',
            fur_length='short',
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.first,
                name='evaluation_group',
            )[
                'group_id'
            ]
        )

        self.culture = (
            CatGroupCultureSystem(
                self.groups
            )
        )

        self.adoption = (
            CatCulturalAdoptionSystem(
                self.groups
            )
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = (
            CatCulturalTraditionEvaluationState(
                group_id=self.group_id,
                score=0.8,
                category='exploration',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                'setdefault',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                '__getitem__',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                '__setitem__',
            )
        )

    def test_adoption_stores_object_record(
        self
    ):
        self.culture.practice(
            self.group_id,
            'night_patrol',
            'exploration',
            weight=0.8,
        )

        self.second.personality.traits.curiosity = 1.0

        result = (
            self.adoption.expose_to_tradition(
                self.second,
                self.group_id,
                'night_patrol',
            )
        )

        self.assertTrue(
            result['adopted']
        )

        record = (
            self.second
            .culture
            .adopted_traditions[
                'night_patrol'
            ]
        )

        self.assertIsInstance(
            record,
            CatCulturalTraditionEvaluationState,
        )

        self.assertEqual(
            record.group_id,
            self.group_id,
        )

        self.assertEqual(
            record.category,
            'exploration',
        )

        self.assertEqual(
            record.score,
            result['score'],
        )

    def test_rejection_stores_object_record(
        self
    ):
        self.culture.practice(
            self.group_id,
            'dangerous_box_jump',
            'exploration',
            weight=0.01,
        )

        self.second.personality.traits.curiosity = 0.0

        result = (
            self.adoption.expose_to_tradition(
                self.second,
                self.group_id,
                'dangerous_box_jump',
            )
        )

        self.assertFalse(
            result['adopted']
        )

        record = (
            self.second
            .culture
            .rejected_traditions[
                'dangerous_box_jump'
            ]
        )

        self.assertIsInstance(
            record,
            CatCulturalTraditionEvaluationState,
        )

        self.assertEqual(
            record.group_id,
            self.group_id,
        )

        self.assertEqual(
            record.category,
            'exploration',
        )

        self.assertEqual(
            record.score,
            result['score'],
        )

    def test_adoption_removes_previous_rejection(
        self
    ):
        self.culture.practice(
            self.group_id,
            'box_route',
            'exploration',
            weight=0.01,
        )

        self.second.personality.traits.curiosity = 0.0

        rejected = (
            self.adoption.expose_to_tradition(
                self.second,
                self.group_id,
                'box_route',
            )
        )

        self.assertFalse(
            rejected['adopted']
        )

        previous = (
            self.second
            .culture
            .rejected_traditions[
                'box_route'
            ]
        )

        self.assertIsInstance(
            previous,
            CatCulturalTraditionEvaluationState,
        )

        self.second.personality.traits.curiosity = 1.0

        self.culture.practice(
            self.group_id,
            'box_route',
            'exploration',
            weight=1.0,
        )

        adopted = (
            self.adoption.expose_to_tradition(
                self.second,
                self.group_id,
                'box_route',
            )
        )

        self.assertTrue(
            adopted['adopted']
        )

        self.assertNotIn(
            'box_route',
            self.second
            .culture
            .rejected_traditions,
        )

        current = (
            self.second
            .culture
            .adopted_traditions[
                'box_route'
            ]
        )

        self.assertIsInstance(
            current,
            CatCulturalTraditionEvaluationState,
        )

    def test_legacy_mapping_record_is_rejected_before_mutation(
        self
    ):
        self.culture.practice(
            self.group_id,
            'night_patrol',
            'exploration',
            weight=0.8,
        )

        self.second.personality.traits.curiosity = 1.0

        self.second.culture.adopted_traditions[
            'legacy'
        ] = {
            'group_id':
                self.group_id,
            'score':
                0.5,
            'category':
                'exploration',
        }

        exposures_before = (
            self.second
            .culture
            .exposures
        )

        with self.assertRaises(
            TypeError
        ):
            self.adoption.expose_to_tradition(
                self.second,
                self.group_id,
                'night_patrol',
            )

        self.assertEqual(
            self.second
            .culture
            .exposures,
            exposures_before,
        )

        self.assertNotIn(
            'night_patrol',
            self.second
            .culture
            .adopted_traditions,
        )


if __name__ == '__main__':
    unittest.main()
