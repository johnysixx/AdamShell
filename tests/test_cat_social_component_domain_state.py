import unittest

from cats.cat_components import (
    CatHumanBond,
    CatHumanBonds,
    CatMeowInvitations,
    CatNorms,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatSocialComponentDomainStateTests(
    unittest.TestCase
):

    def test_social_state_holders_use_pure_domain_base(
        self
    ):
        objects = (
            CatHumanBond(
                human="johny",
            ),
            CatHumanBonds(
                records={},
            ),
            CatMeowInvitations(
                offered=0,
                history=[],
            ),
            CatNorms(
                violations=[],
                sanctions=[],
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
                    "state"
                ]

    def test_different_social_state_types_are_not_equal(
        self
    ):
        bonds = CatHumanBonds(
            records={},
        )

        invitations = CatMeowInvitations(
            records={},
        )

        self.assertNotEqual(
            bonds,
            invitations,
        )


if __name__ == "__main__":
    unittest.main()
