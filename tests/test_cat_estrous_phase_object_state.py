import unittest
from typing import get_type_hints

from cats.cat_estrous_phase import CatEstrousPhase
from cats.cat_reproduction_state import CatReproductionState


class CatEstrousPhaseObjectStateTests(
    unittest.TestCase
):

    def test_reproduction_state_has_phase_domain_type(
        self
    ):
        hints = get_type_hints(
            CatReproductionState
        )

        self.assertIs(
            hints["estrous_phase"],
            CatEstrousPhase,
        )

    def test_initial_phase_is_domain_object(
        self
    ):
        state = CatReproductionState(
            "female"
        )

        self.assertIs(
            state.estrous_phase,
            CatEstrousPhase.INACTIVE,
        )

    def test_phase_values_are_explicit_domain_states(
        self
    ):
        self.assertEqual(
            CatEstrousPhase.INACTIVE.value,
            "inactive",
        )
        self.assertEqual(
            CatEstrousPhase.ESTRUS.value,
            "estrus",
        )
        self.assertEqual(
            CatEstrousPhase.INTERESTRUS.value,
            "interestrus",
        )
        self.assertEqual(
            CatEstrousPhase.DIESTRUS.value,
            "diestrus",
        )

    def test_to_dict_serializes_phase_at_boundary(
        self
    ):
        state = CatReproductionState(
            "female"
        )
        state.estrous_phase = (
            CatEstrousPhase.ESTRUS
        )

        boundary = state.to_dict()

        self.assertEqual(
            boundary["estrous_phase"],
            "estrus",
        )

        self.assertIs(
            state.estrous_phase,
            CatEstrousPhase.ESTRUS,
        )


if __name__ == "__main__":
    unittest.main()
