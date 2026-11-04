import unittest

from core.existence.reality import Reality


class MutableProcess:

    def __init__(self):
        self.state = {
            "type": "mutable_process",
            "metadata": {
                "values": ["original"],
            },
        }

    @property
    def public_state(self):
        return self.state


class RealityPublicStateTests(unittest.TestCase):

    def test_public_state_detaches_nested_process_data(self):
        reality = Reality()
        process = MutableProcess()

        reality.add_natural_process(process)

        first = reality.public_state
        second = reality.public_state

        first["natural_processes"][0][
            "metadata"
        ]["values"].append("snapshot_only")

        self.assertEqual(
            process.state["metadata"]["values"],
            ["original"],
        )

        self.assertEqual(
            second["natural_processes"][0][
                "metadata"
            ]["values"],
            ["original"],
        )

        self.assertIs(
            reality.natural_processes[0],
            process,
        )

    def test_snapshot_ignores_later_live_changes(self):
        reality = Reality()
        process = MutableProcess()

        reality.add_natural_process(process)

        snapshot = reality.public_state

        process.state["metadata"]["values"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot["natural_processes"][0][
                "metadata"
            ]["values"],
            ["original"],
        )

        self.assertEqual(
            reality.public_state["natural_processes"][0][
                "metadata"
            ]["values"],
            ["original", "live_change"],
        )

    def test_process_without_public_state_uses_fallback(self):
        class NoSnapshotProcess:
            pass

        reality = Reality()
        process = NoSnapshotProcess()

        self.assertTrue(
            reality.add_natural_process(process)
        )

        self.assertEqual(
            reality.public_state,
            {
                "natural_process_count": 1,
                "natural_processes": [
                    {
                        "type": "NoSnapshotProcess",
                    },
                ],
            },
        )

        self.assertIs(
            reality.natural_processes[0],
            process,
        )

        self.assertTrue(
            reality.remove_natural_process(process)
        )

        self.assertEqual(
            reality.public_state["natural_process_count"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
