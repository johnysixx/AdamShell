import unittest

from cats.cat_exploration_goal import (
    CatExplorationGoal,
)
from cats.cats import Cats
from core.entity.components import SpatialVector3
from quantum.cat_quantum_exploration_result_state import (
    CatQuantumExplorationAdvancedEvent,
    CatQuantumExplorationArrivalResolvedEvent,
    CatQuantumExplorationContinuedEvent,
    CatQuantumExplorationNotAdvancedResult,
    CatQuantumExplorationRouteStartedEvent,
)
from quantum.cat_quantum_path_state import (
    CatQuantumDirectPathStabilizedEvent,
)
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J,
)
from universe.universe import Universe


class CatQuantumExplorationResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="exploration_result_cat",
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

        self.cat.exploration_goal = (
            CatExplorationGoal(
                layer="quantum_layer",
                position=SpatialVector3(
                    x=4.0,
                    y=0.0,
                    z=0.0,
                ),
            )
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

    def test_direct_path_is_object(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .stabilize_direct_trail(
                cat=self.cat,
                destination=SpatialVector3(
                    x=3.0,
                    y=0.0,
                    z=0.0,
                ),
            )
        )

        self.assertIsInstance(
            result,
            CatQuantumDirectPathStabilizedEvent,
        )

        self.assertTrue(
            result.stabilized
        )

        self.assertEqual(
            result.path_kind,
            "most_direct_possible",
        )

        self.assert_object_only(
            result
        )

    def test_no_exploration_result_is_object(
        self
    ):
        result = (
            self.cats
            .advance_cat_quantum_exploration(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatQuantumExplorationNotAdvancedResult,
        )

        self.assertFalse(
            result.advanced
        )

        self.assert_object_only(
            result
        )

    def test_route_start_result_is_object(
        self
    ):
        self.cats.think_and_act(
            cat=self.cat
        )

        state = (
            self.cat.quantum_exploration
        )

        self.assertIsInstance(
            state.stabilized_path,
            CatQuantumDirectPathStabilizedEvent,
        )

        route_event = next(
            event
            for event
            in reversed(
                self.universe
                .cat_box_transfer
                .history
            )
            if isinstance(
                event,
                CatQuantumExplorationRouteStartedEvent,
            )
        )

        self.assertIsInstance(
            route_event.start_position,
            SpatialVector3,
        )

        self.assertIsInstance(
            route_event.destination,
            SpatialVector3,
        )

        self.assert_object_only(
            route_event
        )

    def test_advance_result_is_object(
        self
    ):
        self.cats.think_and_act(
            cat=self.cat
        )

        result = (
            self.cats
            .advance_cat_quantum_exploration(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatQuantumExplorationAdvancedEvent,
        )

        self.assert_object_only(
            result
        )

    def test_arrival_resolution_is_object(
        self
    ):
        self.cat.personality.traits.curiosity = 0.0
        self.cat.personality.traits.courage = 0.0
        self.cat.personality.traits.patience = 1.0

        self.cats.think_and_act(
            cat=self.cat
        )

        result = None

        for _ in range(100):
            result = (
                self.cats
                .advance_cat_quantum_exploration(
                    self.cat
                )
            )

            if result.arrived:
                break

        self.assertTrue(
            result.arrived
        )

        self.assertIsInstance(
            result.arrival_resolution,
            CatQuantumExplorationArrivalResolvedEvent,
        )

        self.assertTrue(
            result.arrival_resolution.resolved
        )

        self.assert_object_only(
            result.arrival_resolution
        )

    def test_continuation_result_is_object(
        self
    ):
        self.cat.personality.traits.curiosity = 1.0
        self.cat.personality.traits.courage = 1.0
        self.cat.personality.traits.patience = 0.0

        self.cats.think_and_act(
            cat=self.cat
        )

        result = None

        for _ in range(100):
            result = (
                self.cats
                .advance_cat_quantum_exploration(
                    self.cat
                )
            )

            if result.arrived:
                break

        continuation = (
            result
            .arrival_resolution
            .continuation_plan
        )

        self.assertIsInstance(
            continuation,
            CatQuantumExplorationContinuedEvent,
        )

        self.assertTrue(
            continuation.continued
        )

        self.assertIsInstance(
            continuation.destination,
            SpatialVector3,
        )

        self.assert_object_only(
            continuation
        )


if __name__ == "__main__":
    unittest.main()
