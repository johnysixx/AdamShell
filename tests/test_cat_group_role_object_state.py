import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_group_role_system import (
    CatGroupRoleSystem,
)
from cats.cat_group_role_registry import (
    CatGroupRoleHolderRecord,
    CatGroupRoleRegistry,
    CatGroupRoleSpecializationRecord,
    CatGroupRoleSpecializationRegistry,
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
            name="role_state_cat",
            color="black",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.cat,
                name="role_state_group",
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
            "to_dict",
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

    def prepare_guardian(
        self
    ):
        self.cat.personality.traits.courage = 1.0
        self.cat.group.influence = 1.0

        return self.roles.assign(
            self.group_id,
            self.cat,
            "guardian",
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatGroupRoleState(
            role="guardian",
            group_id="group",
            score=0.7,
        )

        self.assertEqual(
            state.role,
            "guardian",
        )

        self.assertEqual(
            state.group_id,
            "group",
        )

        self.assertFalse(
            hasattr(
                state,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                state,
                "__getitem__",
            )
        )

    def test_role_registry_has_no_mapping_api(
        self
    ):
        registry = self.cat.group_roles

        self.assertTrue(
            registry.is_empty
        )

        self.assertEqual(
            registry.count,
            0,
        )

        self.assertEqual(
            registry.records(),
            (),
        )

        self.assertEqual(
            registry.roles(),
            (),
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "pop",
            "setdefault",
            "clear",
            "__getitem__",
            "__setitem__",
            "__contains__",
        ):
            self.assertFalse(
                hasattr(
                    registry,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            registry.store(
                {
                    "role": "guardian",
                }
            )

        with self.assertRaises(
            ValueError
        ):
            registry.store(
                CatGroupRoleState()
            )

    def test_group_role_registries_have_no_mapping_api(
        self
    ):
        group = self.groups.groups[
            self.group_id
        ]

        self.assertIsInstance(
            group.roles,
            CatGroupRoleRegistry,
        )

        self.assertIsInstance(
            group.role_specializations,
            CatGroupRoleSpecializationRegistry,
        )

        for registry in (
            group.roles,
            group.role_specializations,
        ):
            self.assertTrue(
                registry.is_empty
            )

            self.assertEqual(
                registry.count,
                0,
            )

            self.assertEqual(
                registry.records(),
                (),
            )

            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
                "pop",
                "setdefault",
                "clear",
                "__getitem__",
                "__setitem__",
                "__contains__",
                "__iter__",
            ):
                self.assertFalse(
                    hasattr(
                        registry,
                        mapping_method,
                    )
                )

        with self.assertRaises(
            TypeError
        ):
            group.roles.store(
                {
                    "role": "guardian",
                }
            )

        with self.assertRaises(
            TypeError
        ):
            group.role_specializations.store(
                {
                    "base_role": "guardian",
                    "specialization":
                        "night_guardian",
                }
            )

    def test_group_role_holder_record_is_object_state(
        self
    ):
        record = CatGroupRoleHolderRecord(
            role="guardian"
        )

        record.add_holder(
            self.cat.name
        )

        self.assertEqual(
            record.holder_names(),
            (
                self.cat.name,
            ),
        )

        self.assertFalse(
            hasattr(
                record,
                "get",
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = record[
                "role"
            ]

    def test_group_role_specialization_record_is_object_state(
        self
    ):
        record = (
            CatGroupRoleSpecializationRecord(
                base_role="guardian",
                specialization=
                    "night_guardian",
            )
        )

        record.add_holder(
            self.cat.name
        )

        self.assertEqual(
            record.holder_names(),
            (
                self.cat.name,
            ),
        )

        self.assertFalse(
            hasattr(
                record,
                "get",
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = record[
                "specialization"
            ]

    def test_base_role_registry_stores_and_reuses_object(
        self
    ):
        self.prepare_guardian()

        stored = (
            self.cat.group_roles.record(
                "guardian"
            )
        )

        self.assertIsInstance(
            stored,
            CatGroupRoleState,
        )

        self.roles.assign(
            self.group_id,
            self.cat,
            "guardian",
        )

        current = (
            self.cat.group_roles.record(
                "guardian"
            )
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
        self.prepare_guardian()

        self.specializations.specialize(
            self.group_id,
            self.cat,
            "guardian",
            "night_guardian",
        )

        state = (
            self.cat.group_roles.record(
                "night_guardian"
            )
        )

        self.assertIsInstance(
            state,
            CatGroupRoleState,
        )

        self.assertTrue(
            state.specialized
        )

        self.assertEqual(
            state.role,
            "night_guardian",
        )

        self.assertEqual(
            state.base_role,
            "guardian",
        )

    def test_role_assignment_history_is_object_everywhere(
        self
    ):
        result = self.prepare_guardian()

        cat_event = (
            self.cat.group_roles.history[
                -1
            ]
        )

        group_event = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatGroupRoleAssignedEvent,
        )

        self.assertIs(
            cat_event,
            result,
        )

        self.assertIsInstance(
            group_event,
            CatGroupRoleAssignedEvent,
        )

        self.assertEqual(
            group_event,
            result,
        )

        self.assertIsNot(
            group_event,
            result,
        )

        self.assertEqual(
            group_event.role,
            "guardian",
        )

        self.assert_not_mapping(
            result,
            "role",
        )

        self.assert_not_mapping(
            group_event,
            "role",
        )

    def test_role_assignment_denial_uses_pure_object(
        self
    ):
        result = self.roles.assign(
            self.group_id,
            self.cat,
            "unknown_role",
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
            "unknown_role",
        )

        self.assertEqual(
            self.cat.group_roles.history,
            [],
        )

        self.assert_not_mapping(
            result,
            "reason",
        )

    def test_role_release_history_uses_pure_object(
        self
    ):
        self.prepare_guardian()

        result = self.roles.release(
            self.group_id,
            self.cat,
            "guardian",
            reason="rotation",
        )

        event = (
            self.cat.group_roles.history[
                -1
            ]
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
            "rotation",
        )

        self.assert_not_mapping(
            result,
            "reason",
        )

    def test_specializations_query_returns_object_records(
        self
    ):
        self.prepare_guardian()

        self.specializations.specialize(
            self.group_id,
            self.cat,
            "guardian",
            "night_guardian",
        )

        result = (
            self.specializations.specializations(
                self.group_id,
                "guardian",
            )
        )

        self.assertIsInstance(
            result,
            tuple,
        )

        self.assertEqual(
            len(result),
            1,
        )

        record = result[0]

        self.assertIsInstance(
            record,
            CatGroupRoleSpecializationRecord,
        )

        self.assertEqual(
            record.base_role,
            "guardian",
        )

        self.assertEqual(
            record.specialization,
            "night_guardian",
        )

        self.assertEqual(
            record.holder_names(),
            (
                self.cat.name,
            ),
        )

        stored = (
            self.groups.groups[
                self.group_id
            ].role_specializations.record(
                "guardian",
                "night_guardian",
            )
        )

        self.assertIsNot(
            record,
            stored,
        )

    def test_specialization_history_is_object_everywhere(
        self
    ):
        self.prepare_guardian()

        result = (
            self.specializations.specialize(
                self.group_id,
                self.cat,
                "guardian",
                "night_guardian",
            )
        )

        cat_event = (
            self.cat.group_roles.history[
                -1
            ]
        )

        group_event = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatGroupRoleSpecializedEvent,
        )

        self.assertIs(
            cat_event,
            result,
        )

        self.assertIsInstance(
            group_event,
            CatGroupRoleSpecializedEvent,
        )

        self.assertEqual(
            group_event,
            result,
        )

        self.assertIsNot(
            group_event,
            result,
        )

        self.assertEqual(
            group_event.specialization,
            "night_guardian",
        )

        self.assert_not_mapping(
            result,
            "specialization",
        )

        self.assert_not_mapping(
            group_event,
            "specialization",
        )

    def test_specialization_denial_uses_pure_object(
        self
    ):
        result = (
            self.specializations.specialize(
                self.group_id,
                self.cat,
                "guardian",
                "night_guardian",
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
            "base_role_not_held",
        )

        self.assertEqual(
            self.cat.group_roles.history,
            [],
        )

        self.assert_not_mapping(
            result,
            "reason",
        )

    def test_role_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            self.cat.group_roles.record_event(
                {
                    "name": "legacy_mapping",
                }
            )

    def test_legacy_mapping_record_is_rejected_before_holder_side_effect(
        self
    ):
        group = self.groups.groups[
            self.group_id
        ]

        self.assertFalse(
            group.roles.has(
                "guardian"
            )
        )

        with self.assertRaises(
            TypeError
        ):
            self.cat.group_roles.store(
                {
                    "role": "guardian",
                    "group_id": self.group_id,
                    "score": 1.0,
                }
            )

        self.assertFalse(
            self.cat.group_roles.has(
                "guardian"
            )
        )

        self.assertFalse(
            group.roles.has(
                "guardian"
            )
        )


if __name__ == "__main__":
    unittest.main()
