import unittest

from cats.cat_exploration_pair_execution_result_state import (
    CatAutonomousExplorationPairStartedEvent,
)
from cats.cats import Cats
from core.entity.components import SpatialVector3
from quantum.cat_stable_exploration_pair_result_state import (
    CatStableExplorationPairCreatedResult,
    CatStableExplorationPairCreationFailedResult,
)
from quantum.cat_stable_exploration_pair_state import (
    CatStableExplorationPairState,
)
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J,
)
from universe.universe import Universe


class CatStableExplorationPairObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="stable_pair_cat",
            color="black",
            fur_length="short",
        )

        self.cat.current_layer = (
            "meeting_place"
        )

        self.cat.position = (
            SpatialVector3.zero()
        )

        self.cat.idea_energy = (
            QUANTUM_BOX_ENERGY_COST_J
            * 10.0
        )

    def assert_object_only(
        self,
        value,
    ):
        for method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "pair_id"
            ]

    def create_pair(self):
        return (
            self.universe
            .cat_box_transfer
            .create_exploration_pair(
                cat=self.cat,
                destination_layer=
                    "quantum_layer",
                destination_position=(
                    SpatialVector3(
                        x=4.0,
                        y=0.0,
                        z=0.0,
                    )
                ),
            )
        )

    def test_creation_result_is_object(
        self
    ):
        result = (
            self.create_pair()
        )

        self.assertIsInstance(
            result,
            CatStableExplorationPairCreatedResult,
        )

        self.assertTrue(
            result.created
        )

        self.assert_object_only(
            result
        )

    def test_registry_contains_pair_state_objects(
        self
    ):
        result = (
            self.create_pair()
        )

        pair = (
            self.universe
            .stable_cat_box_pairs[-1]
        )

        self.assertIsInstance(
            pair,
            CatStableExplorationPairState,
        )

        self.assertIs(
            pair,
            result.pair,
        )

        self.assertTrue(
            pair.active
        )

        self.assertTrue(
            pair.stable
        )

        self.assert_object_only(
            pair
        )

    def test_pair_tracks_use_through_methods(
        self
    ):
        result = (
            self.create_pair()
        )

        pair = result.pair

        pair.begin_use(
            "other_cat"
        )

        self.assertTrue(
            pair.currently_in_use
        )

        self.assertEqual(
            pair.current_user,
            "other_cat",
        )

        self.assertEqual(
            pair.use_count,
            1,
        )

        self.assertEqual(
            pair.used_by,
            ["other_cat"],
        )

        pair.finish_use()

        self.assertFalse(
            pair.currently_in_use
        )

        self.assertIsNone(
            pair.current_user
        )

    def test_creation_failure_is_object(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .create_exploration_pair(
                cat=self.cat,
                destination_layer=
                    "meeting_place",
                destination_position=(
                    SpatialVector3.zero()
                ),
            )
        )

        self.assertIsInstance(
            result,
            CatStableExplorationPairCreationFailedResult,
        )

        self.assertFalse(
            result.created
        )

        self.assertEqual(
            result.reason,
            "destination_layer_matches_source",
        )

        self.assert_object_only(
            result
        )

    def test_autonomous_execution_result_is_object(
        self
    ):
        self.cat.personality.traits.curiosity = (
            1.0
        )

        result = (
            self.cats.think_and_act(
                cat=self.cat
            )
        )

        execution = (
            result[
                "execution"
            ]
        )

        self.assertIsInstance(
            execution,
            CatAutonomousExplorationPairStartedEvent,
        )

        self.assertTrue(
            execution.executed
        )

        self.assertTrue(
            execution.transfer.transferred
        )

        self.assert_object_only(
            execution
        )

    def test_creator_return_dissolves_pair_state(
        self
    ):
        result = (
            self.create_pair()
        )

        pair = result.pair

        self.universe.cat_box_transfer            .transfer_cat(
                cat=self.cat,
                source_box_id=
                    result.source_box.id,
                target_box_id=
                    result.target_box.id,
            )

        self.universe.cat_box_transfer            .transfer_cat(
                cat=self.cat,
                source_box_id=
                    result.target_box.id,
                target_box_id=
                    result.source_box.id,
            )

        self.assertTrue(
            pair.dissolved
        )

        self.assertFalse(
            pair.active
        )

        self.assertFalse(
            pair.stable
        )

        self.assertTrue(
            pair.creator_returned
        )

        self.assertEqual(
            pair.remaining_energy_j,
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
