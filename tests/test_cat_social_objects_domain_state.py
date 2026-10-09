import unittest

from cats.cat_social_objects import (
    CatBond,
    CatGuestIncident,
    CatMeowInvitation,
    CatSocialMemory,
    CatTerritoryClaim,
    GarfieldTraining,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatSocialObjectsDomainStateTests(
    unittest.TestCase
):

    def test_simple_social_objects_use_pure_domain_base(
        self
    ):
        objects = (
            CatMeowInvitation(
                name="invitation",
            ),
            CatGuestIncident(
                name="incident",
            ),
            GarfieldTraining(
                name="training",
            ),
            CatTerritoryClaim(
                name="claim",
            ),
            CatSocialMemory(
                name="memory",
            ),
            CatBond(
                name="bond",
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

            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
            ):
                self.assertFalse(
                    hasattr(
                        value,
                        mapping_method,
                    )
                )

            with self.assertRaises(
                TypeError
            ):
                _ = value[
                    "name"
                ]

    def test_different_social_types_are_not_equal(
        self
    ):
        memory = CatSocialMemory(
            state="known",
        )

        bond = CatBond(
            state="known",
        )

        self.assertNotEqual(
            memory,
            bond,
        )


if __name__ == "__main__":
    unittest.main()
