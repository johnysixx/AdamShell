import unittest

from meeting_place.bar_payment_kind import (
    BarPaymentKind,
)


class BarPaymentKindObjectStateTests(
    unittest.TestCase
):

    def test_payment_kind_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                payment_kind.value
                for payment_kind
                in BarPaymentKind
            },
            {
                "god_rule",
                "energy",
                "root_existence",
                "reality_exchange",
                "unsupported",
            },
        )


if __name__ == "__main__":
    unittest.main()
