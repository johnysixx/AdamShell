import unittest

from cats.cat_development_stage import CatDevelopmentStage
from universe.universe import Universe
from cats import Cats
from cats.development_resolver import CatDevelopmentResolver
from cats.reproduction import CatReproduction

class CatDevelopmentResolverTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.start_big_bang()
        self.cats = Cats(self.universe)
        self.kitten = self.cats.create_cat(name='kitten', color='black', fur_length='short', sex='female')
        self.resolver = CatDevelopmentResolver(self.universe)
        self.resolver.initialize_newborn(self.kitten, birth_day=10)

    def test_newborn_is_not_fertile(self):
        reproduction = self.kitten.reproduction
        self.assertEqual(self.kitten.age_days, 0)
        self.assertIs(self.kitten.developmental_stage, CatDevelopmentStage.NEWBORN)
        self.assertFalse(reproduction.fertile)
        self.assertFalse(reproduction.reproductive_maturity)

    def test_developmental_stages_follow_age(self):
        expected = {
            0: CatDevelopmentStage.NEWBORN,
            13: CatDevelopmentStage.NEWBORN,
            14: CatDevelopmentStage.SOCIALIZING_KITTEN,
            48: CatDevelopmentStage.SOCIALIZING_KITTEN,
            49: CatDevelopmentStage.PLAYFUL_KITTEN,
            97: CatDevelopmentStage.PLAYFUL_KITTEN,
            98: CatDevelopmentStage.JUVENILE,
            179: CatDevelopmentStage.JUVENILE,
            180: CatDevelopmentStage.ADOLESCENT,
            364: CatDevelopmentStage.ADOLESCENT,
            365: CatDevelopmentStage.ADULT,
        }
        for age, stage in expected.items():
            with self.subTest(age=age):
                self.assertIs(self.resolver.stage_for_age(age), stage)

    def test_intact_cat_becomes_fertile_at_six_months(self):
        before = self.resolver.advance_age(self.kitten, days=179)
        self.assertFalse(before.fertile)
        maturity = self.resolver.advance_age(self.kitten, days=1)
        self.assertEqual(maturity.age_days, 180)
        self.assertIs(
            maturity.stage,
            CatDevelopmentStage.ADOLESCENT,
        )
        self.assertTrue(maturity.reproductive_maturity)
        self.assertTrue(maturity.fertile)

    def test_neutered_cat_never_becomes_fertile(self):
        self.kitten.reproduction = CatReproduction.create_state(sex='female', neutered=True)
        self.kitten.age_days = 0
        self.kitten.developmental_stage = CatDevelopmentStage.NEWBORN
        result = self.resolver.advance_age(self.kitten, days=365)
        reproduction = self.kitten.reproduction
        self.assertIs(
            result.stage,
            CatDevelopmentStage.ADULT,
        )
        self.assertTrue(reproduction.reproductive_maturity)
        self.assertFalse(reproduction.fertile)

    def test_large_age_jump_records_all_transitions(self):
        result = self.resolver.advance_age(self.kitten, days=365)
        self.assertEqual(
            tuple(
                (
                    transition.day,
                    transition.stage,
                )
                for transition
                in result.transitions
            ),
            (
                (
                    14,
                    CatDevelopmentStage.SOCIALIZING_KITTEN,
                ),
                (
                    49,
                    CatDevelopmentStage.PLAYFUL_KITTEN,
                ),
                (
                    98,
                    CatDevelopmentStage.JUVENILE,
                ),
                (
                    180,
                    CatDevelopmentStage.ADOLESCENT,
                ),
                (
                    365,
                    CatDevelopmentStage.ADULT,
                ),
            ),
        )
if __name__ == '__main__':
    unittest.main()
