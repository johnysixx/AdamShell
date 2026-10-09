import unittest

from cats.cat_components import (
    CatEmergencyNursing,
    CatFamily,
    MaternalCare,
    MaternalCareReceived,
)
from cats.cat_social_objects import (
    CatLegend,
)
from core.entity.domain_object import (
    DomainObject,
)


class RemainingCatComponentDomainStateTests(
    unittest.TestCase
):

    def test_remaining_simple_cat_state_uses_domain_object(
        self
    ):
        objects = (
            CatFamily(
                children=[],
                siblings=[],
            ),
            MaternalCare(
                active=False,
                care_events=0,
            ),
            MaternalCareReceived(
                mother=None,
                care_events=0,
                last_phase=None,
            ),
            CatEmergencyNursing.create_state(
                name="domain_cat",
                sex="male",
            ),
            CatLegend(
                legend_id="legend_1",
                active=True,
            ),
        )

        for value in objects:
            self.assertIsInstance(
                value,
                DomainObject,
            )

            self.assertFalse(
                hasattr(
                    value,
                    "to_dict",
                )
            )

            for method_name in (
                "get",
                "keys",
                "items",
                "values",
            ):
                self.assertFalse(
                    hasattr(
                        value,
                        method_name,
                    )
                )

            with self.assertRaises(
                TypeError
            ):
                _ = value[
                    "state"
                ]

    def test_remaining_domain_types_are_distinct(
        self
    ):
        family = CatFamily(
            state="active",
        )

        care = MaternalCare(
            state="active",
        )

        legend = CatLegend(
            state="active",
        )

        self.assertNotEqual(
            family,
            care,
        )

        self.assertNotEqual(
            care,
            legend,
        )

    def test_maternal_care_received_keeps_phase_validation(
        self
    ):
        state = MaternalCareReceived(
            last_phase=None,
        )

        with self.assertRaises(
            TypeError
        ):
            state.last_phase = "legacy_phase"


if __name__ == "__main__":
    unittest.main()
