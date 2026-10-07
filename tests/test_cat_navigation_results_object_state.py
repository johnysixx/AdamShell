import unittest

from core.entity.components import (
    SpatialVector3,
)
from cats.cat_intention_navigation_result_state import (
    CatIntentionNavigationFailedResult,
    CatIntentionNavigationStartedEvent,
)
from cats.cat_intention_state import (
    CatIntentionCandidate,
)
from cats.cat_navigation_decision import (
    CatNavigationDecision,
)
from cats.cat_navigation_result_state import (
    CatNavigationDecisionFailedResult,
    CatNavigationNotOfferedResult,
    CatNavigationOfferedEvent,
    CatNavigationOfferAcceptedEvent,
    CatNavigationOfferDecidedEvent,
    CatNavigationOfferDeclinedEvent,
)
from cats.cats import Cats
from universe.universe import Universe


class FixedRng:

    def __init__(
        self,
        value,
    ):
        self.value = value

    def random(self):
        return self.value


class CatNavigationResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="object_navigation_cat",
            color="black",
            fur_length="short",
        )

        self.cat.position = (
            SpatialVector3(
                x=2.0,
                y=0.0,
                z=0.0,
            )
        )

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "name"
            ]

    def make_bar_offer(
        self,
    ):
        self.cat.suggested_intent = (
            "return_to_bar"
        )

        return (
            self.cats
            .offer_navigation_for_suggested_intent(
                self.cat
            )
        )

    def test_offer_result_is_object(
        self
    ):
        result = (
            self.make_bar_offer()
        )

        self.assertIsInstance(
            result,
            CatNavigationOfferedEvent,
        )

        self.assertTrue(
            result.offered
        )

        self.assertFalse(
            result.accepted
        )

        self.assertEqual(
            result.suggested_intent,
            "return_to_bar",
        )

        self.assert_object_only(
            result
        )

    def test_offer_denial_is_object(
        self
    ):
        result = (
            self.cats
            .offer_navigation_for_suggested_intent(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatNavigationNotOfferedResult,
        )

        self.assertFalse(
            result.offered
        )

        self.assertEqual(
            result.reason,
            "no_suggested_intent",
        )

        self.assert_object_only(
            result
        )

    def test_accept_result_is_object(
        self
    ):
        self.make_bar_offer()

        result = (
            self.cats
            .accept_navigation_offer(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatNavigationOfferAcceptedEvent,
        )

        self.assertTrue(
            result.accepted
        )

        self.assertEqual(
            result.route_id,
            result.route.route_id,
        )

        self.assert_object_only(
            result
        )

    def test_decline_result_is_object(
        self
    ):
        self.make_bar_offer()

        result = (
            self.cats
            .decline_navigation_offer(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatNavigationOfferDeclinedEvent,
        )

        self.assertTrue(
            result.declined
        )

        self.assertIsNotNone(
            result.route
        )

        self.assert_object_only(
            result
        )

    def test_navigation_decision_is_object_graph(
        self
    ):
        self.make_bar_offer()

        result = (
            self.cats
            .decide_navigation_offer(
                self.cat,
                rng=FixedRng(
                    0.1
                ),
                acceptance_chance=0.7,
            )
        )

        self.assertIsInstance(
            result,
            CatNavigationOfferDecidedEvent,
        )

        self.assertIs(
            result.decision,
            CatNavigationDecision.ACCEPTED,
        )

        self.assertIsInstance(
            result.result_event,
            CatNavigationOfferAcceptedEvent,
        )

        self.assertIs(
            result.route,
            result.result_event.route,
        )

        self.assert_object_only(
            result
        )

    def test_navigation_decision_failure_is_object(
        self
    ):
        result = (
            self.cats
            .decide_navigation_offer(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatNavigationDecisionFailedResult,
        )

        self.assertFalse(
            result.decided
        )

        self.assertEqual(
            result.reason,
            "no_navigation_offer",
        )

        self.assert_object_only(
            result
        )

    def test_intention_navigation_execution_is_object(
        self
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type="visit_bar",
                target=None,
                score=1.0,
                reasons=[
                    "test"
                ],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatIntentionNavigationStartedEvent,
        )

        self.assertTrue(
            result.executed
        )

        self.assertIsInstance(
            result.navigation_offer,
            CatNavigationOfferedEvent,
        )

        self.assertIsInstance(
            result.acceptance,
            CatNavigationOfferAcceptedEvent,
        )

        self.assert_object_only(
            result
        )

    def test_navigation_execution_failure_is_object(
        self
    ):
        self.cat.mind.current_intention = (
            CatIntentionCandidate(
                type="visit_recipient",
                target={
                    "recipient":
                        "legacy"
                },
                score=1.0,
                reasons=[
                    "test"
                ],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatIntentionNavigationFailedResult,
        )

        self.assertFalse(
            result.executed
        )

        self.assertEqual(
            result.reason,
            "invalid_visit_recipient_target",
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
