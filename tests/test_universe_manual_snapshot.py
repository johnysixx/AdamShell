import unittest
from types import SimpleNamespace

from meeting_place.universe_manual import UniverseManual
from multiverse.registry import (
    UniverseRegistry,
    UniverseRegistryRecord,
)


class UniverseManualSnapshotTests(unittest.TestCase):

    def make_manual(self):
        registry = UniverseRegistry()

        universe_id = registry.register_universe(
            name="test_universe",
        )

        registry.universes[universe_id].metadata = {
            "nested": {
                "values": ["original"],
            },
        }

        manual = UniverseManual(registry)
        bartender = SimpleNamespace(name="bartender")

        return registry, manual, bartender, universe_id

    def test_registry_uses_canonical_record_objects(self):
        registry = UniverseRegistry()

        self.assertEqual(
            tuple(registry.universes),
            (0, 0.5),
        )

        for universe_id, record in registry.universes.items():
            self.assertIsInstance(
                record,
                UniverseRegistryRecord,
            )
            self.assertEqual(
                record.id,
                universe_id,
            )

            for method in ("get", "keys", "items", "values"):
                self.assertFalse(
                    hasattr(record, method)
                )

            with self.assertRaises(TypeError):
                _ = record["name"]

        self.assertEqual(
            registry.universes[0].to_dict(),
            {
                "id": 0,
                "name": "multiverse",
                "type": "multiverse",
            },
        )

        self.assertEqual(
            registry.universes[0.5].to_dict(),
            {
                "id": 0.5,
                "name": "quantum_layer",
                "type": "quantum_layer",
            },
        )

    def test_registration_reuses_canonical_object(self):
        registry = UniverseRegistry()

        universe_id = registry.register_universe(
            name="test_world",
            universe_type="physical_universe",
        )

        record = registry.universes[universe_id]

        self.assertIsInstance(
            record,
            UniverseRegistryRecord,
        )

        self.assertEqual(
            record.type,
            "physical_universe",
        )

        self.assertEqual(
            registry.register_universe("test_world"),
            universe_id,
        )

        self.assertIs(
            registry.universes[universe_id],
            record,
        )

        self.assertEqual(
            registry.ids_by_name["test_world"],
            universe_id,
        )

        self.assertEqual(
            registry.next_universe_id,
            universe_id + 1,
        )

    def test_record_metadata_is_detached_and_manual_is_typed(self):
        source = {
            "nested": {
                "values": ["original"],
            },
        }

        record = UniverseRegistryRecord(
            id=3,
            name="isolated_world",
            type="universe",
            metadata=source,
        )

        source["nested"]["values"].append("external")

        self.assertEqual(
            record.metadata["nested"]["values"],
            ["original"],
        )

        first = record.to_dict()
        first["metadata"]["nested"]["values"].append(
            "snapshot_only"
        )

        self.assertEqual(
            record.metadata["nested"]["values"],
            ["original"],
        )

        with self.assertRaises(TypeError):
            UniverseRegistryRecord(
                id=4,
                name="bad",
                type="universe",
                metadata=[],
            )

        registry, manual, bartender, universe_id = (
            self.make_manual()
        )

        original = registry.universes[universe_id]

        try:
            registry.universes[universe_id] = {
                "id": universe_id,
                "name": "legacy",
                "type": "universe",
            }

            with self.assertRaises(TypeError):
                manual.read(bartender)

        finally:
            registry.universes[universe_id] = original

        self.assertEqual(
            manual.read(bartender)[universe_id]["name"],
            "test_universe",
        )

    def test_read_detaches_nested_registry_data(self):
        registry, manual, bartender, universe_id = (
            self.make_manual()
        )

        original = registry.universes[universe_id]

        first = manual.read(bartender)
        second = manual.read(bartender)

        first[universe_id]["metadata"][
            "nested"
        ]["values"].append("snapshot_only")

        self.assertEqual(
            original.metadata["nested"]["values"],
            ["original"],
        )

        self.assertEqual(
            second[universe_id]["metadata"][
                "nested"
            ]["values"],
            ["original"],
        )

        self.assertIs(
            registry.universes[universe_id],
            original,
        )

        self.assertIsNot(
            first[universe_id],
            original,
        )

    def test_read_snapshot_ignores_later_changes(self):
        registry, manual, bartender, universe_id = (
            self.make_manual()
        )

        snapshot = manual.read(bartender)

        registry.universes[universe_id].metadata[
            "nested"
        ]["values"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot[universe_id]["metadata"][
                "nested"
            ]["values"],
            ["original"],
        )

        self.assertEqual(
            manual.read(bartender)[universe_id][
                "metadata"
            ]["nested"]["values"],
            ["original", "live_change"],
        )

    def test_access_control_and_public_state_preserved(self):
        registry, manual, bartender, universe_id = (
            self.make_manual()
        )

        unauthorized = SimpleNamespace(
            name="cat",
        )

        self.assertIsNone(
            manual.read(unauthorized)
        )

        self.assertIsNone(
            manual.read(None)
        )

        snapshot = manual.read(bartender)

        self.assertIn(
            universe_id,
            snapshot,
        )

        self.assertEqual(
            snapshot[universe_id]["name"],
            "test_universe",
        )

        self.assertEqual(
            manual.public_state[
                "registered_universe_count"
            ],
            len(registry.universes),
        )

        self.assertEqual(
            manual.allowed_reader,
            "bartender",
        )


if __name__ == "__main__":
    unittest.main()
