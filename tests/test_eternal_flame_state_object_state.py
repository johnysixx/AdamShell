import unittest

from core.eternal_flame.eternal_flame import EternalFlame
from core.eternal_flame.eternal_flame_state import (
    EternalFlameState,
)
from idea_entities.eternal_fire_potential import (
    EternalFirePotential,
)


class EternalFlameStateObjectStateTests(
    unittest.TestCase
):

    def _burning_idea(self):
        fire = EternalFirePotential()
        fire.type = "idea_focal_point"
        fire.state = "burning"
        fire.actualized = True
        return fire

    def test_flame_starts_unignited_as_enum(self):
        flame = EternalFlame()

        self.assertIs(
            flame.state,
            EternalFlameState.UNIGNITED,
        )
        self.assertEqual(
            flame.public_state["state"],
            "unignited",
        )

    def test_ignite_sets_burning_enum(self):
        flame = EternalFlame()

        flame.ignite(
            self._burning_idea(),
            tick=1,
            keeper="pazuzu",
        )

        self.assertIs(
            flame.state,
            EternalFlameState.BURNING,
        )
        self.assertEqual(
            flame.public_state["state"],
            "burning",
        )

    def test_repeated_ignition_keeps_history_boundary_string(
        self
    ):
        flame = EternalFlame()
        idea = self._burning_idea()

        flame.ignite(
            idea,
            tick=1,
        )

        result = flame.ignite(
            idea,
            tick=2,
        )

        self.assertIs(
            flame.state,
            EternalFlameState.BURNING,
        )
        self.assertEqual(
            flame.history[1].state,
            "burning",
        )
        self.assertEqual(
            result["state"],
            "burning",
        )

    def test_string_state_is_rejected(self):
        flame = EternalFlame()

        with self.assertRaises(TypeError):
            flame.state = "burning"

    def test_state_values_define_domain_names(self):
        self.assertEqual(
            {
                state.value
                for state in EternalFlameState
            },
            {
                "unignited",
                "burning",
            },
        )


if __name__ == "__main__":
    unittest.main()
