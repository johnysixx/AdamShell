import unittest

from lifecycle.life_cycle_result_state import (
    LifeCycleTickSkippedEvent,
)
from universe.universe import Universe
from universe.universe_tick_result_state import (
    UniverseTickPhaseCompletedResult,
    UniverseTickPhaseErrorResult,
    UniverseTickPhaseSkippedResult,
    UniverseTickReport,
)


class UniverseTickResultsObjectStateTests(
    unittest.TestCase
):

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

    def test_tick_returns_object_report(
        self
    ):
        universe = Universe()

        report = universe.tick()

        self.assertIsInstance(
            report,
            UniverseTickReport,
        )

        self.assertEqual(
            report.tick,
            1,
        )

        self.assertIsInstance(
            report.phases,
            tuple,
        )

        self.assertIsInstance(
            report.errors,
            tuple,
        )

        self.assertTrue(
            report.ok
        )

        self.assertEqual(
            report.error_count,
            0,
        )

        self.assert_object_only(
            report
        )

    def test_optional_phase_skip_is_object(
        self
    ):
        universe = Universe()

        report = (
            universe.tick_universe()
        )

        layers = next(
            phase
            for phase
            in report.phases
            if phase.phase == "layers"
        )

        self.assertIsInstance(
            layers,
            UniverseTickPhaseSkippedResult,
        )

        self.assertTrue(
            layers.ok
        )

        self.assertTrue(
            layers.skipped
        )

        self.assertEqual(
            layers.reason,
            "component_not_present",
        )

        self.assert_object_only(
            layers
        )

    def test_biology_phase_keeps_lifecycle_object(
        self
    ):
        universe = Universe()

        report = (
            universe.tick_universe()
        )

        biology = next(
            phase
            for phase
            in report.phases
            if phase.phase == "biology"
        )

        self.assertIsInstance(
            biology,
            UniverseTickPhaseCompletedResult,
        )

        self.assertIsInstance(
            biology.result,
            LifeCycleTickSkippedEvent,
        )

        self.assert_object_only(
            biology
        )

    def test_phase_error_and_report_error_collection_are_objects(
        self
    ):
        universe = Universe()

        def broken_physics():
            raise RuntimeError(
                "object scheduler failure"
            )

        universe.update_physics = (
            broken_physics
        )

        report = (
            universe.tick_universe()
        )

        self.assertFalse(
            report.ok
        )

        self.assertEqual(
            report.error_count,
            1,
        )

        self.assertEqual(
            len(
                report.errors
            ),
            1,
        )

        error = (
            report.errors[0]
        )

        self.assertIsInstance(
            error,
            UniverseTickPhaseErrorResult,
        )

        self.assertEqual(
            error.phase,
            "physics",
        )

        self.assertEqual(
            error.error_type,
            "RuntimeError",
        )

        self.assertEqual(
            error.error_message,
            "object scheduler failure",
        )

        self.assertIsNotNone(
            error.cronenberg_id
        )

        self.assertEqual(
            report.cronenbergs_created,
            (
                error.cronenberg_id,
            ),
        )

        self.assert_object_only(
            error
        )

    def test_entity_tick_results_are_phase_objects(
        self
    ):
        universe = Universe()

        class Entity:

            name = "object_entity"
            active = True

            def tick(
                self,
                universe,
            ):
                return None

        universe.add_entity(
            Entity()
        )

        results = (
            universe.tick_entities()
        )

        self.assertIsInstance(
            results,
            tuple,
        )

        self.assertTrue(
            all(
                isinstance(
                    result,
                    (
                        UniverseTickPhaseCompletedResult,
                        UniverseTickPhaseErrorResult,
                    ),
                )
                for result
                in results
            )
        )

        entity_result = next(
            result
            for result
            in results
            if result.source_component
            == "entity:object_entity"
        )

        self.assertTrue(
            entity_result.ok
        )

        self.assert_object_only(
            entity_result
        )


if __name__ == "__main__":
    unittest.main()
