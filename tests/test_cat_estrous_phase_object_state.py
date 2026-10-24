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

    def test_phase_remains_domain_state_without_mapping_boundary(
        self
    ):
        state = CatReproductionState(
            "female"
        )

        state.estrous_phase = (
            CatEstrousPhase.ESTRUS
        )

        self.assertIs(
            state.estrous_phase,
            CatEstrousPhase.ESTRUS,
        )

        self.assertEqual(
            state.estrous_phase.value,
            "estrus",
        )

        self.assertFalse(
            hasattr(
                state,
                "to_dict",
            )
        )


if __name__ == "__main__":
    unittest.main()
