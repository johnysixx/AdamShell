import io
import random
import unittest

from contextlib import redirect_stdout

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_olfaction import CatOlfaction
from cats.cat_knowledge import CatKnowledge
from cats.cat_exploration_planner import CatExplorationPlanner
from cats.cat_quantum_box_memory_details import (
    CatQuantumBoxObservedMemoryDetails,
)
from core.entity.components import SpatialVector3
from universe.aroma_composition import AromaComposition
from universe.dark_sector import QUANTUM_BOX_ENERGY_COST_J
from universe.universe_tick_result_state import (
    UniverseTickPhaseCompletedResult,
)


class A42CatCognitionIntegrationTests(unittest.TestCase):

    def setUp(self):
        before = random.getstate()
        self.addCleanup(random.setstate, before)

    @staticmethod
    def quiet(operation, *args, **kwargs):
        with redirect_stdout(io.StringIO()):
            return operation(*args, **kwargs)

    @staticmethod
    def pos(x, y=0.0, z=0.0):
        return SpatialVector3(
            x=float(x),
            y=float(y),
            z=float(z),
        )

    def make_world(self, number):
        random.seed(42000 + number)

        world = self.quiet(
            Universe,
            universe_id=f"a42_cat_regression_{number}",
        )

        self.quiet(world.enable_quantum_layer)

        return world

    def make_cat(self, cats, name, position=None):
        cat = self.quiet(
            cats.create_cat,
            name=name,
            color="black",
            fur_length="short",
        )

        self.assertIsNotNone(cat)

        if position is not None:
            cat.position = position

        return cat

    def test_01_cat_vision_and_memory(self):
        world = self.make_world(1)
        cats = self.quiet(Cats, world)

        observer = self.make_cat(
            cats, "observer", self.pos(0)
        )

        self.make_cat(cats, "near", self.pos(2))
        self.make_cat(cats, "far", self.pos(20))

        seen = self.quiet(
            cats.observe_cat, observer
        )

        self.assertIn("near", seen.nearby_cats)
        self.assertNotIn("far", seen.nearby_cats)

        self.assertEqual(
            len(observer.mind.observation_history),
            1,
        )
        self.assertIsNotNone(
            observer.mind.last_observations
        )

    def test_02_olfaction_learning_recognition(self):
        world = self.make_world(2)
        cats = self.quiet(Cats, world)

        observer = self.make_cat(
            cats, "observer", self.pos(0)
        )
        pazuzu = self.make_cat(
            cats, "pazuzu", self.pos(2)
        )

        self.quiet(world.add_entity, observer)
        self.quiet(world.add_entity, pazuzu)

        unknown = self.quiet(
            CatOlfaction.sniff, observer, world
        )

        first = next(
            item
            for item in unknown.detected_aromas
            if item.actual_identity == "cat:pazuzu"
        )

        self.assertFalse(first.recognition.recognized)

        self.quiet(
            cats.learn_cat_aroma,
            observer=observer,
            observed_cat=pazuzu,
        )

        known = self.quiet(
            CatOlfaction.sniff, observer, world
        )

        second = next(
            item
            for item in known.detected_aromas
            if item.actual_identity == "cat:pazuzu"
        )

        self.assertTrue(second.recognition.recognized)
        self.assertEqual(
            second.recognition.identity,
            "cat:pazuzu",
        )

    def test_03_quantum_box_perception_memory(self):
        world = self.make_world(3)
        cats = self.quiet(Cats, world)

        cat = self.make_cat(
            cats, "explorer", self.pos(0)
        )

        box = self.quiet(
            world.create_quantum_box,
            rng=random.Random(303),
            box_id="a42_observed_box",
        )

        box.position = self.pos(2)

        first = self.quiet(cats.observe_cat, cat)

        self.assertIn(
            box.id, first.unexplored_boxes
        )

        self.quiet(
            cat.memory.remember,
            event_type="quantum_box_observed",
            participants=[],
            details=CatQuantumBoxObservedMemoryDetails(
                box_id=box.id,
            ),
        )

        second = self.quiet(cats.observe_cat, cat)

        self.assertNotIn(
            box.id, second.unexplored_boxes
        )

    def test_04_perception_drives_mind_decision(self):
        world = self.make_world(4)
        cats = self.quiet(Cats, world)

        cat = self.make_cat(
            cats, "thinking_cat", self.pos(0)
        )

        cat.personality.traits.curiosity = 1.0
        cat.personality.traits.courage = 0.7

        box = self.quiet(
            world.create_quantum_box,
            rng=random.Random(404),
            box_id="a42_thought_box",
        )

        box.position = self.pos(1)

        observations = self.quiet(
            cats.observe_cat, cat
        )

        decision = self.quiet(
            CatMind.decide,
            cat=cat,
            observations=observations,
        )

        self.assertEqual(
            decision.intention,
            "explore_box",
        )
        self.assertEqual(
            decision.target.box_id,
            box.id,
        )
        self.assertEqual(
            cat.mind.decision_count,
            1,
        )
        self.assertEqual(
            len(cat.mind.history),
            1,
        )

    def test_05_scent_memory_and_navigation(self):
        world = self.make_world(5)
        cats = self.quiet(Cats, world)

        cat = self.make_cat(
            cats, "tracker", self.pos(0)
        )
        cat.current_layer = "quantum_layer"

        for source, point, tick, intensity in (
            ("trace_a", self.pos(1), 10, 0.4),
            ("trace_b", self.pos(4), 20, 0.8),
        ):
            self.quiet(
                CatKnowledge.remember_scent_place,
                cat=cat,
                layer="quantum_layer",
                position=point,
                source_id=source,
                recognized_identity="cat:pazuzu",
                components=AromaComposition.empty(),
                perceived_intensity=intensity,
                universe_tick=tick,
            )

        cat.knowledge.scent_clock_tick = 20

        direction = self.quiet(
            CatKnowledge.infer_scent_direction,
            cat=cat,
            identity="cat:pazuzu",
            layer="quantum_layer",
        )

        self.assertTrue(direction.inferred)
        self.assertEqual(
            direction.from_source_id,
            "trace_a",
        )
        self.assertEqual(
            direction.to_source_id,
            "trace_b",
        )
        self.assertEqual(
            direction.unit_vector,
            self.pos(1),
        )

        destination = self.quiet(
            CatExplorationPlanner.choose_scent_destination,
            cat=cat,
            preferred_identity="cat:pazuzu",
        )

        self.assertTrue(destination.selected)
        self.assertIn(
            destination.position,
            (self.pos(1), self.pos(4)),
        )

    def test_06_autonomous_quantum_exploration(self):
        world = self.make_world(6)
        cats = self.quiet(Cats, world)

        cat = self.make_cat(
            cats,
            "quantum_explorer",
            self.pos(3, 1, 0),
        )

        cat.current_layer = "meeting_place"
        cat.idea_energy = (
            QUANTUM_BOX_ENERGY_COST_J * 10.0
        )
        cat.personality.traits.curiosity = 1.0

        before_energy = cat.idea_energy
        before_boxes = len(world.quantum_boxes)

        result = self.quiet(
            cats.think_and_act,
            cat=cat,
        )

        self.assertTrue(result.completed)
        self.assertEqual(
            result.decision.intention,
            "create_exploration_pair",
        )
        self.assertTrue(result.execution.executed)
        self.assertTrue(
            result.execution.transfer.transferred
        )
        self.assertEqual(
            len(world.quantum_boxes),
            before_boxes + 2,
        )
        self.assertEqual(
            len(world.stable_cat_box_pairs),
            1,
        )
        self.assertEqual(
            cat.current_layer,
            "quantum_layer",
        )
        self.assertLess(
            cat.idea_energy,
            before_energy,
        )

    def test_07_hunt_route_planning(self):
        world = self.make_world(7)

        manifested = self.quiet(
            world.manifest_cat,
            name="hunter",
            source="test",
            position=self.pos(0),
        )

        cat = manifested.cat

        def target(label, position, size):
            cronenberg = self.quiet(
                world.create_cronenberg_from_quantum_error,
                RuntimeError(label),
                "a42",
                "hunt_route",
            )
            cronenberg.position = position
            cronenberg.size = float(size)
            return cronenberg

        far = target("far", self.pos(10), 1.0)
        near = target("near", self.pos(3, 4), 1.0)
        large = target("large", self.pos(1), 2.0)

        route = self.quiet(
            world.quantum_space
            .plan_cat_route_to_nearest_huntable_cronenberg,
            cat,
            [far, near, large],
            step_size=2.0,
        )

        self.assertIs(route.target, near)
        self.assertAlmostEqual(
            route.target_distance,
            5.0,
        )
        self.assertEqual(
            route.route.route_steps[-1],
            near.position,
        )

    def test_08_navigation_offer_acceptance(self):
        world = self.make_world(8)

        manifested = self.quiet(
            world.manifest_cat,
            name="hunter_offer",
            source="test",
            position=self.pos(0),
        )

        cat = manifested.cat
        cats = world.cats_layer

        activation = self.quiet(
            cats.activate_for_cronenberg_overpopulation,
            cat,
        )

        self.assertTrue(activation.activated)

        target = self.quiet(
            world.create_cronenberg_from_quantum_error,
            RuntimeError("navigation target"),
            "a42",
            "navigation_offer",
        )

        target.position = self.pos(3)
        target.size = 1.0

        offer = self.quiet(
            cats.offer_navigation_for_suggested_intent,
            cat,
        )

        self.assertTrue(offer.offered)

        accepted = self.quiet(
            cats.accept_navigation_offer,
            cat,
        )

        self.assertTrue(accepted.accepted)
        self.assertEqual(
            cat.intent,
            "hunt_nearest_cronenberg",
        )
        self.assertEqual(
            cat.active_route_id,
            accepted.route.route_id,
        )

    def test_09_live_multicat_universe(self):
        world = self.make_world(9)

        self.quiet(world.start_big_bang)
        self.quiet(world.boot_physics)

        cats = self.quiet(Cats, world)

        first = self.make_cat(
            cats, "pazuzu", self.pos(0)
        )
        second = self.make_cat(
            cats, "observer", self.pos(2)
        )

        reports = []

        for _ in range(3):
            report = self.quiet(
                world.tick_universe
            )
            reports.append(report)

            self.assertEqual(
                report.error_count,
                0,
                msg=repr([
                    (e.phase, e.error_message)
                    for e in report.errors
                ]),
            )

            phases = [
                phase
                for phase in report.phases
                if phase.phase == "cats"
            ]

            self.assertEqual(len(phases), 1)

            phase = phases[0]

            self.assertIsInstance(
                phase,
                UniverseTickPhaseCompletedResult,
            )

            self.assertFalse(
                phase.result.errors,
                msg=repr(phase.result.errors),
            )

        self.assertEqual(
            [report.tick for report in reports],
            [1, 2, 3],
        )
        self.assertEqual(world.universe_tick, 3)
        self.assertEqual(cats.tick_count, 3)
        self.assertEqual(
            world.quantum_state.tick_count,
            3,
        )
        self.assertEqual(
            world.life_cycle_system.day,
            3,
        )
        self.assertEqual(
            world.spacetime.time_axis.tick,
            3,
        )
        self.assertIn(first, cats.cats)
        self.assertIn(second, cats.cats)
        self.assertEqual(
            [s.tick for s in world.universe_history],
            [1, 2, 3],
        )
        self.assertEqual(
            world.cronenberg_count,
            0,
        )


if __name__ == "__main__":
    unittest.main()
