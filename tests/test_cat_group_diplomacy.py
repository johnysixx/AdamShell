import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_memory_system import (
    CatGroupMemorySystem
)
from cats.cat_group_diplomacy_system import (
    CatGroupDiplomacySystem
)
from cats.cat_group_alliance_system import (
    CatGroupAllianceSystem
)
from cats.cat_group_conflict_system import (
    CatGroupConflictSystem
)


class CatGroupDiplomacyTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first_cat = self.cats.create_cat(
            name="first_cat",
            color="black",
            fur_length="short"
        )

        self.second_cat = self.cats.create_cat(
            name="second_cat",
            color="white",
            fur_length="short"
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                self.first_cat,
                name="first_group"
            )[
                "group_id"
            ]
        )

        self.second_group = (
            self.groups.create_group(
                self.second_cat,
                name="second_group"
            )[
                "group_id"
            ]
        )

    def test_groups_remember_conflict(
        self
    ):
        conflict = CatGroupConflictSystem(
            self.groups
        )

        conflict.resolve(
            self.first_group,
            self.second_group,
            self.cats.cats,
            resource="window"
        )

        memory = CatGroupMemorySystem(
            self.groups
        )

        first = memory.relation_memory(
            self.first_group,
            self.second_group
        )

        second = memory.relation_memory(
            self.second_group,
            self.first_group
        )

        self.assertEqual(
            first["conflicts"],
            1
        )

        self.assertEqual(
            second["conflicts"],
            1
        )

    def test_repeated_cooperation_improves_diplomacy(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        for _ in range(3):
            memory.record_cooperation(
                self.first_group,
                self.second_group,
                cooperation_type="shared_hunt"
            )

        diplomacy = CatGroupDiplomacySystem(
            self.groups
        )

        result = diplomacy.evaluate(
            self.first_group,
            self.second_group
        )

        self.assertIn(
            result["status"],
            {
                "tolerant",
                "friendly"
            }
        )

        self.assertGreater(
            result["score"],
            0.0
        )

    def test_groups_can_form_alliance_after_cooperation(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        for _ in range(3):
            memory.record_cooperation(
                self.first_group,
                self.second_group,
                cooperation_type="shared_defense"
            )

        alliances = CatGroupAllianceSystem(
            self.groups
        )

        result = alliances.propose(
            self.first_group,
            self.second_group
        )

        self.assertTrue(
            result["formed"]
        )

        self.assertIn(
            self.second_group,
            self.groups.groups[
                self.first_group
            ][
                "alliances"
            ]
        )

    def test_allied_groups_can_defend_together(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        for _ in range(3):
            memory.record_cooperation(
                self.first_group,
                self.second_group,
                cooperation_type="shared_defense"
            )

        alliances = CatGroupAllianceSystem(
            self.groups
        )

        alliances.propose(
            self.first_group,
            self.second_group
        )

        result = alliances.shared_defense(
            self.first_group,
            self.second_group,
            self.cats.cats,
            threat={
                "name": "cronenberg"
            }
        )

        self.assertTrue(
            result["defended"]
        )

    def test_betrayal_breaks_alliance_and_hurts_relation(
        self
    ):
        memory = CatGroupMemorySystem(
            self.groups
        )

        for _ in range(3):
            memory.record_cooperation(
                self.first_group,
                self.second_group,
                cooperation_type="shared_defense"
            )

        alliances = CatGroupAllianceSystem(
            self.groups
        )

        alliances.propose(
            self.first_group,
            self.second_group
        )

        result = alliances.break_alliance(
            self.first_group,
            self.second_group,
            reason="territory_seized",
            betrayal=True
        )

        self.assertTrue(
            result["broken"]
        )

        diplomacy = CatGroupDiplomacySystem(
            self.groups
        )

        relation = diplomacy.evaluate(
            self.second_group,
            self.first_group
        )

        self.assertGreaterEqual(
            relation[
                "memory"
            ][
                "betrayals"
            ],
            1
        )


if __name__ == "__main__":
    unittest.main()
