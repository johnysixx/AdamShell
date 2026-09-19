import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_navigation_offer_state import (
    CatNavigationOfferState,
)


class CatNavigationOfferObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='navigation_offer_cat',
            color='black',
            fur_length='short',
        )

    @staticmethod
    def legacy_offer():
        return {
            'name': 'cat_navigation_offered',
            'cat': 'legacy_cat',
            'suggested_intent': 'return_to_bar',
            'route_id': 'legacy_route',
            'destination': 'bar_front_door',
            'route_step_count': 1,
            'accepted': False,
            'offered': True,
        }

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatNavigationOfferState(
            suggested_intent='return_to_bar',
            route_id='route_test',
            destination='bar_front_door',
            route_step_count=3,
        )

        self.assertEqual(
            state.suggested_intent,
            'return_to_bar',
        )

        self.assertEqual(
            state.route_step_count,
            3,
        )

        self.assertFalse(
            state.accepted
        )

        self.assertFalse(
            state.declined
        )

        self.assertTrue(
            state.offered
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

        self.assertFalse(
            hasattr(
                state,
                '__setitem__',
            )
        )

    def test_producer_rejects_mapping_state(
        self
    ):
        self.cat.navigation_offer = (
            self.legacy_offer()
        )

        with self.assertRaises(
            TypeError
        ):
            self.cats.offer_navigation_for_suggested_intent(
                self.cat
            )

    def test_accept_rejects_mapping_state(
        self
    ):
        self.cat.navigation_offer = (
            self.legacy_offer()
        )

        with self.assertRaises(
            TypeError
        ):
            self.cats.accept_navigation_offer(
                self.cat
            )

    def test_decline_rejects_mapping_state(
        self
    ):
        self.cat.navigation_offer = (
            self.legacy_offer()
        )

        with self.assertRaises(
            TypeError
        ):
            self.cats.decline_navigation_offer(
                self.cat
            )

    def test_decide_rejects_mapping_state(
        self
    ):
        self.cat.navigation_offer = (
            self.legacy_offer()
        )

        with self.assertRaises(
            TypeError
        ):
            self.cats.decide_navigation_offer(
                self.cat
            )


if __name__ == '__main__':
    unittest.main()
