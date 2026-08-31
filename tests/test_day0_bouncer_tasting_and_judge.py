import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)


class Day0BouncerTastingAndJudgeTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()
        registry = UniverseRegistry()

        (
            root_transition,
            layers,
            idea_universe
        ) = UniverseBootstrap(
            registry,
            self.universe
        ).run()

        from library import Library
        from gods import Gods
        from idea_entities import IdeaEntities
        from meeting_place.meeting_place import MeetingPlace
        from genesis.day0_first_bar_shift import (
            Day0FirstBarShift
        )

        self.bar = MeetingPlace(
            self.universe
        )

        self.shift = Day0FirstBarShift(
            universe=self.universe,
            meeting_place=self.bar,
            library=Library(
                self.universe
            ),
            gods=Gods(
                self.universe
            ),
            idea_entities=IdeaEntities(
                self.universe
            )
        )

        self.result = (
            self.shift
            .advance_to_bouncer_accepts_judge_role()
        )

    def test_everyone_scratches_garfield(
        self
    ):
        scratches = self.result[
            "garfield_scratches"
        ]

        self.assertEqual(
            [
                event["actor"]
                for event in scratches
            ],
            [
                "serpent",
                "lilith",
                "god",
                "bartender",
                "bouncer"
            ]
        )

        self.assertTrue(
            all(
                event["cat"] == "garfield"
                for event in scratches
            )
        )

    def test_bouncer_orders_three_tasting_drinks(
        self
    ):
        service = self.result[
            "service"
        ]

        self.assertEqual(
            [
                drink.name
                for drink in service["drinks"]
            ],
            [
                "wine",
                "mead",
                "beer"
            ]
        )

    def test_receipt_is_staff_purchase(
        self
    ):
        receipt = self.result[
            "service"
        ][
            "receipt"
        ]

        self.assertEqual(
            receipt["receipt_kind"],
            "staff_purchase"
        )

        self.assertEqual(
            receipt["message"],
            "PERSONALNI NAKUP"
        )

        self.assertIsNone(
            receipt["payment"]
        )

        self.assertEqual(
            receipt["charge"],
            0
        )

    def test_bouncer_does_not_open_guest_tab(
        self
    ):
        register = (
            self.shift
            .meeting_place
            .bar_counter
            .cash_register
        )

        self.assertNotIn(
            "bouncer",
            register.open_tabs
        )

    def test_bouncer_tastes_all_three(
        self
    ):
        tasting = self.result[
            "tasting"
        ][
            "tastings"
        ]

        self.assertEqual(
            [
                event["drink"]
                for event in tasting
            ],
            [
                "wine",
                "mead",
                "beer"
            ]
        )

    def test_bouncer_calls_them_disgusting(
        self
    ):
        verdict = self.result[
            "tasting"
        ][
            "verdict"
        ]

        self.assertEqual(
            verdict["verdict"],
            "disgusting"
        )

    def test_bouncer_accepts_judge_role(
        self
    ):
        accepted = self.result[
            "tasting"
        ][
            "accepted"
        ]

        self.assertTrue(
            accepted["accepted"]
        )

        self.assertEqual(
            accepted["role"],
            "tasting_judge"
        )


if __name__ == "__main__":
    unittest.main()
