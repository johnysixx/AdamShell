import unittest
from dataclasses import FrozenInstanceError, dataclass
from types import SimpleNamespace

from gods.god_memory_state import (
    GodHistoricalValue,
    GodMemoryNote,
    GodMemorySnapshot,
    GodObservationFact,
    GodSharedMemory,
)
from idea_universe.primordial_stellar_state import (
    PrimordialNebulaRemnant,
)
from quantum.director_state import (
    QuantumDirectorArrivedAtBarEvent,
    QuantumDirectorMaterialSample,
    QuantumDirectorNebulaStudiedEvent,
    QuantumDirectorStarExplodedEvent,
)


@dataclass
class MutableEvent:
    event: str = "mutable_event"


@dataclass(frozen=True)
class UnrelatedFrozenEvent:
    event: str = "unrelated_event"


class GodMemoryHistoryFactsTests(unittest.TestCase):

    def test_rejects_untyped_and_mutable_events(self):
        memory = GodSharedMemory()

        rejected = (
            {"event": "mapping"},
            SimpleNamespace(event="mutable"),
            MutableEvent(),
            UnrelatedFrozenEvent(),
        )

        for event in rejected:
            with self.subTest(event=type(event).__name__):
                with self.assertRaises(TypeError):
                    memory.record(event)

        self.assertEqual(memory.record_count, 0)
        self.assertEqual(memory.state.facts, ())

    def test_historical_subject_values_do_not_change(self):
        subject = SimpleNamespace(
            name="primordial_nebula",
            type="primordial_nebula",
            stage="before",
            size=10.0,
        )

        event = QuantumDirectorNebulaStudiedEvent(
            subject=subject,
            finding="liquid_hydrocarbons_identified",
            amount=5.0,
        )

        memory = GodSharedMemory()
        before = memory.state

        memory.record(event)

        recorded = memory.state
        fact = memory.fact_at(0)

        self.assertIs(
            memory.record_at(0),
            event,
        )

        self.assertIsNot(recorded, before)
        self.assertEqual(before.facts, ())

        subject.name = "renamed_nebula"
        subject.stage = "after"
        subject.size = 99.0

        # Live event deliberately retains original identity.
        self.assertEqual(
            event.subject.stage,
            "after",
        )

        # Historical facts remain captured at record time.
        self.assertEqual(
            fact.value_for("subject.name"),
            "primordial_nebula",
        )

        self.assertEqual(
            fact.value_for("subject.stage"),
            "before",
        )

        self.assertEqual(
            fact.value_for("subject.size"),
            10.0,
        )

        self.assertEqual(
            fact.value_for("finding"),
            "liquid_hydrocarbons_identified",
        )

        self.assertEqual(
            fact.value_for("amount"),
            5.0,
        )

        with self.assertRaises(FrozenInstanceError):
            fact.event = "changed"

        with self.assertRaises(FrozenInstanceError):
            fact.entries[0].value = "changed"

    def test_remnant_mapping_is_captured_as_scalar_facts(self):
        remnant = PrimordialNebulaRemnant(
            source="first_star",
            elemental_potentials={
                "hydrogen": 1.0,
                "carbon": 2.0,
            },
        )

        event = QuantumDirectorStarExplodedEvent(
            subject=SimpleNamespace(
                name="first_star",
            ),
            remnant=remnant,
        )

        memory = GodSharedMemory()
        memory.record(event)

        fact = memory.fact_at(0)

        remnant.elemental_potentials["carbon"] = 99.0

        self.assertIs(memory.record_at(0), event)

        self.assertEqual(
            fact.value_for("remnant.source"),
            "first_star",
        )

        self.assertEqual(
            fact.value_for(
                "remnant.elemental_potentials.carbon"
            ),
            2.0,
        )

        self.assertEqual(
            fact.value_for(
                "remnant.elemental_potentials.hydrogen"
            ),
            1.0,
        )

    def test_bar_sample_and_encounter_facts(self):
        serpent = SimpleNamespace(
            name="serpent",
            type="idea_entity",
        )

        sample = QuantumDirectorMaterialSample(
            material="liquid_hydrocarbons",
            amount=3.0,
        )

        event = QuantumDirectorArrivedAtBarEvent(
            sample=sample,
            serpent_present=True,
            met=serpent,
            taught_cocktail="raspberry_rum",
        )

        memory = GodSharedMemory()
        memory.record(event)

        serpent.name = "changed"

        fact = memory.fact_at(0)

        self.assertEqual(
            fact.value_for("sample.material"),
            "liquid_hydrocarbons",
        )

        self.assertEqual(
            fact.value_for("sample.amount"),
            3.0,
        )

        self.assertEqual(
            fact.value_for("met.name"),
            "serpent",
        )

        self.assertTrue(
            fact.value_for("serpent_present")
        )

        self.assertEqual(
            fact.value_for("taught_cocktail"),
            "raspberry_rum",
        )

    def test_knowledge_update_preserves_recorded_facts(self):
        memory = GodSharedMemory()

        note = GodMemoryNote("cosmos_ordered")
        memory.record(note)

        first = memory.state
        fact = memory.fact_at(0)

        memory.learn("tiamat_defeated")

        self.assertIsNot(memory.state, first)
        self.assertIs(memory.record_at(0), note)
        self.assertIs(memory.fact_at(0), fact)

        self.assertEqual(first.knowledge, ())
        self.assertEqual(
            memory.state.knowledge,
            ("tiamat_defeated",),
        )

        self.assertEqual(
            fact.event,
            "cosmos_ordered",
        )

    def test_snapshot_rejects_unpaired_or_untyped_facts(self):
        note = GodMemoryNote("first")

        with self.assertRaises(ValueError):
            GodMemorySnapshot(
                observations=(note,),
            )

        with self.assertRaises(TypeError):
            GodMemorySnapshot(
                observations=(note,),
                facts=({},),
            )

        with self.assertRaises(TypeError):
            GodObservationFact(
                event="first",
                entries=[],
            )

        with self.assertRaises(TypeError):
            GodHistoricalValue(
                name="invalid",
                value={},
            )

    def test_historical_fact_has_no_mapping_interface(self):
        memory = GodSharedMemory()

        memory.record(
            GodMemoryNote("first")
        )

        fact = memory.fact_at(0)

        for method in (
            "get",
            "items",
            "keys",
            "values",
        ):
            self.assertFalse(
                hasattr(fact, method)
            )

        with self.assertRaises(TypeError):
            _ = fact["event"]


if __name__ == "__main__":
    unittest.main()
