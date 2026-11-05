import unittest
from dataclasses import FrozenInstanceError

from cats.cat_development_stage import CatDevelopmentStage
from universe.universe import Universe
from cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver,
    CatDevelopmentStageRule,
    CatDevelopmentStageTransition,
)
from cats.reproduction import CatReproduction

class CatDevelopmentResolverTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.start_big_bang()
        self.cats = Cats(self.universe)
        self.kitten = self.cats.create_cat(name='kitten', color='black', fur_length='short', sex='female')
        self.resolver = CatDevelopmentResolver(self.universe)
        self.resolver.initialize_newborn(self.kitten, birth_day=10)

    def test_stage_thresholds_use_immutable_objects(self):
        rules = CatDevelopmentResolver.STAGES

        self.assertIsInstance(rules, tuple)
        self.assertEqual(len(rules), 6)

        self.assertEqual(
            tuple(
                (rule.minimum_age_days, rule.stage)
                for rule in rules
            ),
            (
                (0, CatDevelopmentStage.NEWBORN),
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

        for rule in rules:
            self.assertIsInstance(
                rule,
                CatDevelopmentStageRule,
            )

            for method in (
                "get",
                "keys",
                "items",
                "values",
                "to_dict",
            ):
                self.assertFalse(
                    hasattr(rule, method)
                )

            with self.assertRaises(TypeError):
                _ = rule["stage"]

        with self.assertRaises(FrozenInstanceError):
            rules[0].minimum_age_days = 999

    def test_stage_rule_rejects_invalid_values(self):
        with self.assertRaises(TypeError):
            CatDevelopmentStageRule(
                "14",
                CatDevelopmentStage.SOCIALIZING_KITTEN,
            )

        with self.assertRaises(TypeError):
            CatDevelopmentStageRule(
                True,
                CatDevelopmentStage.NEWBORN,
            )

        with self.assertRaises(ValueError):
            CatDevelopmentStageRule(
                -1,
                CatDevelopmentStage.NEWBORN,
            )

        with self.assertRaises(TypeError):
            CatDevelopmentStageRule(
                14,
                "socializing_kitten",
            )

    def test_stage_rules_preserve_transition_history(self):
        rules = CatDevelopmentResolver.STAGES

        for index, rule in enumerate(rules):
            self.assertIs(
                self.resolver.stage_for_age(
                    rule.minimum_age_days
                ),
                rule.stage,
            )

            if index > 0:
                self.assertIs(
                    self.resolver.stage_for_age(
                        rule.minimum_age_days - 1
                    ),
                    rules[index - 1].stage,
                )

        self.assertIs(
            self.resolver.stage_for_age(1000),
            CatDevelopmentStage.ADULT,
        )

        first = self.resolver._collect_transitions(
            previous_age=0,
            new_age=365,
        )

        second = self.resolver._collect_transitions(
            previous_age=0,
            new_age=365,
        )

        self.assertEqual(
            tuple(
                (event.day, event.stage)
                for event in first
            ),
            tuple(
                (rule.minimum_age_days, rule.stage)
                for rule in rules[1:]
            ),
        )

        self.assertEqual(len(first), 5)

        for event in first:
            self.assertIsInstance(
                event,
                CatDevelopmentStageTransition,
            )

        self.assertIsNot(first[0], second[0])

        with self.assertRaises(FrozenInstanceError):
            first[0].day = 999

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
