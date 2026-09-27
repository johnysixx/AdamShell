import unittest

from cats.cat_distribution_status import (
    CatDistributionStatus,
)


class CatDistributionStatusObjectStateTests(
    unittest.TestCase
):

    def test_status_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                status.value
                for status
                in CatDistributionStatus
            },
            {
                "assigned",
                "unassigned",
            },
        )


if __name__ == "__main__":
    unittest.main()
