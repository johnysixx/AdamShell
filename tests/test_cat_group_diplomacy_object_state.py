import unittest

from cats.cat_group_cultural_conflict_system import (
    CatGroupCulturalConflictSystem,
)
from cats.cat_group_diplomacy_state import (
    CatGroupDiplomacyState,
    CatGroupMutualRelationResult,
)
from cats.cat_group_diplomacy_system import (
    CatGroupDiplomacySystem,
)
from cats.cat_group_memory_state import (
    CatGroupMemoryState,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupDiplomacyObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = (
            self.cats.create_cat(
                name="first",
                color="black",
                fur_length="short",
            )
        )

        self.second = (
            self.cats.create_cat(
                name="second",
                color="white",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        self.first_group = (
            self.groups.create_group(
                self.first,
                name="first_group",
            ).group_id
        )

        self.second_group = (
            self.groups.create_group(
                self.second,
                name="second_group",
            ).group_id
        )

        self.diplomacy = (
            CatGroupDiplomacySystem(
                self.groups
            )
        )

    def assert_not_mapping(
        self,
        value,
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
                "score"
            ]

    def test_evaluate_returns_diplomacy_state_object(
        self
    ):
        result = (
            self.diplomacy.evaluate(
                self.first_group,
                self.second_group,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupDiplomacyState,
        )

        self.assertIsInstance(
            result.memory,
            CatGroupMemoryState,
        )

        self.assertEqual(
            result.group_id,
            self.first_group,
        )

        self.assertEqual(
            result.other_group_id,
            self.second_group,
        )

        self.assert_not_mapping(
            result
        )

    def test_stored_diplomacy_is_detached_object_state(
        self
    ):
        result = (
            self.diplomacy.evaluate(
                self.first_group,
                self.second_group,
            )
        )

        stored = (
            self.groups.groups[
                self.first_group
            ].diplomacy[
                self.second_group
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupDiplomacyState,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored.memory,
            result.memory,
        )

        with self.assertRaises(
            AttributeError
        ):
            stored.score = 1.0

        self.assert_not_mapping(
            stored
        )

    def test_evaluation_memory_is_detached_from_live_group_memory(
        self
    ):
        result = (
            self.diplomacy.evaluate(
                self.first_group,
                self.second_group,
            )
        )

        live_memory = (
            self.diplomacy.memory
            .relation_memory(
                self.first_group,
                self.second_group,
            )
        )

        before = result.memory.cooperations

        live_memory.cooperations += 1

        self.assertEqual(
            result.memory.cooperations,
            before,
        )

    def test_mutual_relation_returns_typed_result(
        self
    ):
        result = (
            self.diplomacy.mutual_relation(
                self.first_group,
                self.second_group,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupMutualRelationResult,
        )

        self.assertIsInstance(
            result.first,
            CatGroupDiplomacyState,
        )

        self.assertIsInstance(
            result.second,
            CatGroupDiplomacyState,
        )

        self.assertEqual(
            result.mutual_score,
            round(
                (
                    result.first.score
                    + result.second.score
                )
                / 2.0,
                4,
            ),
        )

        self.assert_not_mapping(
            result
        )

    def test_cultural_interaction_replaces_diplomacy_object(
        self
    ):
        self.diplomacy.evaluate(
            self.first_group,
            self.second_group,
        )

        self.diplomacy.evaluate(
            self.second_group,
            self.first_group,
        )

        first = (
            self.groups.groups[
                self.first_group
            ]
        )

        before = (
            first.diplomacy[
                self.second_group
            ]
        )

        cultural_conflict = (
            CatGroupCulturalConflictSystem(
                self.groups
            )
        )

        cultural_conflict.interact(
            self.first_group,
            self.second_group,
        )

        after = (
            first.diplomacy[
                self.second_group
            ]
        )

        self.assertIsInstance(
            after,
            CatGroupDiplomacyState,
        )

        self.assertIsNot(
            after,
            before,
        )

        self.assertAlmostEqual(
            after.score,
            min(
                1.0,
                before.score + 0.05,
            ),
        )

        self.assert_not_mapping(
            after
        )


if __name__ == "__main__":
    unittest.main()
