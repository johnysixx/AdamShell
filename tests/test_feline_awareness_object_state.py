import unittest

from cats.feline_awareness_state import (
    FelineAwarenessState,
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


class FelineAwarenessObjectStateTests(
    unittest.TestCase
):

    def test_state_has_no_mapping_api(
        self
    ):
        awareness = FelineAwarenessState(
            name='open_human_door',
            domain='feline',
        )

        self.assertFalse(
            hasattr(
                awareness,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                awareness,
                '__getitem__',
            )
        )

        self.assertFalse(
            hasattr(
                awareness,
                '__setitem__',
            )
        )

        self.assertFalse(
            hasattr(
                awareness,
                'setdefault',
            )
        )

    def test_add_awareness_stores_object(
        self
    ):
        cat = DummyCat()

        stored = FelineWisdom.add_awareness(
            cat=cat,
            knowledge_name=(
                'open_human_door'
            ),
            domain='feline',
            description='door awareness',
            known_teachers=[
                'pazuzu',
            ],
        )

        self.assertIsInstance(
            stored,
            FelineAwarenessState,
        )

        self.assertIs(
            cat.feline_wisdom.awareness[
                'open_human_door'
            ],
            stored,
        )

        self.assertEqual(
            stored.domain,
            'feline',
        )

        self.assertTrue(
            stored.known_to_exist
        )

        self.assertEqual(
            stored.known_teachers,
            [
                'pazuzu',
            ],
        )

    def test_transfer_creates_distinct_object(
        self
    ):
        original = FelineAwarenessState(
            name='open_human_door',
            domain='feline',
            description='door awareness',
            known_teachers=[
                'pazuzu',
                'queen_elisabeth',
            ],
        )

        copied = original.copy_for_transfer(
            received_from='garfield',
            received_on_day=90,
        )

        self.assertIsNot(
            copied,
            original,
        )

        self.assertEqual(
            copied.name,
            original.name,
        )

        self.assertEqual(
            copied.domain,
            original.domain,
        )

        self.assertEqual(
            copied.known_teachers,
            original.known_teachers,
        )

        self.assertIsNot(
            copied.known_teachers,
            original.known_teachers,
        )

        self.assertEqual(
            copied.received_from,
            'garfield',
        )

        self.assertEqual(
            copied.received_on_day,
            90,
        )

    def test_store_rejects_mapping_record(
        self
    ):
        wisdom = FelineWisdomState()

        with self.assertRaises(
            TypeError
        ):
            wisdom.store_awareness(
                {
                    'name':
                        'open_human_door',
                    'domain':
                        'feline',
                }
            )

        self.assertEqual(
            wisdom.awareness,
            {},
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        wisdom = FelineWisdomState()

        wisdom.awareness[
            'open_human_door'
        ] = {
            'name':
                'open_human_door',
            'domain':
                'feline',
        }

        with self.assertRaises(
            TypeError
        ):
            wisdom.awareness_record(
                'open_human_door'
            )

        with self.assertRaises(
            TypeError
        ):
            list(
                wisdom.awareness_items()
            )


if __name__ == '__main__':
    unittest.main()
