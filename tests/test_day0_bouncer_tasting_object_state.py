import unittest

from core.entity.social_entity import (
    CatPettedEvent,
)
from genesis.day0_bouncer_tasting_state import (
    BartenderServesBouncerTastingDrinksEvent,
    BouncerAcceptsWagerJudgeRoleEvent,
    BouncerInitialDrinkVerdictEvent,
    BouncerJudgeAcceptanceResult,
    BouncerOrdersTastingDrinksEvent,
    BouncerTastesDrinkEvent,
    BouncerTastingServiceResult,
)
from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarDrink,
)
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap,
)
from universe.universe import Universe


class Day0BouncerTastingObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        registry = UniverseRegistry()

        UniverseBootstrap(
            registry,
            self.universe,
        ).run()

        self.scene = Day0FirstBarShift(
            universe=self.universe,
            meeting_place=MeetingPlace(
                self.universe
            ),
            library=Library(
                self.universe
            ),
            gods=Gods(
                self.universe
            ),
            idea_entities=IdeaEntities(
                self.universe
            ),
        )

        self.result = (
            self.scene
            .advance_to_bouncer_accepts_judge_role()
        )

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
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
            _ = value[key]

    def test_garfield_scratches_are_object_events(
        self
    ):
        scratches = self.result[
            "garfield_scratches"
        ]

        self.assertIsInstance(
            scratches,
            tuple,
        )

        self.assertEqual(
            len(
                scratches
            ),
            5,
        )

        self.assertTrue(
            all(
                isinstance(
                    event,
                    CatPettedEvent,
                )
                for event in scratches
            )
        )

        self.assertEqual(
            tuple(
                event.actor
                for event in scratches
            ),
            (
                "serpent",
                "lilith",
                "god",
                "bartender",
                "bouncer",
            ),
        )

        for event in scratches:
            self._assert_object_only(
                event,
                "actor",
            )

    def test_tasting_service_is_object_graph(
        self
    ):
        service = self.result[
            "service"
        ]

        self.assertIsInstance(
            service,
            BouncerTastingServiceResult,
        )

        self.assertIsInstance(
            service.receipt,
            BarReceiptState,
        )

        self.assertIsInstance(
            service.order_event,
            BouncerOrdersTastingDrinksEvent,
        )

        self.assertIsInstance(
            service.served_event,
            BartenderServesBouncerTastingDrinksEvent,
        )

        self.assertIsInstance(
            service.drinks,
            tuple,
        )

        self.assertTrue(
            all(
                isinstance(
                    drink,
                    BarDrink,
                )
                for drink in service.drinks
            )
        )

        self.assertEqual(
            tuple(
                drink.name
                for drink in service.drinks
            ),
            (
                "wine",
                "mead",
                "beer",
            ),
        )

        self._assert_object_only(
            service,
            "receipt",
        )

        self._assert_object_only(
            service.order_event,
            "drinks",
        )

        self._assert_object_only(
            service.served_event,
            "receipt_number",
        )

    def test_tasting_result_is_object_graph(
        self
    ):
        tasting = self.result[
            "tasting"
        ]

        self.assertIsInstance(
            tasting,
            BouncerJudgeAcceptanceResult,
        )

        self.assertIsInstance(
            tasting.tastings,
            tuple,
        )

        self.assertTrue(
            all(
                isinstance(
                    event,
                    BouncerTastesDrinkEvent,
                )
                for event in tasting.tastings
            )
        )

        self.assertEqual(
            tuple(
                event.drink
                for event in tasting.tastings
            ),
            (
                "wine",
                "mead",
                "beer",
            ),
        )

        self.assertIsInstance(
            tasting.verdict,
            BouncerInitialDrinkVerdictEvent,
        )

        self.assertEqual(
            tasting.verdict.verdict,
            "disgusting",
        )

        self.assertIsInstance(
            tasting.accepted,
            BouncerAcceptsWagerJudgeRoleEvent,
        )

        self.assertTrue(
            tasting.accepted.accepted
        )

        self.assertEqual(
            tasting.accepted.role,
            "tasting_judge",
        )

        self._assert_object_only(
            tasting,
            "tastings",
        )

        self._assert_object_only(
            tasting.verdict,
            "verdict",
        )

        self._assert_object_only(
            tasting.accepted,
            "accepted",
        )

    def test_service_and_tasting_share_receipt_object(
        self
    ):
        service = self.result[
            "service"
        ]

        tasting = self.result[
            "tasting"
        ]

        self.assertIs(
            tasting.receipt,
            service.receipt,
        )

        self.assertEqual(
            tasting.receipt.receipt_kind,
            "staff_purchase",
        )

        self.assertEqual(
            tasting.receipt.charge,
            0,
        )

    def test_acceptance_updates_real_wager_state(
        self
    ):
        proposal = (
            self.scene
            .serpent_lilith_drink_wager
            .tasting_panel_proposal
        )

        self.assertTrue(
            proposal.bouncer_accepted
        )

        self.assertTrue(
            self.scene
            .meeting_place
            .bouncer
            .wager_judge
        )

    def test_history_serializes_tasting_events(
        self
    ):
        names = {
            event["name"]
            for event in self.scene.history
            if isinstance(
                event,
                dict,
            )
        }

        self.assertIn(
            "bouncer_orders_tasting_drinks",
            names,
        )

        self.assertIn(
            "bartender_serves_bouncer_tasting_drinks",
            names,
        )

        self.assertIn(
            "bouncer_tastes_drink",
            names,
        )

        self.assertIn(
            "bouncer_gives_initial_drink_verdict",
            names,
        )

        self.assertIn(
            "bouncer_accepts_wager_judge_role",
            names,
        )


if __name__ == "__main__":
    unittest.main()
