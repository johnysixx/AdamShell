import unittest

from core.entity.cronenberg_system.origin import (
    CronenbergOrigin
)
from universe.universe import Universe


class CronenbergOriginObjectStateTests(
    unittest.TestCase
):

    def _create_cronenberg(self):
        universe = Universe()
        cronenberg = (
            universe
            .create_cronenberg_from_quantum_error(
                ValueError("origin test"),
                "origin_component",
                "origin_operation",
            )
        )

        return universe, cronenberg

    def _create_pair(self):
        universe, original = (
            self._create_cronenberg()
        )
        counterpart = (
            universe
            .create_cronenberg_quantum_counterpart(
                original
            )["counterpart"]
        )

        return universe, original, counterpart

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
            _ = value["layer"]

    def test_origin_has_no_mapping_api(self):
        _, cronenberg = (
            self._create_cronenberg()
        )

        self.assertIsInstance(
            cronenberg.origin,
            CronenbergOrigin
        )
        self._assert_object_only(
            cronenberg.origin
        )
        self.assertEqual(
            cronenberg.origin.layer,
            "quantum_layer"
        )
        self.assertEqual(
            cronenberg.origin.error_type,
            "ValueError"
        )

    def test_counterpart_marks_same_origin_object(
        self
    ):
        universe, original = (
            self._create_cronenberg()
        )
        counterpart = (
            universe
            .create_cronenberg_quantum_counterpart(
                original
            )["counterpart"]
        )
        origin = counterpart.origin

        self.assertIs(counterpart.origin, origin)
        self.assertEqual(
            origin.counterpart_of,
            original.id
        )
        self.assertEqual(
            origin.pair_id,
            original.quantum_state.pair_id
        )
        self.assertEqual(
            origin.spin_relation,
            "opposite"
        )
        self.assertEqual(
            origin.manifested_in,
            "quantum_layer"
        )

    def test_merge_records_origin_attributes(
        self
    ):
        universe, original, counterpart = (
            self._create_pair()
        )
        original.location = "shared_kernel"
        counterpart.location = "shared_kernel"
        pair_id = original.quantum_state.pair_id

        merged = (
            universe
            .merge_cronenberg_quantum_pair(
                original,
                counterpart,
            )["merged"]
        )

        self.assertEqual(
            merged.origin.merged_from,
            (original.id, counterpart.id)
        )
        self.assertEqual(
            merged.origin.former_pair_id,
            pair_id
        )
        self.assertEqual(
            merged.origin.merge_location,
            "shared_kernel"
        )

    def test_recombination_records_origin_attributes(
        self
    ):
        universe, original, counterpart = (
            self._create_pair()
        )
        original.location = "shared_kernel"
        counterpart.location = "shared_kernel"
        pair_id = original.quantum_state.pair_id

        result = (
            universe
            .resolve_quantum_pair_consumption(
                original,
                counterpart,
            )
        )
        recombined = result["recombined"]
        origin = recombined.origin

        self.assertEqual(
            origin.recombined_from,
            (original.id, counterpart.id)
        )
        self.assertEqual(
            origin.former_pair_id,
            pair_id
        )
        self.assertEqual(
            origin.consumption_location,
            "shared_kernel"
        )
        self.assertEqual(
            origin.released_energy,
            result["event"]["released_energy"]
        )
        self.assertEqual(
            origin.dark_energy_created,
            result["event"][
                "dark_energy_created"
            ]
        )

    def test_public_origin_snapshot_is_detached(
        self
    ):
        universe, original, counterpart = (
            self._create_pair()
        )
        original.location = "shared_kernel"
        counterpart.location = "shared_kernel"
        merged = (
            universe
            .merge_cronenberg_quantum_pair(
                original,
                counterpart,
            )["merged"]
        )

        snapshot = merged.public_state["origin"]
        snapshot["merged_from"].append(
            "changed"
        )
        snapshot["merge_location"] = "changed"

        self.assertEqual(
            merged.origin.merged_from,
            (original.id, counterpart.id)
        )
        self.assertEqual(
            merged.origin.merge_location,
            "shared_kernel"
        )


if __name__ == "__main__":
    unittest.main()
