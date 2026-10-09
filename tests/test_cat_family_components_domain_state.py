import unittest

from cats.cat_components import (
    FamilyBonding,
    ParentalTeaching,
    SiblingPlay,
    SiblingRivalry,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatFamilyComponentsDomainStateTests(
    unittest.TestCase
):

    def test_family_interaction_state_uses_pure_domain_base(
        self
    ):
        objects = (
            SiblingPlay(
                play_events=0,
                partners={},
            ),
            SiblingRivalry(
                events=0,
                rivals={},
            ),
            ParentalTeaching(
                lessons_received=0,
                teachers={},
            ),
            FamilyBonding(
                events=0,
                family_bonds=[],
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

    def test_family_interaction_types_remain_distinct(
        self
    ):
        play = SiblingPlay(
            state="active",
        )

        rivalry = SiblingRivalry(
            state="active",
        )

        teaching = ParentalTeaching(
            state="active",
        )

        bonding = FamilyBonding(
            state="active",
        )

        self.assertNotEqual(
            play,
            rivalry,
        )

        self.assertNotEqual(
            rivalry,
            teaching,
        )

        self.assertNotEqual(
            teaching,
            bonding,
        )


if __name__ == "__main__":
    unittest.main()
