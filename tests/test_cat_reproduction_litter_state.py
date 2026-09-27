import unittest
from typing import get_type_hints

from cats.cat_birth_objects import CatLitter
from cats.cat_reproduction_state import CatReproductionState


class CatReproductionLitterStateTests(
    unittest.TestCase
):

    def test_litter_state_has_domain_types(
        self
    ):
        hints = get_type_hints(
            CatReproductionState
        )

        self.assertEqual(
            hints["litters"],
            list[CatLitter],
        )

        self.assertEqual(
            hints["last_litter"],
            CatLitter | None,
        )

    def test_litter_state_preserves_domain_objects(
        self
    ):
        state = CatReproductionState(
            sex="female"
        )

        litter = CatLitter(
            litter_number=1,
            mother="mother",
            father_names=(),
            embryos_present=0,
            kittens_born=0,
            kitten_names=(),
            birth_results=(),
            pregnancy_day=65,
            gestation_days=65,
            birth_day=65,
        )

        state.litters.append(
            litter
        )
        state.last_litter = litter

        self.assertIs(
            state.litters[0],
            litter,
        )

        self.assertIs(
            state.last_litter,
            litter,
        )

        boundary = state.to_dict()

        self.assertIsInstance(
            boundary["litters"][0],
            dict,
        )

        self.assertIsInstance(
            boundary["last_litter"],
            dict,
        )

        self.assertIs(
            state.litters[0],
            litter,
        )

        self.assertIs(
            state.last_litter,
            litter,
        )


if __name__ == "__main__":
    unittest.main()
