import unittest

from cats.cat_group_scent_state import (
    CatGroupScentMixedEvent,
    CatGroupScentNotMixedResult,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupScentObjectStateTests(
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
            name="bar_cats",
        )

        self.group_id = (
            created.group_id
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

    def join_second(
        self
    ):
        result = self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        self.assertTrue(
            result.joined
        )

    def test_single_member_returns_not_mixed_object(
        self
    ):
        result = (
            self.groups.mix_group_scent(
                self.group_id,
                self.cats.cats,
                amount=0.2,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupScentNotMixedResult,
        )

        self.assertFalse(
            result.mixed
        )

        self.assertEqual(
            result.reason,
            "not_enough_members",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assert_not_mapping(
            result,
            "mixed",
        )

    def test_successful_mix_returns_event_object(
        self
    ):
        self.join_second()

        result = (
            self.groups.mix_group_scent(
                self.group_id,
                self.cats.cats,
                amount=0.2,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupScentMixedEvent,
        )

        self.assertTrue(
            result.mixed
        )

        self.assertEqual(
            result.members,
            (
                self.first.name,
                self.second.name,
            ),
        )

        self.assertIsInstance(
            result.members,
            tuple,
        )

        self.assertAlmostEqual(
            result.shared_scent_strength,
            0.2,
        )

        self.assert_not_mapping(
            result,
            "mixed",
        )

    def test_group_history_stores_detached_scent_event(
        self
    ):
        self.join_second()

        result = (
            self.groups.mix_group_scent(
                self.group_id,
                self.cats.cats,
                amount=0.2,
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
            CatGroupScentMixedEvent,
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
            stored,
            "mixed",
        )

    def test_member_social_history_stores_detached_scent_event(
        self
    ):
        self.join_second()

        result = (
            self.groups.mix_group_scent(
                self.group_id,
                self.cats.cats,
                amount=0.2,
            )
        )

        for cat in (
            self.first,
            self.second,
        ):
            stored = (
                cat.social_interactions[
                    -1
                ]
            )

            self.assertIsInstance(
                stored,
                CatGroupScentMixedEvent,
            )

            self.assertEqual(
                stored,
                result,
            )

            self.assertIsNot(
                stored,
                result,
            )

    def test_scent_mix_preserves_relationship_objects(
        self
    ):
        self.join_second()

        first_relation = (
            self.first.relationships[
                self.second.name
            ]
        )

        second_relation = (
            self.second.relationships[
                self.first.name
            ]
        )

        self.groups.mix_group_scent(
            self.group_id,
            self.cats.cats,
            amount=0.2,
        )

        self.assertIs(
            self.first.relationships[
                self.second.name
            ],
            first_relation,
        )

        self.assertIs(
            self.second.relationships[
                self.first.name
            ],
            second_relation,
        )

        self.assertAlmostEqual(
            first_relation.shared_scent,
            0.2,
        )

        self.assertAlmostEqual(
            second_relation.shared_scent,
            0.2,
        )

    def test_scent_results_are_frozen(
        self
    ):
        denied = (
            self.groups.mix_group_scent(
                self.group_id,
                self.cats.cats,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        self.join_second()

        mixed = (
            self.groups.mix_group_scent(
                self.group_id,
                self.cats.cats,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            mixed.shared_scent_strength = 0.0


if __name__ == "__main__":
    unittest.main()
