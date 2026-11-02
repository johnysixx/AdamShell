import unittest

from gods.god_memory_state import GodSharedMemory
from idea_universe import IdeaUniverse
from idea_universe.primordial_idea_star import (
    PrimordialIdeaStar,
)
from idea_universe.primordial_nebula import (
    PrimordialNebula,
)
from multiverse import UniverseRegistry
from quantum.director_state import (
    QuantumDirectorNebulaCreatedEvent,
    QuantumDirectorStarCreatedEvent,
)
from universe.universe import Universe


class PrimordialCanonicalIdentityTests(unittest.TestCase):

    def _layer(self, universe_id="identity_replay"):
        universe = Universe(
            universe_id=universe_id,
        )
        universe.universe_registry = UniverseRegistry()

        layer = IdeaUniverse(universe)
        layer.stellar_epoch_started = True

        return layer

    def test_stars_get_distinct_canonical_ids(self):
        layer = self._layer()

        first = layer.create_primordial_star()
        second = layer.create_primordial_star()

        self.assertIsNot(first, second)
        self.assertEqual(first.name, second.name)

        self.assertEqual(
            first.id,
            "identity_replay:idea_universe:1:"
            "primordial_star:1",
        )
        self.assertEqual(
            second.id,
            "identity_replay:idea_universe:1:"
            "primordial_star:2",
        )

        first.ignite()
        first.explode()

        self.assertTrue(first.id.endswith(":1"))

        with self.assertRaises(AttributeError):
            first.id = "changed"

    def test_nebulae_get_distinct_canonical_ids(self):
        layer = self._layer()

        first_epoch = layer.run_primordial_stellar_epoch(
            star_count=2,
        )

        second_epoch = layer.run_primordial_stellar_epoch(
            star_count=1,
        )

        first = first_epoch.primordial_nebula
        second = second_epoch.primordial_nebula

        self.assertIsNot(first, second)
        self.assertEqual(first.name, second.name)

        self.assertEqual(
            first.id,
            "identity_replay:idea_universe:1:"
            "primordial_nebula:1",
        )
        self.assertEqual(
            second.id,
            "identity_replay:idea_universe:1:"
            "primordial_nebula:2",
        )

        first.tick()

        self.assertTrue(first.id.endswith(":1"))
        self.assertEqual(
            first.public_state["id"],
            first.id,
        )

        with self.assertRaises(AttributeError):
            first.id = "changed"

    def test_same_creation_sequence_replays_same_ids(self):
        first = self._layer()
        second = self._layer()

        def create_sequence(layer):
            early_star = layer.create_primordial_star()

            first_epoch = (
                layer.run_primordial_stellar_epoch(
                    star_count=2,
                )
            )

            second_epoch = (
                layer.run_primordial_stellar_epoch(
                    star_count=1,
                )
            )

            return (
                early_star.id,
                tuple(
                    star.id for star in first_epoch.stars
                ),
                first_epoch.primordial_nebula.id,
                tuple(
                    star.id for star in second_epoch.stars
                ),
                second_epoch.primordial_nebula.id,
            )

        first_ids = create_sequence(first)
        second_ids = create_sequence(second)

        self.assertEqual(first_ids, second_ids)

        flattened = (
            (first_ids[0],)
            + first_ids[1]
            + (first_ids[2],)
            + first_ids[3]
            + (first_ids[4],)
        )

        self.assertEqual(
            len(flattened),
            len(set(flattened)),
        )

    def test_history_distinguishes_same_named_stars(self):
        layer = self._layer()

        first = layer.create_primordial_star()
        second = layer.create_primordial_star()

        memory = GodSharedMemory()

        memory.record(
            QuantumDirectorStarCreatedEvent(
                subject=first,
            )
        )

        memory.record(
            QuantumDirectorStarCreatedEvent(
                subject=second,
            )
        )

        first_fact = memory.fact_at(0)
        second_fact = memory.fact_at(1)

        self.assertNotEqual(first_fact, second_fact)

        self.assertEqual(
            first_fact.value_for("subject.id"),
            first.id,
        )

        self.assertEqual(
            second_fact.value_for("subject.id"),
            second.id,
        )

        self.assertEqual(
            first_fact.value_for("subject.name"),
            second_fact.value_for("subject.name"),
        )

    def test_history_distinguishes_same_named_nebulae(self):
        layer = self._layer()

        first = layer.run_primordial_stellar_epoch(
            star_count=1,
        ).primordial_nebula

        second = layer.run_primordial_stellar_epoch(
            star_count=1,
        ).primordial_nebula

        memory = GodSharedMemory()

        memory.record(
            QuantumDirectorNebulaCreatedEvent(
                subject=first,
            )
        )

        memory.record(
            QuantumDirectorNebulaCreatedEvent(
                subject=second,
            )
        )

        self.assertNotEqual(
            memory.fact_at(0),
            memory.fact_at(1),
        )

        self.assertEqual(
            memory.fact_at(0).value_for("subject.id"),
            first.id,
        )

        self.assertEqual(
            memory.fact_at(1).value_for("subject.id"),
            second.id,
        )

    def test_unowned_objects_cannot_enter_history(self):
        memory = GodSharedMemory()

        candidates = (
            QuantumDirectorStarCreatedEvent(
                subject=PrimordialIdeaStar(),
            ),
            QuantumDirectorNebulaCreatedEvent(
                subject=PrimordialNebula(),
            ),
        )

        original = memory.state

        for event in candidates:
            with self.subTest(event=event.event):
                with self.assertRaisesRegex(
                    TypeError,
                    "canonical entity ID",
                ):
                    memory.record(event)

        self.assertIs(memory.state, original)
        self.assertEqual(memory.record_count, 0)

    def test_direct_explicit_ids_are_supported(self):
        star = PrimordialIdeaStar(
            object_id="external:star:1",
        )

        nebula = PrimordialNebula(
            object_id="external:nebula:1",
        )

        self.assertEqual(star.id, "external:star:1")
        self.assertEqual(nebula.id, "external:nebula:1")

        memory = GodSharedMemory()

        memory.record(
            QuantumDirectorStarCreatedEvent(
                subject=star,
            )
        )

        memory.record(
            QuantumDirectorNebulaCreatedEvent(
                subject=nebula,
            )
        )

        self.assertEqual(
            memory.fact_at(0).value_for("subject.id"),
            star.id,
        )

        self.assertEqual(
            memory.fact_at(1).value_for("subject.id"),
            nebula.id,
        )

    def test_rejects_invalid_explicit_ids(self):
        for cls in (
            PrimordialIdeaStar,
            PrimordialNebula,
        ):
            for bad_id in ("", "   ", 123, {}):
                with self.subTest(
                    cls=cls.__name__,
                    bad_id=repr(bad_id),
                ):
                    with self.assertRaises(ValueError):
                        cls(object_id=bad_id)

    def test_failed_creation_does_not_advance_sequence(self):
        layer = self._layer()
        layer.stellar_epoch_started = False

        with self.assertRaises(RuntimeError):
            layer.create_primordial_star()

        layer.stellar_epoch_started = True
        star = layer.create_primordial_star()

        self.assertTrue(
            star.id.endswith(":primordial_star:1")
        )


if __name__ == "__main__":
    unittest.main()
