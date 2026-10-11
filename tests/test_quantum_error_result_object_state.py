import unittest

from quantum.error_boundary import (
    QuantumErrorBoundary,
    QuantumErrorResult,
)


class FakeCronenberg:

    def __init__(self):
        self.id = "cronenberg_test"


class QuantumErrorResultObjectStateTests(
    unittest.TestCase
):

    def test_error_boundary_returns_object_result(
        self,
    ):
        cronenberg = FakeCronenberg()

        boundary = QuantumErrorBoundary(
            cronenberg_factory=(
                lambda **kwargs: cronenberg
            )
        )

        def broken_operation():
            raise RuntimeError("boom")

        result = boundary.execute(
            operation=broken_operation,
            source_component="test",
            source_operation="broken",
        )

        self.assertIsInstance(
            result,
            QuantumErrorResult,
        )
        self.assertEqual(
            result.type,
            "quantum_error",
        )
        self.assertEqual(
            result.error_type,
            "RuntimeError",
        )
        self.assertEqual(
            result.error_message,
            "boom",
        )
        self.assertIs(
            result.cronenberg,
            cronenberg,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = result["error_type"]

    def test_successful_operation_is_not_wrapped(
        self,
    ):
        boundary = QuantumErrorBoundary(
            cronenberg_factory=(
                lambda **kwargs: FakeCronenberg()
            )
        )

        result = boundary.execute(
            operation=lambda: "success",
            source_component="test",
            source_operation="success",
        )

        self.assertEqual(
            result,
            "success",
        )


if __name__ == "__main__":
    unittest.main()
