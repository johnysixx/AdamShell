import unittest

from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_group_territory_state import (
    CatGroupTerritoryClaimedEvent,
    CatGroupTerritoryClaimedResult,
)
from cats.cat_social_objects import (
    CatTerritoryClaim,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupTerritoryResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short",
        )

        self.second = self.cats.create_cat(
            name="second",
            color="white",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        created = self.groups.create_group(
            self.first,
            name="territory_group",
        )

        self.group_id = (
            created.group_id
        )

        joined = self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        self.assertTrue(
            joined.joined
        )

    def assert_not_mapping(
        self,
        value,
        key,
    ):
        for method_name in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    method_name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                key
            ]

    def claim(
        self,
        strength=0.8,
    ):
        return (
            self.groups.claim_territory(
                self.group_id,
                self.cats.cats,
                layer="meeting_place",
                location="window",
                strength=strength,
            )
        )

    def test_claim_returns_result_object(
        self
    ):
        result = self.claim()

        self.assertIsInstance(
            result,
            CatGroupTerritoryClaimedResult,
        )

        self.assertTrue(
            result.claimed
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.territory,
            "meeting_place::window",
        )

        self.assertEqual(
            result.member_count,
            2,
        )

        self.assert_not_mapping(
            result,
            "claimed",
        )

    def test_claims_are_object_tuple(
        self
    ):
        result = self.claim()

        self.assertIsInstance(
            result.claims,
            tuple,
        )

        self.assertEqual(
            len(
                result.claims
            ),
            2,
        )

        for claim in result.claims:
            self.assertIsInstance(
                claim,
                CatTerritoryClaim,
            )

        self.assertEqual(
            {
                claim.owner
                for claim in result.claims
            },
            {
                self.first.name,
                self.second.name,
            },
        )

    def test_returned_claims_are_detached_from_personal_registry(
        self
    ):
        result = self.claim()

        by_owner = {
            claim.owner: claim
            for claim in result.claims
        }

        key = (
            "meeting_place::window"
        )

        self.assertIsNot(
            by_owner[
                self.first.name
            ],
            self.first.territories.claims[
                key
            ],
        )

        self.assertIsNot(
            by_owner[
                self.second.name
            ],
            self.second.territories.claims[
                key
            ],
        )

    def test_group_history_stores_event_object(
        self
    ):
        result = self.claim()

        event = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            event,
            CatGroupTerritoryClaimedEvent,
        )

        self.assertTrue(
            event.claimed
        )

        self.assertEqual(
            event.group_id,
            result.group_id,
        )

        self.assertEqual(
            event.territory,
            result.territory,
        )

        self.assertEqual(
            event.member_count,
            result.member_count,
        )

        self.assert_not_mapping(
            event,
            "claimed",
        )

    def test_member_histories_store_detached_event_objects(
        self
    ):
        self.claim()

        first_event = (
            self.first
            .social_interactions[
                -1
            ]
        )

        second_event = (
            self.second
            .social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            first_event,
            CatGroupTerritoryClaimedEvent,
        )

        self.assertIsInstance(
            second_event,
            CatGroupTerritoryClaimedEvent,
        )

        self.assertIsNot(
            first_event,
            second_event,
        )

        self.assertEqual(
            first_event,
            second_event,
        )

    def test_result_and_event_are_frozen(
        self
    ):
        result = self.claim()

        with self.assertRaises(
            AttributeError
        ):
            result.territory = "changed"

        event = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        with self.assertRaises(
            AttributeError
        ):
            event.member_count = 0

    def test_reclaim_returns_updated_claim_snapshots(
        self
    ):
        first = self.claim(
            strength=0.6,
        )

        second = self.claim(
            strength=0.9,
        )

        self.assertTrue(
            all(
                claim.strength == 0.6
                for claim in first.claims
            )
        )

        self.assertTrue(
            all(
                claim.strength == 0.9
                for claim in second.claims
            )
        )

        self.assertTrue(
            all(
                claim.scent_marks == 1
                for claim in first.claims
            )
        )

        self.assertTrue(
            all(
                claim.scent_marks == 2
                for claim in second.claims
            )
        )


if __name__ == "__main__":
    unittest.main()
