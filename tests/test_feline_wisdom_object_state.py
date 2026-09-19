import unittest

from cats.feline_wisdom import (
    FelineWisdom,
)
from cats.feline_wisdom_state import (
    FelineWisdomState,
)


class DummyCat:

    def __init__(self):
        self.feline_wisdom = None


class FelineWisdomObjectStateTests(
    unittest.TestCase
):

    def test_state_has_no_mapping_api(
        self
    ):
        state = FelineWisdomState()

        self.assertFalse(
            hasattr(
                state,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                state,
                "setdefault",
            )
        )

        self.assertFalse(
            hasattr(
                state,
                "__getitem__",
            )
        )

        self.assertFalse(
            hasattr(
                state,
                "__setitem__",
            )
        )

    def test_create_state_owns_registries(
        self
    ):
        state = (
            FelineWisdom.create_state(
                can_transmit_meow=True
            )
        )

        self.assertIsInstance(
            state,
            FelineWisdomState,
        )

        self.assertTrue(
            state.can_transmit_meow
        )

        self.assertEqual(
            state.awareness,
            {},
        )

        self.assertEqual(
            state.abilities,
            {},
        )

        self.assertEqual(
            state.transmission_history,
            [],
        )

        self.assertEqual(
            state.lesson_history,
            [],
        )

    def test_ensure_state_reuses_same_object(
        self
    ):
        cat = DummyCat()

        stored = FelineWisdom.ensure_state(
            cat
        )

        current = FelineWisdom.ensure_state(
            cat,
            can_transmit_meow=True,
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertIs(
            cat.feline_wisdom,
            stored,
        )

        self.assertTrue(
            stored.can_transmit_meow
        )

    def test_legacy_mapping_state_is_rejected(
        self
    ):
        cat = DummyCat()

        cat.feline_wisdom = {
            "can_transmit_meow": False,
            "awareness": {},
            "abilities": {},
            "transmission_history": [],
            "lesson_history": [],
        }

        with self.assertRaises(
            TypeError
        ):
            FelineWisdom.ensure_state(
                cat
            )


if __name__ == "__main__":
    unittest.main()
