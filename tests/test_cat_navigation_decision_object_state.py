import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_navigation_offer_state import (
    CatNavigationOfferState,
)
from cats.cat_navigation_decision_state import (
    CatNavigationDecisionState,
)
from cats.cat_navigation_decision import (
    CatNavigationDecision,
)
from cats.cat_navigation_result_state import (
    CatNavigationOfferDecidedEvent,
)


class FixedRng:

    def __init__(self, value):
        self.value = value

    def random(self):
        return self.value


class CatNavigationDecisionObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='decision_state_cat',
            color='black',
            fur_length='short',
        )

        self.cat.navigation_offer = (
            CatNavigationOfferState(
                suggested_intent='return_to_bar',
                route_id='route_test',
                destination='bar_front_door',
                route_step_count=1,
            )
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatNavigationDecisionState(
            route_id='route_test',
            destination='bar_front_door',
            suggested_intent='return_to_bar',
            decision_roll=0.25,
            acceptance_chance=0.7,
            decision=CatNavigationDecision.ACCEPTED,
            decided=True,
        )

        self.assertTrue(
            state.decided
        )

        self.assertIs(
            state.decision,
            CatNavigationDecision.ACCEPTED,
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

    def test_decision_is_stored_as_object(
        self
    ):
        result = (
            self.cats
            .decide_navigation_offer(
                self.cat,
                rng=FixedRng(0.25),
                acceptance_chance=0.7,
            )
        )

        state = (
            self.cat
            .last_navigation_decision
        )

        self.assertIsInstance(
            state,
            CatNavigationDecisionState,
        )

        self.assertEqual(
            state.route_id,
            'route_test',
        )

        self.assertEqual(
            state.destination,
            'bar_front_door',
        )

        self.assertEqual(
            state.suggested_intent,
            'return_to_bar',
        )

        self.assertEqual(
            state.decision_roll,
            0.25,
        )

        self.assertEqual(
            state.acceptance_chance,
            0.7,
        )

        self.assertIs(
            state.decision,
            CatNavigationDecision.ACCEPTED,
        )

        self.assertTrue(
            state.decided
        )

        self.assertIsInstance(
            result,
            CatNavigationOfferDecidedEvent,
        )

        self.assertIs(
            result.decision,
            CatNavigationDecision.ACCEPTED,
        )

    def test_string_decision_is_rejected(
        self
    ):
        with self.assertRaises(TypeError):
            CatNavigationDecisionState(
                decision="accepted",
                decided=True,
            )

    def test_legacy_mapping_state_is_rejected(
        self
    ):
        self.cat.last_navigation_decision = {
            'decision': 'accepted',
            'decided': True,
        }

        with self.assertRaises(
            TypeError
        ):
            (
                self.cats
                .decide_navigation_offer(
                    self.cat,
                    rng=FixedRng(0.25),
                )
            )


if __name__ == '__main__':
    unittest.main()
