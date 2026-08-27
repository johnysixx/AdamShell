import unittest

from universe.universe import Universe


class TickEntity:

    def __init__(
        self,
        name,
        fail=False
    ):
        self.name = name
        self.type = "tick_test_entity"
        self.active = True
        self.fail = fail
        self.ticks = 0

    def tick(
        self,
        universe
    ):
        self.ticks += 1

        if self.fail:
            raise RuntimeError(
                f"{self.name} tick failed"
            )


class UniverseTickSchedulerTests(
    unittest.TestCase
):

    def test_tick_returns_phase_report(
        self
    ):
        universe = Universe()

        report = universe.tick()

        self.assertEqual(
            report[
                "tick"
            ],
            1
        )

        self.assertEqual(
            universe.universe_tick,
            1
        )

        self.assertIn(
            "phases",
            report
        )

        self.assertIn(
            "errors",
            report
        )

    def test_phase_error_creates_cronenberg_and_tick_continues(
        self
    ):
        universe = Universe()

        original_history = len(
            universe.universe_history
        )

        def broken_physics():
            raise RuntimeError(
                "physics exploded"
            )

        universe.update_physics = (
            broken_physics
        )

        report = (
            universe.tick_universe()
        )

        self.assertFalse(
            report[
                "ok"
            ]
        )

        self.assertEqual(
            report[
                "error_count"
            ],
            1
        )

        self.assertEqual(
            len(
                report[
                    "cronenbergs_created"
                ]
            ),
            1
        )

        self.assertEqual(
            universe.cronenberg_count,
            1
        )

        # History still runs after broken physics.
        self.assertEqual(
            len(
                universe.universe_history
            ),
            original_history + 1
        )

        self.assertEqual(
            report[
                "errors"
            ][
                0
            ][
                "phase"
            ],
            "physics"
        )

    def test_entity_error_does_not_stop_other_entities(
        self
    ):
        universe = Universe()

        broken = TickEntity(
            "broken",
            fail=True
        )

        healthy = TickEntity(
            "healthy"
        )

        universe.add_entity(
            broken
        )

        universe.add_entity(
            healthy
        )

        report = (
            universe.tick_universe()
        )

        self.assertEqual(
            broken.ticks,
            1
        )

        self.assertEqual(
            healthy.ticks,
            1
        )

        self.assertEqual(
            report[
                "error_count"
            ],
            1
        )

        self.assertEqual(
            universe.cronenberg_count,
            1
        )

        self.assertEqual(
            report[
                "errors"
            ][
                0
            ][
                "source_component"
            ],
            "entity:broken"
        )

    def test_multiple_independent_errors_create_multiple_cronenbergs(
        self
    ):
        universe = Universe()

        universe.add_entity(
            TickEntity(
                "first",
                fail=True
            )
        )

        universe.add_entity(
            TickEntity(
                "second",
                fail=True
            )
        )

        report = (
            universe.tick_universe()
        )

        self.assertEqual(
            report[
                "error_count"
            ],
            2
        )

        self.assertEqual(
            len(
                report[
                    "cronenbergs_created"
                ]
            ),
            2
        )

        self.assertEqual(
            universe.cronenberg_count,
            2
        )


if __name__ == "__main__":
    unittest.main()
