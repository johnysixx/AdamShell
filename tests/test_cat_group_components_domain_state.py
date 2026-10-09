import unittest

from cats.cat_components import (
    CatCulture,
    CatGroupMembership,
    CatGroupRoles,
)
from cats.cat_group_role_state import (
    CatGroupRoleAssignedEvent,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatGroupComponentsDomainStateTests(
    unittest.TestCase
):

    def test_group_state_components_use_pure_domain_base(
        self
    ):
        objects = (
            CatGroupMembership(
                group_id=None,
                member=False,
            ),
            CatCulture(
                traditions={},
                myths={},
            ),
            CatGroupRoles(
                active={},
                history=[],
                role_events=0,
            ),
        )

        for value in objects:
            self.assertIsInstance(
                value,
                DomainObject,
            )

            self.assertFalse(
                hasattr(
                    value,
                    "to_dict",
                )
            )

            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
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
                    "state"
                ]

    def test_group_component_types_remain_distinct(
        self
    ):
        membership = CatGroupMembership(
            state="active",
        )

        culture = CatCulture(
            state="active",
        )

        self.assertNotEqual(
            membership,
            culture,
        )

    def test_group_roles_preserve_typed_history_behavior(
        self
    ):
        roles = CatGroupRoles(
            active={},
            history=[],
            role_events=0,
        )

        event = CatGroupRoleAssignedEvent(
            group_id="group",
            cat="cat",
            role="guardian",
            score=0.8,
        )

        result = roles.record_event(
            event
        )

        self.assertIs(
            result,
            event,
        )

        self.assertIs(
            roles.history[-1],
            event,
        )

        with self.assertRaises(
            TypeError
        ):
            roles.record_event(
                {
                    "name": "legacy_mapping",
                }
            )


if __name__ == "__main__":
    unittest.main()
