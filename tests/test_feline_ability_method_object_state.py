import unittest

from cats.feline_ability_method_state import (
    FelineAbilityMethodConstraints,
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
                constraints=(
                    FelineAbilityMethodConstraints(
                        requires_unlocked=True,
                    )
                ),
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
            ability.method_record(
                'hang_on_handle'
            ),
            method,
        )

        self.assertEqual(
            method.teacher,
            'pazuzu',
        )

        self.assertIsInstance(
            method.constraints,
            FelineAbilityMethodConstraints,
        )

        self.assertTrue(
            method.constraints.requires_unlocked
        )

    def test_constraints_are_object_state(
        self
    ):
        cat = DummyCat()

        constraints = (
            FelineAbilityMethodConstraints(
                requires_unlocked=True,
            )
        )

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

        self.assertIs(
            method.constraints,
            constraints,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
            "__setitem__",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    method.constraints,
                    mapping_method,
                )
            )

        self.assertTrue(
            method.constraints.requires_unlocked
        )

    def test_mapping_constraints_are_rejected(
        self
    ):
        cat = DummyCat()

        with self.assertRaises(
            TypeError
        ):
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

        self.assertTrue(
            ability.methods.is_empty
        )

    def test_method_registry_is_not_mapping(
        self
    ):
        ability = FelineAbilityState()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
            "__setitem__",
        ):
            self.assertFalse(
                hasattr(
                    ability.methods,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = ability.methods[
                'hang_on_handle'
            ]

        self.assertIsNone(
            ability.method_record(
                'hang_on_handle'
            )
        )


if __name__ == '__main__':
    unittest.main()
