import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_territory_state import (
    CatGroupTerritoryState
)


class CatGroupTerritoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name='territory_first',
            color='black',
            fur_length='short',
        )

        self.second = self.cats.create_cat(
            name='territory_second',
            color='white',
            fur_length='short',
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.first,
                name='territory_group',
            )[
                'group_id'
            ]
        )

        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatGroupTerritoryState(
            layer='meeting_place',
            location='window',
            strength=0.8,
            members=[
                'first'
            ],
        )

        self.assertEqual(
            state.layer,
            'meeting_place',
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

    def test_registry_stores_object_record(
        self
    ):
        self.groups.claim_territory(
            self.group_id,
            self.cats.cats,
            layer='meeting_place',
            location='window',
            strength=0.8,
        )

        state = (
            self.groups
            .groups[self.group_id]
            .territories[
                'meeting_place::window'
            ]
        )

        self.assertIsInstance(
            state,
            CatGroupTerritoryState,
        )

        self.assertEqual(
            state.location,
            'window',
        )

        self.assertAlmostEqual(
            state.strength,
            0.8,
        )

        self.assertEqual(
            state.members,
            [
                self.first.name,
                self.second.name,
            ],
        )

    def test_reclaim_mutates_same_object(
        self
    ):
        self.groups.claim_territory(
            self.group_id,
            self.cats.cats,
            layer='meeting_place',
            location='window',
            strength=0.6,
        )

        stored = (
            self.groups
            .groups[self.group_id]
            .territories[
                'meeting_place::window'
            ]
        )

        self.groups.claim_territory(
            self.group_id,
            self.cats.cats,
            layer='meeting_place',
            location='window',
            strength=0.9,
        )

        current = (
            self.groups
            .groups[self.group_id]
            .territories[
                'meeting_place::window'
            ]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertAlmostEqual(
            stored.strength,
            0.9,
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        group = self.groups.groups[
            self.group_id
        ]

        group.territories[
            'meeting_place::window'
        ] = {
            'layer':
                'meeting_place',
            'location':
                'window',
            'strength':
                0.7,
            'members': [],
        }

        first_claim_count = len(
            self.first.territories.claims
        )

        second_claim_count = len(
            self.second.territories.claims
        )

        with self.assertRaises(
            TypeError
        ):
            self.groups.claim_territory(
                self.group_id,
                self.cats.cats,
                layer='meeting_place',
                location='window',
                strength=0.8,
            )

        self.assertEqual(
            len(
                self.first
                .territories.claims
            ),
            first_claim_count,
        )

        self.assertEqual(
            len(
                self.second
                .territories.claims
            ),
            second_claim_count,
        )


if __name__ == '__main__':
    unittest.main()
