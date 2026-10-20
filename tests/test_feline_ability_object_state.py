import unittest

from cats.feline_ability_state import (
    FelineAbilityState,
)
from cats.feline_ability_method_state import (
    FelineAbilityMethodConstraints,
)
from cats.feline_wisdom import (
    FelineWisdom,
)
from cats.feline_wisdom_state import (
    FelineWisdomState,
)


class DummyCat:

    def __init__(self):
        self.feline_wisdom = None


class FelineAbilityObjectStateTests(
    unittest.TestCase
):

    def test_state_has_no_mapping_api(
        self
    ):
        ability = FelineAbilityState()

        self.assertFalse(
            hasattr(
                ability,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                ability,
                'setdefault',
            )
        )

        self.assertFalse(
            hasattr(
                ability,
                '__getitem__',
            )
        )

        self.assertFalse(
            hasattr(
                ability,
                '__setitem__',
            )
        )

    def test_ensure_ability_stores_object(
        self
    ):
        wisdom = FelineWisdomState()

        ability = wisdom.ensure_ability(
            'open_human_door'
        )

        self.assertIsInstance(
            ability,
            FelineAbilityState,
        )

        self.assertIs(
            wisdom.ability_record(
                'open_human_door'
            ),
            ability,
        )

        self.assertFalse(
            ability.learned
        )

        self.assertTrue(
            ability.methods.is_empty
        )

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

        self.assertFalse(
            ability.can_close
        )

    def test_learning_method_reuses_ability_object(
        self
    ):
        cat = DummyCat()

        first_method = (
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

        ability = (
            cat
            .feline_wisdom
            .ability_record(
                'open_human_door'
            )
        )

        current_id = id(
            ability
        )

        second_method = (
            FelineWisdom.learn_ability_method(
                cat=cat,
                ability_name=(
                    'open_human_door'
                ),
                method_name=(
                    'pull_with_paw'
                ),
                teacher_name=(
                    'queen_elisabeth'
                ),
                constraints=(
                    FelineAbilityMethodConstraints(
                        requires_unlocked=True,
                    )
                ),
            )
        )

        current = (
            cat
            .feline_wisdom
            .ability_record(
                'open_human_door'
            )
        )

        self.assertEqual(
            id(current),
            current_id,
        )

        self.assertTrue(
            current.learned
        )

        self.assertIs(
            current.method_record(
                'hang_on_handle'
            ),
            first_method,
        )

        self.assertIs(
            current.method_record(
                'pull_with_paw'
            ),
            second_method,
        )

    def test_store_rejects_mapping_record(
        self
    ):
        wisdom = FelineWisdomState()

        with self.assertRaises(
            TypeError
        ):
            wisdom.store_ability(
                'open_human_door',
                {
                    'learned': False,
                    'methods': {},
                    'can_close': False,
                },
            )

        self.assertTrue(
            wisdom.abilities.is_empty
        )

    def test_ability_registry_is_not_mapping(
        self
    ):
        wisdom = FelineWisdomState()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
            "__setitem__",
            "setdefault",
        ):
            self.assertFalse(
                hasattr(
                    wisdom.abilities,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = wisdom.abilities[
                'open_human_door'
            ]

        self.assertIsNone(
            wisdom.ability_record(
                'open_human_door'
            )
        )

        self.assertEqual(
            wisdom.ability_records(),
            (),
        )


if __name__ == '__main__':
    unittest.main()
