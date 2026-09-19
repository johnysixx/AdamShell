import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_ritual_system import (
    CatGroupRitualSystem
)
from cats.cat_group_ritual_evolution_system import (
    CatGroupRitualEvolutionSystem
)
from cats.cat_ritual_lineage_state import (
    CatRitualLineageState
)


class CatRitualLineageObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='lineage_cat',
            color='black',
            fur_length='short',
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.cat,
                name='lineage_group',
            )[
                'group_id'
            ]
        )

        self.rituals = (
            CatGroupRitualSystem(
                self.groups
            )
        )

        self.evolution = (
            CatGroupRitualEvolutionSystem(
                self.groups
            )
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatRitualLineageState(
            root_ritual='night_watch'
        )

        self.assertEqual(
            state.root_ritual,
            'night_watch',
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

    def test_register_origin_stores_object_record(
        self
    ):
        self.rituals.define(
            self.group_id,
            'night_watch',
            'territory',
        )

        state = (
            self.groups
            .groups[self.group_id]
            .ritual_lineages[
                'night_watch'
            ]
        )

        self.assertIsInstance(
            state,
            CatRitualLineageState,
        )

        self.assertEqual(
            state.root_ritual,
            'night_watch',
        )

        self.assertEqual(
            state.versions,
            [
                'night_watch'
            ],
        )

    def test_mutation_preserves_same_lineage_object(
        self
    ):
        self.rituals.define(
            self.group_id,
            'night_watch',
            'territory',
        )

        stored = (
            self.groups
            .groups[self.group_id]
            .ritual_lineages[
                'night_watch'
            ]
        )

        self.evolution.mutate(
            self.group_id,
            'night_watch',
            'silent_watch',
        )

        current = (
            self.groups
            .groups[self.group_id]
            .ritual_lineages[
                'night_watch'
            ]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertIn(
            'silent_watch',
            current.versions,
        )

        self.assertEqual(
            current.children[
                'night_watch'
            ],
            [
                'silent_watch'
            ],
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        self.rituals.define(
            self.group_id,
            'night_watch',
            'territory',
        )

        self.groups.groups[
            self.group_id
        ].ritual_lineages[
            'night_watch'
        ] = {
            'root_ritual':
                'night_watch',
            'versions': [
                'night_watch'
            ],
            'children': {},
        }

        with self.assertRaises(
            TypeError
        ):
            self.evolution.lineage(
                self.group_id,
                'night_watch',
            )


if __name__ == '__main__':
    unittest.main()
