import unittest

from cats.cats import Cats
from core.entity.components import SpatialVector3
from quantum.cat_box_transfer_result_state import (
    CatQuantumBoxTransferCompletedEvent,
    CatQuantumBoxTransferFailedResult,
    CatStableExplorationPairTransferEvent,
    StableCatBoxPairDissolutionEvent,
)
from quantum.cat_quantum_trail_state import (
    QuantumCatTrail,
)
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J,
)
from universe.universe import Universe


class CatQuantumBoxTransferResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="transfer_result_cat",
            color="black",
            fur_length="short",
        )

        self.cat.current_layer = (
            "meeting_place"
        )

        self.cat.position = SpatialVector3(
            x=1.0,
            y=0.0,
            z=0.0,
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

    def ordinary_boxes(self):
        source = (
            self.universe
            .create_quantum_box(
                layer="meeting_place"
            )
        )

        target = (
            self.universe
            .create_quantum_box(
                layer="quantum_layer"
            )
        )

        source.position = self.cat.position

        target.position = SpatialVector3(
            x=8.0,
            y=0.0,
            z=0.0,
        )

        self.universe.cat_box_transfer            .pair_boxes(
                source,
                target,
            )

        return source, target

    def test_failure_result_is_object(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                cat=self.cat,
                source_box_id="missing",
                target_box_id="missing_target",
            )
        )

        self.assertIsInstance(
            result,
            CatQuantumBoxTransferFailedResult,
        )

        self.assertFalse(
            result.transferred
        )

        self.assertEqual(
            result.reason,
            "source_box_not_found",
        )

        self.assert_object_only(
            result
        )

    def test_completed_transfer_and_trail_are_objects(
        self
    ):
        source, target = (
            self.ordinary_boxes()
        )

        result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                cat=self.cat,
                source_box_id=source.id,
                target_box_id=target.id,
            )
        )

        self.assertIsInstance(
            result,
            CatQuantumBoxTransferCompletedEvent,
        )

        self.assertIsInstance(
            result.trail,
            QuantumCatTrail,
        )

        self.assertTrue(
            result.transferred
        )

        self.assertTrue(
            result.target_box_consumed
        )

        self.assertIs(
            result.trail,
            self.universe
            .quantum_cat_trails[-1],
        )

        self.assert_object_only(
            result
        )

        self.assert_object_only(
            result.trail
        )

    def test_stable_pair_transfer_result_is_object(
        self
    ):
        self.cat.idea_energy = (
            QUANTUM_BOX_ENERGY_COST_J
            * 10.0
        )

        creation = (
            self.universe
            .cat_box_transfer
            .create_exploration_pair(
                cat=self.cat,
                destination_layer=
                    "quantum_layer",
                destination_position=(
                    SpatialVector3(
                        x=8.0,
                        y=0.0,
                        z=0.0,
                    )
                ),
            )
        )

        result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                cat=self.cat,
                source_box_id=(
                    creation.source_box.id
                ),
                target_box_id=(
                    creation.target_box.id
                ),
            )
        )

        self.assertIsInstance(
            result,
            CatStableExplorationPairTransferEvent,
        )

        self.assertTrue(
            result.transferred
        )

        self.assertTrue(
            result.pair_remains_stable
        )

        self.assertFalse(
            result.target_box_consumed
        )

        self.assert_object_only(
            result
        )

    def test_creator_return_dissolution_is_object(
        self
    ):
        self.cat.idea_energy = (
            QUANTUM_BOX_ENERGY_COST_J
            * 10.0
        )

        creation = (
            self.universe
            .cat_box_transfer
            .create_exploration_pair(
                cat=self.cat,
                destination_layer=
                    "quantum_layer",
                destination_position=(
                    SpatialVector3(
                        x=8.0,
                        y=0.0,
                        z=0.0,
                    )
                ),
            )
        )

        source = creation.source_box

        target = creation.target_box

        self.universe.cat_box_transfer            .transfer_cat(
                cat=self.cat,
                source_box_id=source.id,
                target_box_id=target.id,
            )

        result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                cat=self.cat,
                source_box_id=target.id,
                target_box_id=source.id,
            )
        )

        dissolution = (
            result.pair_dissolution
        )

        self.assertIsInstance(
            dissolution,
            StableCatBoxPairDissolutionEvent,
        )

        self.assertTrue(
            dissolution.dissolved
        )

        self.assertTrue(
            dissolution.energy_conserved
        )

        self.assertGreater(
            dissolution.cronenberg_energy_j,
            0.0,
        )

        self.assert_object_only(
            dissolution
        )

    def test_transfer_history_keeps_objects(
        self
    ):
        source, target = (
            self.ordinary_boxes()
        )

        result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                cat=self.cat,
                source_box_id=source.id,
                target_box_id=target.id,
            )
        )

        stored = (
            self.universe
            .cat_box_transfer
            .history[-1]
        )

        quantum_event = (
            self.universe
            .quantum_events[-1]
        )

        self.assertIsInstance(
            stored,
            CatQuantumBoxTransferCompletedEvent,
        )

        self.assertIsInstance(
            quantum_event,
            CatQuantumBoxTransferCompletedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertEqual(
            quantum_event,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assertIsNot(
            quantum_event,
            result,
        )


if __name__ == "__main__":
    unittest.main()
