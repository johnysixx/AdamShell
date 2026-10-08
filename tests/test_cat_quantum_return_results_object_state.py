import unittest

from cats.cats import Cats
from core.entity.components import SpatialVector3
from quantum.cat_quantum_return_result_state import (
    CatQuantumReturnAdvancedEvent,
    CatQuantumReturnNotAdvancedResult,
    CatQuantumReturnRouteNotStartedResult,
    CatQuantumReturnRouteStartedEvent,
)
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J,
)
from universe.universe import Universe


class CatQuantumReturnResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="return_result_cat",
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
            _ = value["name"]

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

    def test_missing_pair_start_failure_is_object(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .start_quantum_return_route(
                cat=self.cat,
                pair_id="missing_pair",
            )
        )

        self.assertIsInstance(
            result,
            CatQuantumReturnRouteNotStartedResult,
        )

        self.assertFalse(
            result.started
        )

        self.assertEqual(
            result.reason,
            "stable_pair_not_found",
        )

        self.assert_object_only(
            result
        )

    def test_started_return_plan_is_object(
        self
    ):
        creation = (
            self.create_pair()
        )

        pair_id = creation.pair_id

        # Return route starts from the remote side.
        self.cat.current_layer = (
            "quantum_layer"
        )

        self.cat.position = (
            creation.target_box.position
        )

        result = (
            self.universe
            .cat_box_transfer
            .start_quantum_return_route(
                cat=self.cat,
                pair_id=pair_id,
            )
        )

        self.assertIsInstance(
            result,
            CatQuantumReturnRouteStartedEvent,
        )

        self.assertTrue(
            result.started
        )

        self.assertIsInstance(
            result.destination,
            SpatialVector3,
        )

        self.assert_object_only(
            result
        )

    def test_no_active_return_is_object(
        self
    ):
        result = (
            self.cats
            .advance_cat_quantum_return(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatQuantumReturnNotAdvancedResult,
        )

        self.assertFalse(
            result.advanced
        )

        self.assert_object_only(
            result
        )

    def test_advanced_return_event_uses_objects(
        self
    ):
        creation = (
            self.create_pair()
        )

        source = creation.source_box

        target = creation.target_box

        self.universe.cat_box_transfer            .transfer_cat(
                cat=self.cat,
                source_box_id=source.id,
                target_box_id=target.id,
            )

        started = (
            self.universe
            .cat_box_transfer
            .start_quantum_return_route(
                cat=self.cat,
                pair_id=creation.pair_id,
            )
        )

        self.assertTrue(
            started.started
        )

        result = (
            self.cats
            .advance_cat_quantum_return(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatQuantumReturnAdvancedEvent,
        )

        self.assertIsInstance(
            result.position,
            SpatialVector3,
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
