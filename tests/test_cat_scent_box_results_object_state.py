import unittest

from cats.cat_intention_state import (
    CatIntentionCandidate,
    CatScentBoxTarget,
)
from cats.cat_scent_box_result_state import (
    CatScentBoxFollowingEvent,
    CatScentBoxTransferredEvent,
    CatScentBoxTransferFailedResult,
)
from cats.cats import Cats
from core.entity.components import (
    SpatialVector3,
)
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J,
)
from universe.universe import Universe


class CatScentBoxResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.creator = (
            self.cats.create_cat(
                name="creator",
                color="black",
                fur_length="short",
            )
        )

        self.tracker = (
            self.cats.create_cat(
                name="tracker",
                color="gray",
                fur_length="short",
            )
        )

        self.creator.current_layer = (
            "meeting_place"
        )

        self.creator.position = (
            SpatialVector3(
                x=3.0,
                y=0.0,
                z=0.0,
            )
        )

        self.creator.idea_energy = (
            QUANTUM_BOX_ENERGY_COST_J
            * 10.0
        )

        self.tracker.current_layer = (
            "meeting_place"
        )

        self.tracker.position = (
            SpatialVector3.zero()
        )

        creation = (
            self.universe
            .cat_box_transfer
            .create_exploration_pair(
                cat=self.creator,
                destination_layer=
                    "quantum_layer",
                destination_position=(
                    SpatialVector3(
                        x=8.0,
                        y=0.0,
                        z=0.0,
                    )
                ),
                source_position=(
                    self.creator.position
                ),
            )
        )

        self.source = creation[
            "source_box"
        ]

        self.target = creation[
            "target_box"
        ]

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
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
                "name"
            ]

    def intention(self):
        return CatIntentionCandidate(
            type="follow_scent_through_box",
            target=CatScentBoxTarget(
                identity="cat:creator",
                box_id=self.source.id,
                counterpart_box_id=
                    self.target.id,
                source_layer=
                    "meeting_place",
                target_layer=
                    "quantum_layer",
            ),
            score=1.0,
            reasons=["test"],
        )

    def test_invalid_target_failure_is_object(
        self
    ):
        self.tracker.mind.current_intention = (
            CatIntentionCandidate(
                type="follow_scent_through_box",
                target="invalid",
                score=1.0,
                reasons=["test"],
            )
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.tracker
            )
        )

        self.assertIsInstance(
            result,
            CatScentBoxTransferFailedResult,
        )

        self.assertFalse(
            result.executed
        )

        self.assert_object_only(
            result
        )

    def test_following_event_uses_spatial_objects(
        self
    ):
        self.tracker.mind.current_intention = (
            self.intention()
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.tracker
            )
        )

        self.assertIsInstance(
            result,
            CatScentBoxFollowingEvent,
        )

        self.assertEqual(
            result.destination,
            self.source.position,
        )

        self.assertIsInstance(
            result.destination,
            SpatialVector3,
        )

        self.assert_object_only(
            result
        )

    def test_transfer_event_does_not_expose_legacy_transfer_mapping(
        self
    ):
        self.tracker.position = (
            self.source.position
        )

        self.tracker.mind.current_intention = (
            self.intention()
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.tracker
            )
        )

        self.assertIsInstance(
            result,
            CatScentBoxTransferredEvent,
        )

        self.assertTrue(
            result.transferred
        )

        self.assertTrue(
            result.executed
        )

        self.assertFalse(
            hasattr(
                result,
                "transfer",
            )
        )

        self.assert_object_only(
            result
        )

    def test_history_and_active_execution_store_objects(
        self
    ):
        self.tracker.mind.current_intention = (
            self.intention()
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.tracker
            )
        )

        active = (
            self.tracker
            .mind
            .active_body_execution
        )

        stored = (
            self.cats
            .intention_executor
            .history[-1]
        )

        self.assertIsInstance(
            active,
            CatScentBoxFollowingEvent,
        )

        self.assertIsInstance(
            stored,
            CatScentBoxFollowingEvent,
        )

        self.assertEqual(
            active,
            result,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            active,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )


if __name__ == "__main__":
    unittest.main()
