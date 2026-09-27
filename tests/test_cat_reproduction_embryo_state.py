import unittest
from typing import get_type_hints

from cats.cat_birth_objects import KittenEmbryo
from cats.cat_reproduction_state import CatReproductionState


class CatReproductionEmbryoStateTests(
    unittest.TestCase
):

    def test_embryo_state_has_domain_type(
        self
    ):
        hints = get_type_hints(
            CatReproductionState
        )

        self.assertEqual(
            hints["embryos"],
            list[KittenEmbryo],
        )


if __name__ == "__main__":
    unittest.main()
