import unittest

from cats.cats import Cats
from core.entity.components import (
    SpatialVector3,
)
from core.entity.quantum_cat_route import (
    QuantumCatRouteEncounter,
)
from universe.quantum_cat_route_advance_state import (
    QuantumCatRouteAdvancedEvent,
    QuantumCatRouteAlreadyArrivedResult,
    QuantumCatRouteDetouredEvent,
    QuantumCatRouteNoActiveRouteResult,
)
from universe.universe import Universe


class QuantumCatRouteAdvanceObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = (
            self.cats.create_cat(
                name="route_advance_cat",
                color="black",
                fur_length="short",
            )
        )

        self.cat.current_layer = (
            "quantum_layer"
        )

        self.cat.position = (
            SpatialVector3.zero()
        )

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
                "result"
            ]

    def advance(
        self,
        cronenbergs=None,
    ):
        return (
            self.universe
            .quantum_space
            .advance_cat_route(
                cat=self.cat,
                cronenbergs=(
                    []
                    if cronenbergs is None
                    else cronenbergs
                ),
                encounter_system=(
                    self.universe
                    .cat_cronenberg_encounter
                ),
                universe=self.universe,
            )
        )

    def test_no_active_route_result_is_object(
        self
    ):
        result = (
            self.advance()
        )

        self.assertIsInstance(
            result,
            QuantumCatRouteNoActiveRouteResult,
        )

        self.assertEqual(
            result.result,
            "no_active_route",
        )

        self.assertFalse(
            result.arrived
        )

        self.assert_object_only(
            result
        )

    def test_route_advance_result_is_object(
        self
    ):
        destination = (
            SpatialVector3(
                x=1.0,
                y=0.0,
                z=0.0,
            )
        )

        (
            self.universe
            .quantum_space
            .plan_direct_cat_route(
                cat_id=self.cat.name,
                start_position=
                    self.cat.position,
                destination_position=
                    destination,
                destination="test",
                step_size=1.0,
            )
        )

        result = (
            self.advance()
        )

        self.assertIsInstance(
            result,
            QuantumCatRouteAdvancedEvent,
        )

        self.assertEqual(
            result.position,
            destination,
        )

        self.assertTrue(
            result.arrived
        )

        self.assert_object_only(
            result
        )

    def test_already_arrived_result_is_object(
        self
    ):
        (
            self.universe
            .quantum_space
            .plan_direct_cat_route(
                cat_id=self.cat.name,
                start_position=
                    self.cat.position,
                destination_position=
                    self.cat.position,
                destination="same_place",
                step_size=1.0,
            )
        )

        result = (
            self.advance()
        )

        self.assertIsInstance(
            result,
            QuantumCatRouteAlreadyArrivedResult,
        )

        self.assertEqual(
            result.position,
            self.cat.position,
        )

        self.assert_object_only(
            result
        )

    def test_large_cronenberg_returns_detour_object_graph(
        self
    ):
        destination = (
            SpatialVector3(
                x=2.0,
                y=0.0,
                z=0.0,
            )
        )

        planned = (
            self.universe
            .quantum_space
            .plan_direct_cat_route(
                cat_id=self.cat.name,
                start_position=
                    self.cat.position,
                destination_position=
                    destination,
                destination="test",
                step_size=1.0,
            )
        )

        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "route obstacle"
                ),
                source_component="test",
                source_operation=(
                    "route_advance_object"
                ),
            )
        )

        cronenberg.position = (
            SpatialVector3(
                x=1.0,
                y=0.0,
                z=0.0,
            )
        )

        cronenberg.size = 2.0

        result = (
            self.advance(
                cronenbergs=[
                    cronenberg
                ]
            )
        )

        self.assertIsInstance(
            result,
            QuantumCatRouteDetouredEvent,
        )

        self.assertIsInstance(
            result.encounter,
            QuantumCatRouteEncounter,
        )

        self.assertIs(
            planned.route.encounters[-1],
            result.encounter,
        )

        self.assertIs(
            self.universe
            .cat_cronenberg_encounter
            .history[-1],
            result.encounter,
        )

        self.assertEqual(
            result.encounter.result,
            "cat_avoids_cronenberg",
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
