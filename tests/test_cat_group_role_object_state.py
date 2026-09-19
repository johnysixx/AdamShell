import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_role_system import (
    CatGroupRoleSystem
)
from cats.cat_group_role_specialization_system import (
    CatGroupRoleSpecializationSystem,
)
from cats.cat_group_role_state import (
    CatGroupRoleState
)


class CatGroupRoleObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='role_state_cat',
            color='black',
            fur_length='short',
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.cat,
                name='role_state_group',
            )[
                'group_id'
            ]
        )

        self.roles = CatGroupRoleSystem(
            self.groups
        )

        self.specializations = (
            CatGroupRoleSpecializationSystem(
                self.groups
            )
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatGroupRoleState(
            group_id='group',
            score=0.7,
        )

        self.assertEqual(
            state.group_id,
            'group',
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

    def test_base_role_registry_stores_and_reuses_object(
        self
    ):
        self.cat.personality.traits.courage = 1.0
        self.cat.group.influence = 1.0

        self.roles.assign(
            self.group_id,
            self.cat,
            'guardian',
        )

        stored = (
            self.cat.group_roles.active[
                'guardian'
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupRoleState,
        )

        self.roles.assign(
            self.group_id,
            self.cat,
            'guardian',
        )

        current = (
            self.cat.group_roles.active[
                'guardian'
            ]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertFalse(
            current.specialized
        )

        self.assertIsNone(
            current.base_role
        )

    def test_specialization_stores_object_record(
        self
    ):
        self.cat.personality.traits.courage = 1.0
        self.cat.group.influence = 1.0

        self.roles.assign(
            self.group_id,
            self.cat,
            'guardian',
        )

        self.specializations.specialize(
            self.group_id,
            self.cat,
            'guardian',
            'night_guardian',
        )

        state = (
            self.cat.group_roles.active[
                'night_guardian'
            ]
        )

        self.assertIsInstance(
            state,
            CatGroupRoleState,
        )

        self.assertTrue(
            state.specialized
        )

        self.assertEqual(
            state.base_role,
            'guardian',
        )

        self.assertEqual(
            state.group_id,
            self.group_id,
        )

    def test_legacy_mapping_record_is_rejected_before_holder_side_effect(
        self
    ):
        self.cat.personality.traits.courage = 1.0
        self.cat.group.influence = 1.0

        self.cat.group_roles.active[
            'guardian'
        ] = {
            'group_id': self.group_id,
            'score': 1.0,
        }

        group = self.groups.groups[
            self.group_id
        ]

        self.assertNotIn(
            'guardian',
            group.roles,
        )

        with self.assertRaises(
            TypeError
        ):
            self.roles.assign(
                self.group_id,
                self.cat,
                'guardian',
            )

        self.assertNotIn(
            'guardian',
            group.roles,
        )


if __name__ == '__main__':
    unittest.main()
