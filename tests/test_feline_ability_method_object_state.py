import unittest

from cats.feline_ability_method_state import (
    FelineAbilityMethodState,
)
from cats.feline_ability_state import (
    FelineAbilityState,
)
from cats.feline_wisdom import (
    FelineWisdom,
)


class DummyCat:

    def __init__(self):
        self.feline_wisdom = None


class FelineAbilityMethodObjectStateTests(
    unittest.TestCase
):

    def test_state_has_no_mapping_api(
        self
    ):
        method = FelineAbilityMethodState(
            name='hang_on_handle',
            teacher='pazuzu',
        )

        self.assertFalse(
            hasattr(
                method,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                method,
                'setdefault',
            )
        )

        self.assertFalse(
            hasattr(
                method,
                '__getitem__',
            )
        )

        self.assertFalse(
            hasattr(
                method,
                '__setitem__',
            )
        )

    def test_learning_method_stores_object(
        self
    ):
        cat = DummyCat()

        method = (
            FelineWisdom.learn_ability_method(
                cat=cat,
                ability_name=(
                    'open_human_door'
                ),
                method_name=(
                    'hang_on_handle'
                ),
                teacher_name='pazuzu',
                constraints={
                    'requires_unlocked':
                        True,
                },
            )
        )

        self.assertIsInstance(
            method,
            FelineAbilityMethodState,
        )

        ability = (
            cat
            .feline_wisdom
            .ability_record(
                'open_human_door'
            )
        )

        self.assertIs(
            ability.method_record(
                'hang_on_handle'
            ),
            method,
        )

        self.assertIs(
            ability.methods[
                'hang_on_handle'
            ],
            method,
        )

        self.assertEqual(
            method.teacher,
            'pazuzu',
        )

        self.assertEqual(
            method.constraints,
            {
                'requires_unlocked':
                    True,
            },
        )

    def test_constraints_are_copied(
        self
    ):
        cat = DummyCat()

        constraints = {
            'requires_unlocked': True,
        }

        method = (
            FelineWisdom.learn_ability_method(
                cat=cat,
                ability_name=(
                    'open_human_door'
                ),
                method_name=(
                    'hang_on_handle'
                ),
                teacher_name='pazuzu',
                constraints=constraints,
            )
        )

        self.assertIsNot(
            method.constraints,
            constraints,
        )

        constraints[
            'requires_unlocked'
        ] = False

        self.assertTrue(
            method.constraints[
                'requires_unlocked'
            ]
        )

    def test_store_rejects_mapping_record(
        self
    ):
        ability = FelineAbilityState()

        with self.assertRaises(
            TypeError
        ):
            ability.store_method(
                {
                    'name':
                        'hang_on_handle',
                    'teacher':
                        'pazuzu',
                    'constraints': {},
                }
            )

        self.assertEqual(
            ability.methods,
            {},
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        ability = FelineAbilityState()

        ability.methods[
            'hang_on_handle'
        ] = {
            'name':
                'hang_on_handle',
            'teacher':
                'pazuzu',
            'constraints': {},
        }

        with self.assertRaises(
            TypeError
        ):
            ability.method_record(
                'hang_on_handle'
            )

        with self.assertRaises(
            TypeError
        ):
            list(
                ability.method_records()
            )

        with self.assertRaises(
            TypeError
        ):
            ability.method_names()


if __name__ == '__main__':
    unittest.main()
