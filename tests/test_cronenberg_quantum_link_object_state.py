import unittest

from core.entity.cronenberg_system.quantum_links import (
    CronenbergQuantumLink,
    CronenbergQuantumLinks,
)
from universe.universe import Universe


class CronenbergQuantumLinkObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(self, value):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method
                )
            )

        with self.assertRaises(TypeError):
            _ = value["target_id"]

    def test_live_link_has_no_mapping_api(
        self
    ):
        links = CronenbergQuantumLinks(
            owner_id="source"
        )

        event = links.add_link(
            target_id="target",
            link_type="quantum_counterpart",
            strength=0.75,
            created_tick=4,
        )

        self.assertEqual(len(links.links), 1)
        link = links.links[0]
        self.assertIsInstance(
            link,
            CronenbergQuantumLink
        )
        self._assert_object_only(link)
        self.assertEqual(link.target_id, "target")
        self.assertEqual(
            link.link_type,
            "quantum_counterpart"
        )
        self.assertEqual(event["strength"], 0.75)

    def test_duplicate_strengthens_same_object(
        self
    ):
        links = CronenbergQuantumLinks(
            owner_id="source"
        )
        links.add_link(
            target_id="target",
            link_type="causal_paradox",
            strength=0.5,
        )
        link = links.links[0]

        event = links.add_link(
            target_id="target",
            link_type="causal_paradox",
            strength=0.9,
        )

        self.assertIs(links.links[0], link)
        self.assertEqual(link.strength, 0.9)
        self.assertEqual(event["strength"], 0.9)
        self.assertEqual(len(links.history), 1)

    def test_returned_link_snapshot_is_detached(
        self
    ):
        links = CronenbergQuantumLinks(
            owner_id="source"
        )
        event = links.add_link(
            target_id="target",
            link_type="manifested_consequence",
            metadata={
                "route": {
                    "layer": "quantum_layer"
                }
            },
        )

        event["strength"] = 99.0
        event["metadata"]["route"][
            "layer"
        ] = "changed"

        link = links.links[0]
        self.assertEqual(link.strength, 1.0)
        self.assertEqual(
            link.metadata["route"]["layer"],
            "quantum_layer"
        )

    def test_public_state_is_deeply_detached(
        self
    ):
        links = CronenbergQuantumLinks(
            owner_id="source"
        )
        links.add_link(
            target_id="target",
            link_type="causal_paradox",
            metadata={
                "route": {
                    "step": 3
                }
            },
        )

        public_state = links.public_state
        public_state["links"][0][
            "metadata"
        ]["route"]["step"] = 99
        public_state["history"][0][
            "link"
        ]["metadata"]["route"]["step"] = 88

        self.assertEqual(
            links.links[0]
            .metadata["route"]["step"],
            3
        )
        self.assertEqual(
            links.history[0]["link"]
            ["metadata"]["route"]["step"],
            3
        )

    def test_counterpart_creation_uses_link_objects(
        self
    ):
        universe = Universe()
        original = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("test"),
                "test",
                "quantum_link_object_state",
            )
        )
        counterpart = (
            universe
            .create_cronenberg_quantum_counterpart(
                original
            )["counterpart"]
        )

        original_link = (
            original.quantum_link_system
            .links[0]
        )
        counterpart_link = (
            counterpart.quantum_link_system
            .links[0]
        )

        self.assertIsInstance(
            original_link,
            CronenbergQuantumLink
        )
        self.assertIsInstance(
            counterpart_link,
            CronenbergQuantumLink
        )
        self.assertEqual(
            original_link.target_id,
            counterpart.id
        )
        self.assertEqual(
            counterpart_link.target_id,
            original.id
        )
        self.assertEqual(
            original.quantum_links[0][
                "target_id"
            ],
            counterpart.id
        )


if __name__ == "__main__":
    unittest.main()
