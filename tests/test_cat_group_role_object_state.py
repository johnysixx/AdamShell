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
    CatGroupRoleAssignedEvent,
    CatGroupRoleAssignmentDeniedResult,
    CatGroupRoleReleasedEvent,
    CatGroupRoleSpecializationDeniedResult,
    CatGroupRoleSpecializedEvent,
    CatGroupRoleState,
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
            ).group_id
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

    def test_role_assignment_history_uses_object_state(
        self
    ):
        self.cat.personality.traits.courage = 1.0
        self.cat.group.influence = 1.0

        result = self.roles.assign(
            self.group_id,
            self.cat,
            'guardian',
        )

        event = (
            self.cat
            .group_roles
            .history[-1]
        )

        self.assertIsInstance(
            result,
            CatGroupRoleAssignedEvent,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertEqual(
            event.role,
            'guardian',
        )

        for mapping_method in (
            'get',
            'keys',
            'items',
            'values',
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                'role'
            ]

        boundary = (
            result.to_dict()
        )

        boundary[
            'role'
        ] = 'changed'

        self.assertEqual(
            event.role,
            'guardian',
        )

        group_event = (
            self.groups
            .groups[self.group_id]
            .history[-1]
        )

        self.assertEqual(
            group_event['role'],
            'guardian',
        )

    def test_role_assignment_denial_uses_result_object(
        self
    ):
        result = self.roles.assign(
            self.group_id,
            self.cat,
            'unknown_role',
        )

        self.assertIsInstance(
            result,
            CatGroupRoleAssignmentDeniedResult,
        )

        self.assertFalse(
            result.assigned
        )

        self.assertEqual(
            result.reason,
            'unknown_role',
        )

        self.assertEqual(
            result.role,
            'unknown_role',
        )

        self.assertEqual(
            self.cat.group_roles.history,
            [],
        )

        for mapping_method in (
            'get',
            'keys',
            'items',
            'values',
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                'reason'
            ]

        boundary = (
            result.to_dict()
        )

        boundary[
            'reason'
        ] = 'changed'

        self.assertEqual(
            result.reason,
            'unknown_role',
        )

    def test_role_release_history_uses_object_state(
        self
    ):
        self.cat.personality.traits.courage = 1.0
        self.cat.group.influence = 1.0

        self.roles.assign(
            self.group_id,
            self.cat,
            'guardian',
        )

        result = self.roles.release(
            self.group_id,
            self.cat,
            'guardian',
            reason='rotation',
        )

        event = (
            self.cat
            .group_roles
            .history[-1]
        )

        self.assertIsInstance(
            result,
            CatGroupRoleReleasedEvent,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertEqual(
            event.reason,
            'rotation',
        )

        for mapping_method in (
            'get',
            'keys',
            'items',
            'values',
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                'reason'
            ]

        boundary = (
            result.to_dict()
        )

        boundary[
            'reason'
        ] = 'changed'

        self.assertEqual(
            event.reason,
            'rotation',
        )

    def test_specialization_history_uses_object_state(
        self
    ):
        self.cat.personality.traits.courage = 1.0
        self.cat.group.influence = 1.0

        self.roles.assign(
            self.group_id,
            self.cat,
            'guardian',
        )

        result = (
            self.specializations
            .specialize(
                self.group_id,
                self.cat,
                'guardian',
                'night_guardian',
            )
        )

        event = (
            self.cat
            .group_roles
            .history[-1]
        )

        self.assertIsInstance(
            result,
            CatGroupRoleSpecializedEvent,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertEqual(
            event.specialization,
            'night_guardian',
        )

        for mapping_method in (
            'get',
            'keys',
            'items',
            'values',
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                'specialization'
            ]

        boundary = (
            result.to_dict()
        )

        boundary[
            'specialization'
        ] = 'changed'

        self.assertEqual(
            event.specialization,
            'night_guardian',
        )

        group_event = (
            self.groups
            .groups[self.group_id]
            .history[-1]
        )

        self.assertEqual(
            group_event[
                'specialization'
            ],
            'night_guardian',
        )

    def test_specialization_denial_uses_result_object(
        self
    ):
        result = (
            self.specializations
            .specialize(
                self.group_id,
                self.cat,
                'guardian',
                'night_guardian',
            )
        )

        self.assertIsInstance(
            result,
            CatGroupRoleSpecializationDeniedResult,
        )

        self.assertFalse(
            result.specialized
        )

        self.assertEqual(
            result.reason,
            'base_role_not_held',
        )

        self.assertEqual(
            result.base_role,
            'guardian',
        )

        self.assertEqual(
            result.specialization,
            'night_guardian',
        )

        self.assertEqual(
            self.cat.group_roles.history,
            [],
        )

        for mapping_method in (
            'get',
            'keys',
            'items',
            'values',
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                'reason'
            ]

        boundary = (
            result.to_dict()
        )

        boundary[
            'reason'
        ] = 'changed'

        self.assertEqual(
            result.reason,
            'base_role_not_held',
        )

    def test_role_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.cat.group_roles.record_event(
                {
                    'name': 'legacy_mapping',
                }
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
