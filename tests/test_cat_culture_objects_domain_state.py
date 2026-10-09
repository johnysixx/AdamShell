import unittest

from cats.cat_culture_objects import (
    CatGroupInnovation,
    CatGroupInstitution,
    CatGroupMyth,
    CatGroupNorm,
    CatGroupRitual,
    CatGroupTaboo,
    CatInstitutionConflict,
    CatNormViolation,
    CatTabooViolation,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatCultureObjectsDomainStateTests(
    unittest.TestCase
):

    def test_cultural_domain_objects_use_pure_domain_base(
        self
    ):
        objects = (
            CatGroupMyth(
                name="myth",
            ),
            CatGroupNorm(
                name="norm",
            ),
            CatGroupTaboo(
                name="taboo",
            ),
            CatGroupRitual(
                name="ritual",
            ),
            CatGroupInstitution(
                name="institution",
            ),
            CatGroupInnovation(
                name="innovation",
            ),
            CatInstitutionConflict(
                name="conflict",
            ),
            CatNormViolation(
                severity=0.5,
            ),
            CatTabooViolation(
                severity=0.8,
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

    def test_violation_types_remain_distinct_domain_objects(
        self
    ):
        norm = CatNormViolation(
            severity=0.5,
        )

        taboo = CatTabooViolation(
            severity=0.5,
        )

        self.assertNotEqual(
            norm,
            taboo,
        )


if __name__ == "__main__":
    unittest.main()
