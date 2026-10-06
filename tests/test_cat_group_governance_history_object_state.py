import unittest

from cats.cat_group_institution_establishment_state import (
    CatGroupInstitutionEstablishedEvent,
)
from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_ritual_evolution_system import (
    CatGroupRitualEvolutionSystem,
)
from cats.cat_group_ritual_performance_state import (
    CatGroupRitualPerformedEvent,
)
from cats.cat_group_ritual_system import (
    CatGroupRitualSystem,
)
from cats.cat_group_role_specialization_system import (
    CatGroupRoleSpecializationSystem,
)
from cats.cat_group_role_state import (
    CatGroupRoleAssignedEvent,
    CatGroupRoleSpecializedEvent,
)
from cats.cat_group_role_system import (
    CatGroupRoleSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_ritual_mutation_state import (
    CatGroupRitualMutatedEvent,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupGovernanceHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name="governance_first",
            color="black",
            fur_length="short",
        )

        self.second = self.cats.create_cat(
            name="governance_second",
            color="white",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.first,
                name="governance_group",
            ).group_id
        )

        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

    def assert_object_only(
        self,
        event,
    ):
        for name in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = event[
                "name"
            ]

    def test_role_assignment_group_history_is_object(
        self
    ):
        self.first.personality.traits.courage = 1.0
        self.first.group.influence = 1.0

        result = CatGroupRoleSystem(
            self.groups
        ).assign(
            self.group_id,
            self.first,
            "guardian",
        )

        stored = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupRoleAssignedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )

    def test_role_specialization_group_history_is_object(
        self
    ):
        self.first.personality.traits.courage = 1.0
        self.first.group.influence = 1.0

        CatGroupRoleSystem(
            self.groups
        ).assign(
            self.group_id,
            self.first,
            "guardian",
        )

        result = (
            CatGroupRoleSpecializationSystem(
                self.groups
            ).specialize(
                self.group_id,
                self.first,
                "guardian",
                "night_guardian",
            )
        )

        stored = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupRoleSpecializedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )

    def test_institution_establishment_history_is_object(
        self
    ):
        result = (
            CatGroupInstitutionSystem(
                self.groups
            ).establish(
                self.group_id,
                "night_watch",
                "protect_group",
                roles=[
                    "guardian"
                ],
                rituals=[],
            )
        )

        stored = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupInstitutionEstablishedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )

    def test_ritual_performance_history_is_object(
        self
    ):
        rituals = CatGroupRitualSystem(
            self.groups
        )

        rituals.define(
            self.group_id,
            "evening_patrol",
            "territory",
        )

        result = rituals.perform(
            self.group_id,
            "evening_patrol",
            [
                self.first,
                self.second,
            ],
        )

        group_event = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            group_event,
            CatGroupRitualPerformedEvent,
        )

        self.assertEqual(
            group_event,
            result,
        )

        for cat in (
            self.first,
            self.second,
        ):
            member_event = (
                cat.social_interactions[
                    -1
                ]
            )

            self.assertIsInstance(
                member_event,
                CatGroupRitualPerformedEvent,
            )

            self.assertEqual(
                member_event,
                result,
            )

            self.assertIsNot(
                member_event,
                result,
            )

        self.assert_object_only(
            group_event
        )

    def test_ritual_mutation_history_is_object(
        self
    ):
        rituals = CatGroupRitualSystem(
            self.groups
        )

        rituals.define(
            self.group_id,
            "evening_patrol",
            "territory",
        )

        result = (
            CatGroupRitualEvolutionSystem(
                self.groups
            ).mutate(
                self.group_id,
                "evening_patrol",
                "silent_patrol",
            )
        )

        stored = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupRitualMutatedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )


if __name__ == "__main__":
    unittest.main()
