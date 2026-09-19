import unittest

from cats.feline_ability_state import (
    FelineAbilityState,
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
            wisdom.abilities[
                'open_human_door'
            ],
            ability,
        )

        self.assertFalse(
            ability.learned
        )

        self.assertEqual(
            ability.methods,
            {},
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
                constraints={
                    'requires_unlocked':
                        True,
                },
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
                constraints={
                    'requires_unlocked':
                        True,
                },
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
            current.methods[
                'hang_on_handle'
            ],
            first_method,
        )

        self.assertIs(
            current.methods[
                'pull_with_paw'
            ],
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

        self.assertEqual(
            wisdom.abilities,
            {},
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        wisdom = FelineWisdomState()

        wisdom.abilities[
            'open_human_door'
        ] = {
            'learned': True,
            'methods': {},
            'can_close': False,
        }

        with self.assertRaises(
            TypeError
        ):
            wisdom.ability_record(
                'open_human_door'
            )

        with self.assertRaises(
            TypeError
        ):
            wisdom.ensure_ability(
                'open_human_door'
            )

        with self.assertRaises(
            TypeError
        ):
            list(
                wisdom.ability_items()
            )


if __name__ == '__main__':
    unittest.main()
