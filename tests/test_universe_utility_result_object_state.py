import unittest
from universe.aroma_composition import AromaComposition

from universe.aroma_profile import AromaProfile, AromaSurfaceResidue
from universe.aroma_residue import AromaResidue
from universe.aroma_residue_result_state import AromaResidueTransferResult
from universe.relativistic_travel import calculate_relativistic_travel
from universe.relativistic_travel_result_state import RelativisticTravelResult


class Target:
    pass


class UniverseUtilityResultObjectStateTests(unittest.TestCase):

    def assert_object_only(self, value):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value["result"]

    def test_aroma_transfer_returns_object_result(self):
        source = AromaProfile(
            identity="cat:pazuzu",
            base_components=AromaComposition.from_pairs(("cat", 1.0)),
        )
        target = Target()

        result = AromaResidue.transfer(
            source_profile=source,
            target=target,
            source_identity="pazuzu",
            fraction=0.25,
        )

        self.assertIsInstance(
            result,
            AromaResidueTransferResult,
        )
        self.assertTrue(result.transferred)
        self.assertEqual(
            result.components.amount("cat"),
            0.25,
        )
        self.assertIsInstance(
            result.residue,
            AromaSurfaceResidue,
        )
        self.assertIsNone(result.reason)
        self.assert_object_only(result)

    def test_aroma_transfer_failure_returns_object_result(self):
        result = AromaResidue.transfer_existing(
            source=Target(),
            target=Target(),
            source_identity="empty",
        )

        self.assertIsInstance(
            result,
            AromaResidueTransferResult,
        )
        self.assertFalse(result.transferred)
        self.assertEqual(
            result.reason,
            "source_has_no_aroma",
        )
        self.assertEqual(
            result.components.to_dict(),
            {},
        )
        self.assertIsNone(result.residue)
        self.assert_object_only(result)

    def test_aroma_result_snapshot_is_detached(self):
        source = AromaProfile(
            identity="cat:pazuzu",
            base_components=AromaComposition.from_pairs(("cat", 1.0)),
        )
        result = AromaResidue.transfer(
            source_profile=source,
            target=Target(),
            source_identity="pazuzu",
        )

        snapshot = result.to_dict()
        snapshot["components"]["cat"] = 99.0
        snapshot["residue"]["components"]["cat"] = 99.0

        self.assertNotEqual(
            result.components.amount("cat"),
            99.0,
        )
        self.assertNotEqual(
            result.residue.components.amount("cat"),
            99.0,
        )

    def test_relativistic_travel_returns_object_result(self):
        result = calculate_relativistic_travel(
            distance_m=1_000.0,
        )

        self.assertIsInstance(
            result,
            RelativisticTravelResult,
        )
        self.assertEqual(
            result.distance_m,
            1_000.0,
        )
        self.assertGreater(
            result.lorentz_factor,
            1.0,
        )
        self.assertGreater(
            result.coordinate_time_s,
            result.proper_time_s,
        )
        self.assert_object_only(result)

    def test_relativistic_snapshot_is_detached_boundary(self):
        result = calculate_relativistic_travel(
            distance_m=10.0,
        )

        snapshot = result.to_dict()
        snapshot["distance_m"] = 99.0

        self.assertEqual(
            result.distance_m,
            10.0,
        )


if __name__ == "__main__":
    unittest.main()
