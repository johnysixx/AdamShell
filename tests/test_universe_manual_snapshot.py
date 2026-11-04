import unittest
from types import SimpleNamespace

from meeting_place.universe_manual import UniverseManual
from multiverse.registry import UniverseRegistry


class UniverseManualSnapshotTests(unittest.TestCase):

    def make_manual(self):
        registry = UniverseRegistry()

        universe_id = registry.register_universe(
            name="test_universe",
        )

        registry.universes[universe_id][
            "metadata"
        ] = {
            "nested": {
                "values": ["original"],
            },
        }

        manual = UniverseManual(registry)
        bartender = SimpleNamespace(name="bartender")

        return registry, manual, bartender, universe_id

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
            original["metadata"]["nested"]["values"],
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

        registry.universes[universe_id][
            "metadata"
        ]["nested"]["values"].append(
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
