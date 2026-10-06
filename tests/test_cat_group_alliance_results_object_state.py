import unittest

from cats.cat_group_alliance_break_state import (
    CatGroupAllianceBreakDeniedResult,
    CatGroupAllianceBrokenEvent,
)
from cats.cat_group_alliance_defense_state import (
    CatGroupAlliedDefenseDeniedResult,
    CatGroupAlliedDefenseResult,
)
from cats.cat_group_alliance_proposal_state import (
    CatGroupAllianceDeniedResult,
    CatGroupAllianceFormedEvent,
    CatGroupAlliancePreservedResult,
)
from cats.cat_group_alliance_system import (
    CatGroupAllianceSystem,
)
from cats.cat_group_memory_system import (
    CatGroupMemorySystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_group_threat_state import (
    CatGroupThreatResponseEvent,
    CatGroupThreatState,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupAllianceResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first_cat = (
            self.cats.create_cat(
                name="first_cat",
                color="black",
                fur_length="short",
            )
        )

        self.second_cat = (
            self.cats.create_cat(
                name="second_cat",
                color="white",
                fur_length="short",
            )
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                self.first_cat,
                name="first_group",
            )[
                "group_id"
            ]
        )

        self.second_group = (
            self.groups.create_group(
                self.second_cat,
                name="second_group",
            )[
                "group_id"
            ]
        )

        self.alliances = (
            CatGroupAllianceSystem(
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
                "name"
            ]

    def prepare_alliance(self):
        memory = (
            CatGroupMemorySystem(
                self.groups
            )
        )

        for _ in range(3):
            memory.record_cooperation(
                self.first_group,
                self.second_group,
                cooperation_type=(
                    "shared_defense"
                ),
            )

        return self.alliances.propose(
            self.first_group,
            self.second_group,
        )

    def test_same_group_proposal_returns_denied_object(
        self
    ):
        result = self.alliances.propose(
            self.first_group,
            self.first_group,
        )

        self.assertIsInstance(
            result,
            CatGroupAllianceDeniedResult,
        )

        self.assertFalse(
            result.formed
        )

        self.assertEqual(
            result.reason,
            "same_group",
        )

        self.assertIsNone(
            result.relation
        )

        self.assert_not_mapping(
            result
        )

    def test_requirements_failure_returns_denied_object(
        self
    ):
        result = self.alliances.propose(
            self.first_group,
            self.second_group,
        )

        self.assertIsInstance(
            result,
            CatGroupAllianceDeniedResult,
        )

        self.assertFalse(
            result.formed
        )

        self.assertEqual(
            result.reason,
            "alliance_requirements_not_met",
        )

        self.assertIsNotNone(
            result.relation
        )

        self.assert_not_mapping(
            result
        )

    def test_successful_proposal_returns_formed_event(
        self
    ):
        result = (
            self.prepare_alliance()
        )

        self.assertIsInstance(
            result,
            CatGroupAllianceFormedEvent,
        )

        self.assertTrue(
            result.formed
        )

        self.assertIn(
            self.second_group,
            self.groups.groups[
                self.first_group
            ].alliances,
        )

        self.assert_not_mapping(
            result
        )

    def test_existing_alliance_returns_preserved_object(
        self
    ):
        self.prepare_alliance()

        result = self.alliances.propose(
            self.first_group,
            self.second_group,
        )

        self.assertIsInstance(
            result,
            CatGroupAlliancePreservedResult,
        )

        self.assertTrue(
            result.formed
        )

        self.assertTrue(
            result.existing
        )

        self.assert_not_mapping(
            result
        )

    def test_formed_event_history_stores_objects(
        self
    ):
        result = (
            self.prepare_alliance()
        )

        first_history = (
            self.groups.groups[
                self.first_group
            ].history[
                -1
            ]
        )

        second_history = (
            self.groups.groups[
                self.second_group
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            first_history,
            CatGroupAllianceFormedEvent,
        )

        self.assertIsInstance(
            second_history,
            CatGroupAllianceFormedEvent,
        )

        self.assertEqual(
            first_history,
            result,
        )

        self.assertEqual(
            second_history,
            result,
        )

        self.assertIsNot(
            first_history,
            result,
        )

        self.assertIsNot(
            second_history,
            result,
        )

        self.assert_not_mapping(
            first_history
        )

    def test_shared_defense_denial_returns_object(
        self
    ):
        result = (
            self.alliances.shared_defense(
                self.first_group,
                self.second_group,
                self.cats.cats,
                threat=CatGroupThreatState(
                    name="cronenberg"
                ),
            )
        )

        self.assertIsInstance(
            result,
            CatGroupAlliedDefenseDeniedResult,
        )

        self.assertFalse(
            result.defended
        )

        self.assertEqual(
            result.reason,
            "groups_not_allied",
        )

        self.assert_not_mapping(
            result
        )

    def test_shared_defense_contains_threat_response_objects(
        self
    ):
        self.prepare_alliance()

        result = (
            self.alliances.shared_defense(
                self.first_group,
                self.second_group,
                self.cats.cats,
                threat=CatGroupThreatState(
                    name="cronenberg"
                ),
            )
        )

        self.assertIsInstance(
            result,
            CatGroupAlliedDefenseResult,
        )

        self.assertIsInstance(
            result.first_response,
            CatGroupThreatResponseEvent,
        )

        self.assertIsInstance(
            result.second_response,
            CatGroupThreatResponseEvent,
        )

        self.assertTrue(
            result.defended
        )

        self.assert_not_mapping(
            result
        )

        self.assert_not_mapping(
            result.first_response
        )

        self.assert_not_mapping(
            result.second_response
        )

    def test_threat_response_uses_immutable_collections(
        self
    ):
        self.prepare_alliance()

        result = (
            self.alliances.shared_defense(
                self.first_group,
                self.second_group,
                self.cats.cats,
                threat=CatGroupThreatState(
                    name="cronenberg"
                ),
            )
        )

        self.assertIsInstance(
            result.first_response.defenders,
            tuple,
        )

        self.assertIsInstance(
            result.first_response.withdrawers,
            tuple,
        )

        with self.assertRaises(
            AttributeError
        ):
            result.first_response.threat = (
                "changed"
            )

    def test_break_denial_returns_object(
        self
    ):
        result = (
            self.alliances.break_alliance(
                self.first_group,
                self.second_group,
                reason="territory_seized",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupAllianceBreakDeniedResult,
        )

        self.assertFalse(
            result.broken
        )

        self.assertEqual(
            result.reason,
            "not_allied",
        )

        self.assert_not_mapping(
            result
        )

    def test_break_returns_broken_event_object(
        self
    ):
        self.prepare_alliance()

        result = (
            self.alliances.break_alliance(
                self.first_group,
                self.second_group,
                reason="territory_seized",
                betrayal=True,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupAllianceBrokenEvent,
        )

        self.assertTrue(
            result.broken
        )

        self.assertTrue(
            result.betrayal
        )

        self.assertEqual(
            result.reason,
            "territory_seized",
        )

        self.assert_not_mapping(
            result
        )

    def test_broken_event_history_stores_objects(
        self
    ):
        self.prepare_alliance()

        result = (
            self.alliances.break_alliance(
                self.first_group,
                self.second_group,
                reason="territory_seized",
                betrayal=True,
            )
        )

        first_history = (
            self.groups.groups[
                self.first_group
            ].history[
                -1
            ]
        )

        second_history = (
            self.groups.groups[
                self.second_group
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            first_history,
            CatGroupAllianceBrokenEvent,
        )

        self.assertIsInstance(
            second_history,
            CatGroupAllianceBrokenEvent,
        )

        self.assertEqual(
            first_history,
            result,
        )

        self.assertEqual(
            second_history,
            result,
        )

        self.assert_not_mapping(
            first_history
        )

    def test_alliance_results_are_frozen(
        self
    ):
        formed = (
            self.prepare_alliance()
        )

        with self.assertRaises(
            AttributeError
        ):
            formed.first_group = (
                "changed"
            )

        broken = (
            self.alliances.break_alliance(
                self.first_group,
                self.second_group,
                reason="territory_seized",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            broken.reason = (
                "changed"
            )


if __name__ == "__main__":
    unittest.main()
