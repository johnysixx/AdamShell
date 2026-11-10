import io
import random
import unittest

from contextlib import redirect_stdout

from universe.universe import Universe
from cats.cats import Cats
from core.entity.components import SpatialVector3
from quantum.error_boundary import QuantumErrorResult
from universe.dark_sector import QUANTUM_BOX_ENERGY_COST_J
from universe.universe_tick_result_state import (
    UniverseTickPhaseCompletedResult,
)


class A42WorldConsistencyIntegrationTests(unittest.TestCase):

    def setUp(self):
        original_rng = random.getstate()
        self.addCleanup(
            random.setstate,
            original_rng,
        )

    @staticmethod
    def quiet(operation, *args, **kwargs):
        with redirect_stdout(io.StringIO()):
            return operation(*args, **kwargs)

    @staticmethod
    def position(x, y=0.0, z=0.0):
        return SpatialVector3(
            x=float(x),
            y=float(y),
            z=float(z),
        )

    def make_world(self, number):
        random.seed(43000 + number)

        world = self.quiet(
            Universe,
            universe_id=f"a42_consistency_{number}",
        )

        self.quiet(
            world.enable_quantum_layer
        )

        return world

    @staticmethod
    def events(world, event_name):
        return [
            event
            for event in world.quantum_events
            if getattr(event, "name", None)
            == event_name
        ]

    def assert_quantum_registry(self, world):
        active = {
            box.id: box
            for box in world.quantum_boxes
        }

        self.assertEqual(
            len(active),
            len(world.quantum_boxes),
            "Duplicate live QuantumBox ID.",
        )

        created = self.events(
            world, "quantum_box_created"
        )

        disappeared = self.events(
            world, "quantum_box_disappeared"
        )

        collapsed = self.events(
            world, "quantum_box_collapsed"
        )

        manifested = self.events(
            world, "cat_manifested"
        )

        created_ids = [
            event.box_id
            for event in created
        ]

        disappeared_ids = [
            event.box_id
            for event in disappeared
        ]

        self.assertEqual(
            len(created_ids),
            len(set(created_ids)),
            "Duplicate creation event.",
        )

        self.assertEqual(
            len(disappeared_ids),
            len(set(disappeared_ids)),
            "Duplicate disappearance event.",
        )

        self.assertTrue(
            set(disappeared_ids).issubset(
                set(created_ids)
            ),
            "Disappearance references unknown box.",
        )

        self.assertTrue(
            set(active).isdisjoint(
                set(disappeared_ids)
            ),
            "Disappeared box remains active.",
        )

        self.assertEqual(
            set(active) | set(disappeared_ids),
            set(created_ids),
            "Live boxes and history diverged.",
        )

        self.assertEqual(
            world.statistics.total_quantum_boxes_created,
            len(created),
        )

        self.assertEqual(
            world.statistics.total_quantum_boxes_disappeared,
            len(disappeared),
        )

        self.assertEqual(
            world.statistics.total_quantum_collapses,
            len(collapsed),
        )

        self.assertEqual(
            world.statistics.total_cats_created,
            len(manifested),
        )

        for event in created + disappeared:
            self.assertLessEqual(
                event.tick,
                world.quantum_state.tick_count,
            )

        return {
            "created": len(created),
            "disappeared": len(disappeared),
            "collapsed": len(collapsed),
            "manifested": len(manifested),
            "active": len(active),
        }

    def assert_cat_registry(self, world):
        cats = getattr(
            world,
            "cats_layer",
            None,
        )

        if cats is None:
            return 0

        self.assertIs(
            world.world.get("cats_state"),
            cats.cats_state,
        )

        self.assertIs(
            world.world["cats"]["cats"],
            cats.cats,
        )

        self.assertEqual(
            len({
                id(cat)
                for cat in cats.cats
            }),
            len(cats.cats),
            "Duplicate Cat object reference.",
        )

        for event in self.events(
            world,
            "cat_manifested",
        ):
            matches = [
                cat
                for cat in cats.cats
                if cat.name == event.cat_name
            ]

            self.assertEqual(
                len(matches),
                1,
                "Manifested cat missing or duplicated.",
            )

            linked_entities = [
                entity
                for entity in world.entities
                if getattr(
                    entity, "cat_data", None
                ) is matches[0]
            ]

            self.assertEqual(
                len(linked_entities),
                1,
                "Manifested cat entity link mismatch.",
            )

        return len(cats.cats)

    def assert_live_tick(self, world, tick_number):
        report = self.quiet(
            world.tick_universe
        )

        self.assertEqual(
            report.tick,
            tick_number,
        )

        self.assertFalse(
            report.errors,
            msg=repr(report.errors),
        )

        for phase in report.phases:
            if not isinstance(
                phase,
                UniverseTickPhaseCompletedResult,
            ):
                continue

            result = phase.result

            if isinstance(
                result,
                QuantumErrorResult,
            ):
                self.fail(
                    f"Hidden quantum error at "
                    f"tick {tick_number}, "
                    f"phase {phase.phase}: "
                    f"{result.error_type}: "
                    f"{result.error_message}"
                )

            if phase.phase == "cats":
                self.assertFalse(
                    result.errors,
                    msg=repr(result.errors),
                )

        self.assertEqual(
            len(world.universe_history),
            tick_number,
        )

        snapshot = world.universe_history[-1]

        self.assertEqual(
            snapshot.tick,
            tick_number,
        )

        self.assertEqual(
            snapshot.energy,
            world.energy_pool,
        )

        self.assertEqual(
            snapshot.entropy,
            world.entropy,
        )

        self.assertEqual(
            snapshot.pressure,
            world.pressure,
        )

        self.assertEqual(
            len(
                world.cronenberg_population_statistics
                .history
            ),
            tick_number,
        )

        self.assertEqual(
            world.cronenberg_count,
            len(world.cronenbergs),
        )

        self.assertEqual(
            world.quantum_state.tick_count,
            tick_number,
        )

        self.assertEqual(
            len(world.quantum_clock_events),
            tick_number,
        )

        if world.spacetime is not None:
            self.assertEqual(
                snapshot.curvature,
                world.spacetime.curvature,
            )

        self.assert_quantum_registry(world)
        self.assert_cat_registry(world)

        return report

    def test_01_box_registry_history_layers(self):
        world = self.make_world(1)

        boxes = []

        for index, (seed, layer) in enumerate(
            (
                (101, "quantum_layer"),
                (202, "meeting_place"),
                (303, "quantum_layer"),
            ),
            start=1,
        ):
            box = self.quiet(
                world.create_quantum_box,
                rng=random.Random(seed),
                box_id=(
                    f"a42_consistency_box_{index}"
                ),
                layer=layer,
            )

            boxes.append(box)

        state = self.assert_quantum_registry(world)

        self.assertEqual(state["created"], 3)
        self.assertEqual(state["active"], 3)

        creation_events = self.events(
            world,
            "quantum_box_created",
        )

        for box, event in zip(
            boxes,
            creation_events,
        ):
            self.assertEqual(
                box.id,
                event.box_id,
            )

            self.assertEqual(
                box.position,
                event.position,
            )

            self.assertEqual(
                box.current_layer,
                event.layer,
            )

            self.assertEqual(event.tick, 0)

        visible = world.snapshot[
            "quantum_layer_map"
        ]["boxes"]

        self.assertEqual(
            {
                item["id"]
                for item in visible
            },
            {
                boxes[0].id,
                boxes[2].id,
            },
        )

    def test_02_opening_and_manifested_cat_links(self):
        world = self.make_world(2)

        empty = self.quiet(
            world.create_quantum_box,
            rng=random.Random(11),
            box_id="a42_empty",
        )

        cat_box = self.quiet(
            world.create_quantum_box,
            rng=random.Random(22),
            box_id="a42_cat",
        )

        empty_result = self.quiet(
            world.open_quantum_box,
            empty.id,
            rng=random.Random(1),
        )

        cat_result = self.quiet(
            world.open_quantum_box,
            cat_box.id,
            rng=random.Random(0),
        )

        self.assertEqual(
            empty_result.name,
            "empty_quantum_box_opened",
        )

        self.assertEqual(
            cat_result.name,
            "cat_manifested",
        )

        self.assertEqual(
            cat_result.box_id,
            cat_box.id,
        )

        self.assertEqual(
            world.quantum_boxes,
            [],
        )

        self.assertEqual(
            self.assert_quantum_registry(world),
            {
                "created": 2,
                "disappeared": 2,
                "collapsed": 2,
                "manifested": 1,
                "active": 0,
            },
        )

        self.assertEqual(
            self.assert_cat_registry(world),
            1,
        )

    def test_03_replay_independent_of_source(self):
        source = self.make_world(3)

        original = self.quiet(
            source.create_quantum_box,
            rng=random.Random(333),
            box_id="a42_replay_independent",
        )

        event = self.events(
            source,
            "quantum_box_created",
        )[0]

        target = self.make_world(30)

        restored = self.quiet(
            target.replay_quantum_box_created,
            event,
        )

        self.assertIsNot(
            restored,
            original,
        )

        self.assertEqual(
            restored.public_state,
            original.public_state,
        )

        self.assertEqual(
            target.quantum_events,
            [],
        )

        self.assertEqual(
            target.statistics.total_quantum_boxes_created,
            1,
        )

        target_before = restored.public_state

        self.quiet(
            source.open_quantum_box,
            original.id,
            rng=random.Random(1),
        )

        self.assertEqual(
            source.quantum_boxes,
            [],
        )

        self.assertEqual(
            len(target.quantum_boxes),
            1,
        )

        self.assertIs(
            target.quantum_boxes[0],
            restored,
        )

        self.assertEqual(
            restored.public_state,
            target_before,
        )

        self.assert_quantum_registry(source)

        # The replay deliberately does not emit events
        # into the target's source-event history.

    def test_04_stable_pair_reference_integrity(self):
        world = self.make_world(4)
        cats = self.quiet(Cats, world)

        cat = self.quiet(
            cats.create_cat,
            name="a42_pair_creator",
            color="black",
            fur_length="short",
        )

        cat.position = self.position(3, 1)
        cat.current_layer = "meeting_place"
        cat.idea_energy = (
            QUANTUM_BOX_ENERGY_COST_J * 10
        )
        cat.personality.traits.curiosity = 1.0

        thought = self.quiet(
            cats.think_and_act,
            cat=cat,
        )

        self.assertTrue(thought.completed)
        self.assertTrue(
            thought.execution.executed
        )
        self.assertTrue(
            thought.execution.transfer.transferred
        )

        self.assertEqual(
            len(world.stable_cat_box_pairs),
            1,
        )

        pair = world.stable_cat_box_pairs[0]

        live = {
            box.id: box
            for box in world.quantum_boxes
        }

        self.assertTrue(pair.active)
        self.assertTrue(pair.stable)

        self.assertEqual(
            pair.box_ids,
            frozenset(live),
        )

        anchor = live[pair.anchor_box_id]
        remote = live[pair.remote_box_id]

        self.assertEqual(
            anchor.current_layer,
            pair.anchor_layer,
        )

        self.assertEqual(
            remote.current_layer,
            pair.remote_layer,
        )

        self.assertEqual(
            anchor.quantum_counterpart.box_id,
            remote.id,
        )

        self.assertEqual(
            remote.quantum_counterpart.box_id,
            anchor.id,
        )

        self.assertEqual(
            cat.quantum_transfer.stable_pair_id,
            pair.pair_id,
        )

        self.assertEqual(
            cat.current_layer,
            pair.remote_layer,
        )

        self.assert_quantum_registry(world)
        self.assert_cat_registry(world)

    def test_05_cronenberg_entity_event_statistics(self):
        world = self.make_world(5)

        cronenberg = self.quiet(
            world.create_cronenberg_from_quantum_error,
            RuntimeError(
                "a42_consistency_injected_error"
            ),
            "a42",
            "consistency_probe",
        )

        matching = self.events(
            world,
            "cronenberg_manifested",
        )

        self.assertEqual(
            len(matching),
            1,
        )

        self.assertEqual(
            matching[0].cronenberg_id,
            cronenberg.id,
        )

        self.assertEqual(
            len(world.cronenbergs),
            1,
        )

        self.assertIs(
            world.cronenbergs[0],
            cronenberg,
        )

        self.assertEqual(
            sum(
                entity is cronenberg
                for entity in world.entities
            ),
            1,
        )

        self.assertEqual(
            world.cronenberg_count,
            1,
        )

        for tick in range(1, 4):
            self.assert_live_tick(
                world,
                tick,
            )

        population = (
            world.cronenberg_population_statistics
            .history[-1].snapshot
        )

        self.assertEqual(
            population.total_count,
            len(world.cronenbergs),
        )

    def test_06_live_cross_registry_60_ticks(self):
        world = self.make_world(6)

        self.quiet(world.start_big_bang)
        self.quiet(world.boot_physics)

        cats = self.quiet(Cats, world)

        first = self.quiet(
            cats.create_cat,
            name="a42_pazuzu",
            color="black",
            fur_length="short",
        )

        second = self.quiet(
            cats.create_cat,
            name="a42_observer",
            color="gray",
            fur_length="short",
        )

        first.position = self.position(0)
        second.position = self.position(2)

        self.quiet(
            world.create_quantum_box,
            rng=random.Random(606),
            box_id="a42_runtime_box",
        )

        canonical_cats = cats.cats
        canonical_spacetime = world.spacetime

        for tick in range(1, 61):
            self.assert_live_tick(
                world,
                tick,
            )

            self.assertIs(
                world.spacetime,
                canonical_spacetime,
            )

            self.assertIs(
                cats.cats,
                canonical_cats,
            )

            self.assertEqual(
                cats.tick_count,
                tick,
            )

            self.assertEqual(
                world.life_cycle_system.day,
                tick,
            )

            self.assertEqual(
                world.spacetime.time_axis.tick,
                tick,
            )

            self.assertIn(
                first,
                cats.cats,
            )

            self.assertIn(
                second,
                cats.cats,
            )

        self.assert_quantum_registry(world)

    def test_07_snapshot_detachment(self):
        world = self.make_world(7)

        box = self.quiet(
            world.create_quantum_box,
            rng=random.Random(707),
            box_id="a42_snapshot_box",
        )

        initial_position = box.position

        snapshot = world.snapshot
        statistics = world.statistics.public_state

        snapshot["statistics"][
            "total_quantum_boxes_created"
        ] = -999

        snapshot["quantum_layer_map"][
            "boxes"
        ][0]["position"]["x"] = 999.0

        statistics[
            "total_quantum_boxes_created"
        ] = -999

        self.assertEqual(
            world.statistics.total_quantum_boxes_created,
            1,
        )

        self.assertEqual(
            box.position,
            initial_position,
        )

        fresh = world.snapshot

        self.assertEqual(
            fresh["statistics"][
                "total_quantum_boxes_created"
            ],
            1,
        )

        self.assertEqual(
            fresh["quantum_layer_map"][
                "boxes"
            ][0]["position"]["x"],
            initial_position.x,
        )

        self.assert_quantum_registry(world)


if __name__ == "__main__":
    unittest.main()
