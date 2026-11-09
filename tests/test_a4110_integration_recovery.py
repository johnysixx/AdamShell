import io
import random
import unittest

from contextlib import redirect_stdout

from universe.universe import Universe


class ProbeEntity:
    def __init__(self, name, action=None):
        self.name = name
        self.type = "a4110_integration_probe"
        self.active = True
        self.ticks = 0
        self.age = 0
        self.energy = 10.0
        self.observed = []
        self.action = action

    def tick(self, universe):
        self.ticks += 1

        if self.action is not None:
            self.action(self, universe)


class A4110IntegrationRecoveryTests(unittest.TestCase):

    def setUp(self):
        before_rng = random.getstate()
        self.addCleanup(random.setstate, before_rng)

    @staticmethod
    def make_world(number, *entities):
        with redirect_stdout(io.StringIO()):
            world = Universe(
                universe_id=f"a4110_regression_{number}"
            )
            for entity in entities:
                world.add_entity(entity)

        return world

    @staticmethod
    def tick(world):
        with redirect_stdout(io.StringIO()):
            return world.tick_universe()

    @staticmethod
    def tick_entities(world):
        with redirect_stdout(io.StringIO()):
            return world.tick_entities()

    @staticmethod
    def history_ticks(world):
        return [
            snapshot.tick
            for snapshot in world.universe_history
        ]

    def assert_manifestations(self, world, reports):
        ids = [
            cronenberg_id
            for report in reports
            for cronenberg_id
            in report.cronenbergs_created
        ]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            len(ids),
            world.cronenberg_count,
        )
        self.assertEqual(
            set(ids),
            {item.id for item in world.cronenbergs},
        )

    def test_01_three_healthy_ticks(self):
        world = self.make_world(1)
        history = world.universe_history
        stats = (
            world.cronenberg_population_statistics
            .history
        )

        reports = [self.tick(world) for _ in range(3)]

        self.assertEqual(
            [report.tick for report in reports],
            [1, 2, 3],
        )
        self.assertTrue(all(r.ok for r in reports))
        self.assertEqual(
            self.history_ticks(world),
            [1, 2, 3],
        )
        self.assertEqual(len(stats), 3)
        self.assertIs(world.universe_history, history)
        self.assertIs(
            world.cronenberg_population_statistics.history,
            stats,
        )
        self.assertEqual(world.cronenberg_count, 0)

    def test_02_fail_once_then_recover(self):
        attempts = {"count": 0}

        def action(entity, world):
            attempts["count"] += 1
            entity.age += 1

            if attempts["count"] == 1:
                raise RuntimeError("first failure")

        probe = ProbeEntity("recover", action)
        world = self.make_world(2, probe)

        first = self.tick(world)

        self.assertEqual(first.error_count, 1)
        self.assertEqual(
            (probe.ticks, probe.age),
            (1, 0),
        )

        second = self.tick(world)

        self.assertEqual(second.error_count, 0)
        self.assertEqual(
            (probe.ticks, probe.age),
            (2, 1),
        )
        self.assertEqual(
            self.history_ticks(world),
            [1, 2],
        )

        self.assert_manifestations(
            world, [first, second]
        )

    def test_03_two_failures_then_recover(self):
        attempts = {"count": 0}

        def action(entity, world):
            attempts["count"] += 1
            entity.age += 5

            if attempts["count"] <= 2:
                raise RuntimeError("repeated failure")

        probe = ProbeEntity("repeated", action)
        world = self.make_world(3, probe)

        reports = []

        for n in (1, 2):
            report = self.tick(world)
            reports.append(report)

            self.assertEqual(report.error_count, 1)
            self.assertEqual(
                (probe.ticks, probe.age),
                (n, 0),
            )

        reports.append(self.tick(world))

        self.assertEqual(reports[-1].error_count, 0)
        self.assertEqual(
            (probe.ticks, probe.age),
            (3, 5),
        )
        self.assertEqual(
            self.history_ticks(world),
            [1, 2, 3],
        )

        self.assert_manifestations(world, reports)

    def test_04_earlier_entity_commit_survives(self):
        def good_action(entity, world):
            entity.energy += 1.0

        good = ProbeEntity("good", good_action)
        attempts = {"count": 0}

        def bad_action(entity, world):
            attempts["count"] += 1

            if attempts["count"] == 1:
                good.energy = 999.0
                raise RuntimeError("cross entity")

        bad = ProbeEntity("bad", bad_action)
        world = self.make_world(4, good, bad)

        first = self.tick(world)

        self.assertEqual(first.error_count, 1)
        self.assertEqual(good.energy, 11.0)

        second = self.tick(world)

        self.assertEqual(second.error_count, 0)
        self.assertEqual(good.energy, 12.0)
        self.assertEqual(
            (good.ticks, bad.ticks),
            (2, 2),
        )

        self.assert_manifestations(
            world, [first, second]
        )

    def test_05_global_rng_restored_before_manifestation(self):
        def action(entity, world):
            random.random()
            random.random()
            raise RuntimeError("global rng failure")

        probe = ProbeEntity("rng", action)
        world = self.make_world(5, probe)

        original = (
            world.create_cronenberg_from_quantum_error
        )

        observed = []

        def observe(*args, **kwargs):
            observed.append(random.getstate())
            return original(*args, **kwargs)

        world.create_cronenberg_from_quantum_error = (
            observe
        )

        expected = []

        for _ in range(2):
            expected.append(random.getstate())
            results = self.tick_entities(world)

            errors = [
                result
                for result in results
                if not result.ok
            ]

            self.assertEqual(len(errors), 1)

        self.assertEqual(observed, expected)
        self.assertEqual(world.cronenberg_count, 2)

    def test_06_phase_rng_restored_before_manifestation(self):
        world = self.make_world(6)

        original = (
            world.create_cronenberg_from_quantum_error
        )

        observed = []

        def observe(*args, **kwargs):
            observed.append(random.getstate())
            return original(*args, **kwargs)

        world.create_cronenberg_from_quantum_error = (
            observe
        )

        before_rng = random.getstate()
        before_energy = world.energy_pool

        def broken():
            random.random()
            random.random()
            world.energy_pool -= 19
            raise RuntimeError("phase failure")

        with redirect_stdout(io.StringIO()):
            result = world._run_tick_operation(
                phase="physics",
                operation=broken,
                source_component="universe",
                source_operation="a4110_physics",
            )

        self.assertFalse(result.ok)
        self.assertEqual(observed, [before_rng])
        self.assertEqual(
            world.energy_pool,
            before_energy,
        )
        self.assertEqual(world.cronenberg_count, 1)

    def test_07_private_rng_two_failures_then_success(self):
        local_rng = random.Random(2026)
        expected_rng = random.Random(2026)
        expected_value = expected_rng.random()

        initial_state = local_rng.getstate()
        attempts = {"count": 0}

        def action(entity, world):
            attempts["count"] += 1
            value = entity.local_rng.random()
            entity.observed.append(value)

            if attempts["count"] <= 2:
                raise RuntimeError("private rng failure")

        probe = ProbeEntity("private_rng", action)
        probe.local_rng = local_rng

        world = self.make_world(7, probe)
        reports = []

        for _ in range(2):
            report = self.tick(world)
            reports.append(report)

            self.assertEqual(report.error_count, 1)
            self.assertEqual(
                local_rng.getstate(),
                initial_state,
            )
            self.assertEqual(probe.observed, [])

        reports.append(self.tick(world))

        self.assertEqual(reports[-1].error_count, 0)
        self.assertEqual(
            probe.observed,
            [expected_value],
        )
        self.assertEqual(probe.ticks, 3)

        self.assert_manifestations(world, reports)

    def test_08_quantum_clock_survives_physics_failure(self):
        world = self.make_world(8)

        with redirect_stdout(io.StringIO()):
            world.enable_quantum_layer()

        original = world.update_physics
        attempts = {"count": 0}

        def physics():
            attempts["count"] += 1

            if attempts["count"] == 2:
                world.quantum_state.tick_count = 999
                world.quantum_clock_events.append(
                    "partial"
                )
                raise RuntimeError("physics failure")

            return original()

        world.update_physics = physics

        quantum_state = world.quantum_state
        clock_events = world.quantum_clock_events

        reports = []
        ticks = []
        counts = []

        for _ in range(3):
            reports.append(self.tick(world))
            ticks.append(world.quantum_state.tick_count)
            counts.append(
                len(world.quantum_clock_events)
            )

        self.assertEqual(
            [r.error_count for r in reports],
            [0, 1, 0],
        )
        self.assertEqual(ticks, [1, 2, 3])
        self.assertEqual(counts, [1, 2, 3])
        self.assertIs(world.quantum_state, quantum_state)
        self.assertIs(
            world.quantum_clock_events,
            clock_events,
        )
        self.assertEqual(
            self.history_ticks(world),
            [1, 2, 3],
        )

        self.assert_manifestations(world, reports)

    def test_09_biology_publication_recovers(self):
        world = self.make_world(9)
        world.physical_universe_started = True

        lifecycle = world.life_cycle_system
        lifecycle.handlers = []

        original = lifecycle.tick_day
        attempts = {"count": 0}

        def biology():
            attempts["count"] += 1
            result = original()

            if attempts["count"] == 1:
                raise RuntimeError("late biology failure")

            return result

        lifecycle.tick_day = biology

        first = self.tick(world)

        self.assertEqual(
            [e.phase for e in first.errors],
            ["biology"],
        )
        self.assertEqual(lifecycle.day, 0)
        self.assertEqual(len(lifecycle.history), 0)

        second = self.tick(world)
        third = self.tick(world)

        self.assertTrue(second.ok)
        self.assertTrue(third.ok)
        self.assertEqual(lifecycle.day, 2)
        self.assertEqual(len(lifecycle.history), 2)
        self.assertEqual(
            self.history_ticks(world),
            [1, 2, 3],
        )

        self.assert_manifestations(
            world, [first, second, third]
        )

    def test_10_history_fails_twice_then_recovers(self):
        world = self.make_world(10)
        original = world.record_universe_state
        attempts = {"count": 0}

        def history():
            attempts["count"] += 1
            original()

            if attempts["count"] <= 2:
                raise RuntimeError("history failure")

        world.record_universe_state = history

        reports = [
            self.tick(world)
            for _ in range(3)
        ]

        self.assertEqual(
            [r.error_count for r in reports],
            [1, 1, 0],
        )
        self.assertEqual(
            self.history_ticks(world),
            [3],
        )

        populations = [
            record.snapshot.total_count
            for record
            in world.cronenberg_population_statistics.history
        ]

        self.assertEqual(populations, [0, 1, 2])
        self.assert_manifestations(world, reports)

    def test_11_multiple_errors_then_clean_tick(self):
        world = self.make_world(11)
        world.physical_universe_started = True
        world.life_cycle_system.handlers = []

        original_physics = world.update_physics
        original_biology = (
            world.life_cycle_system.tick_day
        )

        attempts = {"physics": 0, "biology": 0}

        def physics():
            attempts["physics"] += 1
            result = original_physics()

            if attempts["physics"] == 1:
                raise RuntimeError("physics failure")

            return result

        def biology():
            attempts["biology"] += 1
            result = original_biology()

            if attempts["biology"] == 1:
                raise RuntimeError("biology failure")

            return result

        world.update_physics = physics
        world.life_cycle_system.tick_day = biology

        first = self.tick(world)

        self.assertEqual(
            [e.phase for e in first.errors],
            ["physics", "biology"],
        )
        self.assertEqual(
            world.life_cycle_system.day,
            0,
        )

        second = self.tick(world)

        self.assertTrue(second.ok)
        self.assertEqual(
            world.life_cycle_system.day,
            1,
        )
        self.assertEqual(
            self.history_ticks(world),
            [1, 2],
        )

        self.assert_manifestations(
            world, [first, second]
        )

    def test_12_shared_graph_phase_retry(self):
        attempts = {"count": 0}
        payload = {"items": ["base"]}
        items = payload["items"]

        class Layer:
            def __init__(self):
                self.payload = payload

            def tick(self):
                attempts["count"] += 1

                if attempts["count"] == 1:
                    items.append("partial")
                    raise RuntimeError("layer failure")

                items.append("committed")

        layer = Layer()
        probe = ProbeEntity("observer")
        probe.payload = payload

        world = self.make_world(12, probe)
        world.layers = layer

        first = self.tick(world)

        self.assertEqual(
            [e.phase for e in first.errors],
            ["layers"],
        )
        self.assertEqual(items, ["base"])

        second = self.tick(world)

        self.assertTrue(second.ok)
        self.assertEqual(
            items,
            ["base", "committed"],
        )
        self.assertIs(world.layers, layer)
        self.assertIs(probe.payload, payload)
        self.assertIs(payload["items"], items)
        self.assertEqual(probe.ticks, 2)

        self.assert_manifestations(
            world, [first, second]
        )

    def test_13_history_failure_preserves_biology(self):
        world = self.make_world(13)
        world.physical_universe_started = True

        lifecycle = world.life_cycle_system
        lifecycle.handlers = []

        original = world.record_universe_state
        attempts = {"count": 0}

        def history():
            attempts["count"] += 1
            original()

            if attempts["count"] == 1:
                lifecycle.day = 999
                lifecycle.history.append("partial")
                raise RuntimeError("history corruption")

        world.record_universe_state = history

        first = self.tick(world)

        self.assertEqual(
            [e.phase for e in first.errors],
            ["history"],
        )
        self.assertEqual(lifecycle.day, 1)
        self.assertEqual(len(lifecycle.history), 1)

        second = self.tick(world)

        self.assertTrue(second.ok)
        self.assertEqual(lifecycle.day, 2)
        self.assertEqual(len(lifecycle.history), 2)
        self.assertEqual(
            self.history_ticks(world),
            [2],
        )

        self.assert_manifestations(
            world, [first, second]
        )

    def test_14_repeated_registry_rollback(self):
        attempts = {"count": 0}

        def action(entity, world):
            attempts["count"] += 1

            world.world["probe"]["items"].append(
                "update"
            )
            world.entity_memory["probe"]["entries"].append(
                "update"
            )
            world.conflict_history.append("update")
            world.symbolic_replay_outbox.append(
                "update"
            )

            if attempts["count"] <= 2:
                raise RuntimeError("registry failure")

        probe = ProbeEntity("registry_probe", action)
        world = self.make_world(14, probe)

        registry = world.world
        memory = world.entity_memory
        conflicts = world.conflict_history
        outbox = world.symbolic_replay_outbox

        nested_world = {"items": ["base"]}
        nested_memory = {"entries": ["base"]}

        registry["probe"] = nested_world
        memory["probe"] = nested_memory

        items = nested_world["items"]
        entries = nested_memory["entries"]

        reports = []

        for _ in range(2):
            report = self.tick(world)
            reports.append(report)

            self.assertEqual(report.error_count, 1)
            self.assertEqual(items, ["base"])
            self.assertEqual(entries, ["base"])
            self.assertEqual(conflicts, [])
            self.assertEqual(outbox, [])

        reports.append(self.tick(world))

        self.assertTrue(reports[-1].ok)
        self.assertEqual(
            items,
            ["base", "update"],
        )
        self.assertEqual(
            entries,
            ["base", "update"],
        )
        self.assertEqual(conflicts, ["update"])
        self.assertEqual(outbox, ["update"])

        self.assertIs(world.world, registry)
        self.assertIs(world.entity_memory, memory)
        self.assertIs(world.conflict_history, conflicts)
        self.assertIs(
            world.symbolic_replay_outbox,
            outbox,
        )
        self.assertIs(nested_world["items"], items)
        self.assertIs(
            nested_memory["entries"],
            entries,
        )

        self.assert_manifestations(world, reports)


if __name__ == "__main__":
    unittest.main()
