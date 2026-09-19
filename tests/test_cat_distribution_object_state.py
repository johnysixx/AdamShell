import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_distribution_state import (
    CatDistributionState,
)
from cats.cat_distribution_system import (
    CatDistributionSystem,
)


class CatDistributionObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='distribution_cat',
            color='black',
            fur_length='short',
        )

    def test_new_cat_has_object_state(
        self
    ):
        state = self.cat.distribution

        self.assertIsInstance(
            state,
            CatDistributionState,
        )

        self.assertIsNone(
            state.recipient
        )

        self.assertIsNone(
            state.status
        )

        self.assertIsNone(
            state.suggested_layer
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
                '__getitem__',
            )
        )

    def test_unassigned_path_mutates_same_object(
        self
    ):
        state = self.cat.distribution

        system = CatDistributionSystem(
            meeting_entities=[
                self.cat,
            ],
            idea_entities=[],
        )

        result = system.handle_after_milk(
            self.cat
        )

        self.assertFalse(
            result['distributed']
        )

        self.assertIs(
            self.cat.distribution,
            state,
        )

        self.assertIsNone(
            state.recipient
        )

        self.assertEqual(
            state.status,
            'unassigned',
        )

        self.assertEqual(
            state.suggested_layer,
            'idea_universe',
        )

    def test_legacy_mapping_is_rejected(
        self
    ):
        self.cat.distribution = {
            'recipient': None,
            'status': None,
            'suggested_layer': None,
        }

        system = CatDistributionSystem(
            meeting_entities=[
                self.cat,
            ],
            idea_entities=[],
        )

        with self.assertRaises(
            TypeError
        ):
            system.handle_after_milk(
                self.cat
            )


if __name__ == '__main__':
    unittest.main()
