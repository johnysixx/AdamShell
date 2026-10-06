import unittest

from cats.cat_group_leave_state import (
    CatLeftGroupEvent,
)
from cats.cat_group_role_state import (
    CatGroupRoleSuitabilityResult,
)
from cats.cat_group_role_system import (
    CatGroupRoleSystem,
)
from cats.cat_group_succession_state import (
    CatGroupDepartureWithSuccessionResult,
    CatGroupRoleBecameVacantEvent,
    CatGroupRoleSucceededEvent,
    CatGroupSuccessionCandidate,
)
from cats.cat_group_succession_system import (
    CatGroupSuccessionSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupSuccessionObjectStateTests(
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

        self.third = self.cats.create_cat(
            name="third",
            color="gray",
            fur_length="short",
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        created = self.groups.create_group(
            self.first,
            name="bar_cats",
        )

        self.group_id = (
            created.group_id
        )

        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        self.groups.add_member(
            self.group_id,
            self.third,
            self.cats.cats,
        )

        self.roles = CatGroupRoleSystem(
            self.groups
        )

        self.succession = (
            CatGroupSuccessionSystem(
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

    def prepare_guardians(self):
        self.first.personality.traits.courage = 1.0
        self.first.group.influence = 0.8

        self.second.personality.traits.courage = 1.0
        self.second.group.influence = 0.8

        assigned = self.roles.assign(
            self.group_id,
            self.first,
            "guardian",
        )

        self.assertTrue(
            assigned.assigned
        )

    def test_role_suitability_returns_object(
        self
    ):
        self.second.personality.traits.courage = 1.0
        self.second.group.influence = 0.8

        result = self.roles.suitability(
            self.group_id,
            self.second,
            "guardian",
        )

        self.assertIsInstance(
            result,
            CatGroupRoleSuitabilityResult,
        )

        self.assertTrue(
            result.eligible
        )

        self.assertGreater(
            result.score,
            0.0,
        )

        self.assertIsNone(
            result.reason
        )

        self.assert_not_mapping(
            result,
            "score",
        )

    def test_candidates_are_typed_objects(
        self
    ):
        self.second.personality.traits.courage = 1.0
        self.second.group.influence = 0.8

        candidates = (
            self.succession.candidates(
                self.group_id,
                "guardian",
                self.cats.cats,
                exclude=[
                    self.first.name,
                ],
            )
        )

        self.assertIsInstance(
            candidates,
            tuple,
        )

        self.assertGreaterEqual(
            len(candidates),
            1,
        )

        candidate = candidates[0]

        self.assertIsInstance(
            candidate,
            CatGroupSuccessionCandidate,
        )

        self.assertIs(
            candidate.cat,
            self.second,
        )

        self.assertEqual(
            candidate.cat_name,
            self.second.name,
        )

        self.assert_not_mapping(
            candidate,
            "score",
        )

    def test_successful_succession_stores_event_objects(
        self
    ):
        self.prepare_guardians()

        result = self.succession.succeed(
            self.group_id,
            self.first,
            "guardian",
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupRoleSucceededEvent,
        )

        self.assertTrue(
            result.succeeded
        )

        self.assertEqual(
            result.successor,
            self.second.name,
        )

        group = self.groups.groups[
            self.group_id
        ]

        succession_event = (
            group.succession_history[
                -1
            ]
        )

        group_event = (
            group.history[
                -1
            ]
        )

        self.assertIsInstance(
            succession_event,
            CatGroupRoleSucceededEvent,
        )

        self.assertIsInstance(
            group_event,
            CatGroupRoleSucceededEvent,
        )

        self.assertEqual(
            succession_event,
            result,
        )

        self.assertEqual(
            group_event,
            result,
        )

        self.assertIsNot(
            succession_event,
            result,
        )

        self.assertIsNot(
            group_event,
            result,
        )

        self.assert_not_mapping(
            result,
            "succeeded",
        )

    def test_missing_successor_stores_vacant_event_object(
        self
    ):
        self.first.personality.traits.courage = 1.0
        self.first.group.influence = 0.8

        assigned = self.roles.assign(
            self.group_id,
            self.first,
            "guardian",
        )

        self.assertTrue(
            assigned.assigned
        )

        for cat in (
            self.second,
            self.third,
        ):
            cat.personality.traits.courage = 0.0
            cat.group.influence = 0.0

        result = self.succession.succeed(
            self.group_id,
            self.first,
            "guardian",
            self.cats.cats,
        )

        self.assertIsInstance(
            result,
            CatGroupRoleBecameVacantEvent,
        )

        self.assertFalse(
            result.succeeded
        )

        self.assertIsNone(
            result.successor
        )

        stored = (
            self.groups.groups[
                self.group_id
            ].succession_history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupRoleBecameVacantEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_not_mapping(
            result,
            "succeeded",
        )

    def test_departure_returns_nested_object_state(
        self
    ):
        self.prepare_guardians()

        result = (
            self.succession
            .handle_departure(
                self.group_id,
                self.first,
                self.cats.cats,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupDepartureWithSuccessionResult,
        )

        self.assertTrue(
            result.departed
        )

        self.assertIsInstance(
            result.roles,
            tuple,
        )

        self.assertEqual(
            result.roles,
            (
                "guardian",
            ),
        )

        self.assertIsInstance(
            result.successions,
            tuple,
        )

        self.assertEqual(
            len(
                result.successions
            ),
            1,
        )

        self.assertIsInstance(
            result.successions[0],
            CatGroupRoleSucceededEvent,
        )

        self.assertIsInstance(
            result.leave_result,
            CatLeftGroupEvent,
        )

        self.assertFalse(
            self.first.group.member
        )

        self.assert_not_mapping(
            result,
            "departed",
        )

        self.assert_not_mapping(
            result.successions[0],
            "succeeded",
        )

        self.assert_not_mapping(
            result.leave_result,
            "left",
        )

    def test_succession_results_are_frozen(
        self
    ):
        self.prepare_guardians()

        succeeded = (
            self.succession.succeed(
                self.group_id,
                self.first,
                "guardian",
                self.cats.cats,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            succeeded.successor = (
                "changed"
            )


if __name__ == "__main__":
    unittest.main()
