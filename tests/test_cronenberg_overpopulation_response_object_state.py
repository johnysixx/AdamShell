import unittest

from cats import Cats
from cats.cat_overpopulation_activation_state import (
    CatOverpopulationActivatedEvent,
    CatOverpopulationActivationDeniedResult,
)
from universe.cronenberg_population_statistics_state import (
    CronenbergPopulationCriticalResponse,
    CronenbergPopulationDelta,
    CronenbergPopulationPressureTransitionEvent,
    CronenbergPopulationPressureWarningEvent,
    CronenbergPopulationRecord,
    CronenbergPopulationSnapshot,
)
from universe.universe import Universe
from universe.universe_tick_result_state import (
    UniverseTickPhaseCompletedResult,
)


class CronenbergOverpopulationResponseObjectStateTests(
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

    def test_cat_activation_is_object(
        self
    ):
        universe = Universe()

        cats = Cats(
            universe
        )

        cat = cats.create_cat(
            name="population_hunter",
            color="black",
            fur_length="short",
        )

        result = (
            cats
            .activate_for_cronenberg_overpopulation(
                cat,
                hunt_quota=10,
            )
        )

        self.assertIsInstance(
            result,
            CatOverpopulationActivatedEvent,
        )

        self.assertTrue(
            result.activated
        )

        self.assertEqual(
            result.cat,
            cat.name,
        )

        self.assertEqual(
            result.suggested_intent,
            "hunt_nearest_cronenberg",
        )

        self.assertIsInstance(
            cats.events[-1],
            CatOverpopulationActivatedEvent,
        )

        self.assert_object_only(
            result
        )

    def test_cat_activation_denial_is_object(
        self
    ):
        universe = Universe()

        cats = Cats(
            universe
        )

        result = (
            cats
            .activate_for_cronenberg_overpopulation(
                object()
            )
        )

        self.assertIsInstance(
            result,
            CatOverpopulationActivationDeniedResult,
        )

        self.assertFalse(
            result.activated
        )

        self.assertEqual(
            result.reason,
            "invalid_cat",
        )

        self.assert_object_only(
            result
        )

    def test_population_snapshot_is_object(
        self
    ):
        universe = Universe()

        snapshot = (
            universe
            .cronenberg_population_statistics
            .snapshot()
        )

        self.assertIsInstance(
            snapshot,
            CronenbergPopulationSnapshot,
        )

        self.assertEqual(
            snapshot.total_count,
            0,
        )

        self.assertEqual(
            snapshot.population_pressure_level,
            "low",
        )

        self.assert_object_only(
            snapshot
        )

    def test_population_record_has_object_only_graph(
        self
    ):
        universe = Universe()

        statistics = (
            universe
            .cronenberg_population_statistics
        )

        result = (
            statistics.record_snapshot()
        )

        stored = (
            statistics.history[-1]
        )

        self.assertIsInstance(
            result,
            CronenbergPopulationRecord,
        )

        self.assertIsInstance(
            result.snapshot,
            CronenbergPopulationSnapshot,
        )

        self.assertIsInstance(
            result.delta,
            CronenbergPopulationDelta,
        )

        self.assertIsInstance(
            result.critical_response,
            CronenbergPopulationCriticalResponse,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        for value in (
            result,
            result.snapshot,
            result.delta,
            result.critical_response,
        ):
            self.assert_object_only(
                value
            )

    def test_critical_transition_warning_and_activation_are_objects(
        self
    ):
        universe = Universe()

        cats = Cats(
            universe
        )

        cat = cats.create_cat(
            name="critical_hunter",
            color="black",
            fur_length="short",
        )

        statistics = (
            universe
            .cronenberg_population_statistics
        )

        statistics.record_snapshot()

        for number in range(
            11
        ):
            universe.create_cronenberg_from_quantum_error(
                RuntimeError(
                    f"pressure-{number}"
                ),
                "test",
                f"pressure_{number}",
            )

        result = (
            statistics.record_snapshot()
        )

        self.assertIsInstance(
            result.pressure_transition,
            CronenbergPopulationPressureTransitionEvent,
        )

        self.assertEqual(
            result.pressure_transition
            .current_level,
            "critical",
        )

        self.assertIsInstance(
            result.pressure_warning,
            CronenbergPopulationPressureWarningEvent,
        )

        self.assertGreaterEqual(
            result.pressure_warning
            .existing_cats_activated,
            1,
        )

        self.assertIn(
            cat.name,
            result.pressure_warning
            .activated_cat_names,
        )

        self.assertEqual(
            cat.state,
            "aware_of_cronenberg_overpopulation",
        )

        emitted_warning = next(
            event
            for event
            in reversed(
                universe.quantum_events
            )
            if isinstance(
                event,
                CronenbergPopulationPressureWarningEvent,
            )
        )

        self.assertEqual(
            emitted_warning,
            result.pressure_warning,
        )

        self.assertIsNot(
            emitted_warning,
            result.pressure_warning,
        )

        self.assert_object_only(
            result.pressure_transition
        )

        self.assert_object_only(
            result.pressure_warning
        )

    def test_scheduler_statistics_phase_keeps_record_object(
        self
    ):
        universe = Universe()

        report = (
            universe.tick_universe()
        )

        phase = next(
            phase
            for phase
            in report.phases
            if phase.phase
            == "statistics"
        )

        self.assertIsInstance(
            phase,
            UniverseTickPhaseCompletedResult,
        )

        self.assertIsInstance(
            phase.result,
            CronenbergPopulationRecord,
        )

        self.assert_object_only(
            phase.result
        )


if __name__ == "__main__":
    unittest.main()
