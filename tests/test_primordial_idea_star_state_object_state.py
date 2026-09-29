import unittest

from idea_universe.primordial_idea_star import (
    PrimordialIdeaStar,
)
from idea_universe.primordial_idea_star_state import (
    PrimordialIdeaStarState,
)


class PrimordialIdeaStarStateObjectStateTests(
    unittest.TestCase
):

    def test_star_starts_created_as_enum(self):
        star = PrimordialIdeaStar()

        self.assertIs(
            star.state,
            PrimordialIdeaStarState.CREATED,
        )

    def test_ignite_sets_burning_enum_and_returns_boundary_string(
        self
    ):
        star = PrimordialIdeaStar()

        result = star.ignite()

        self.assertIs(
            star.state,
            PrimordialIdeaStarState.BURNING,
        )
        self.assertEqual(
            result,
            "burning",
        )

    def test_explode_sets_exploded_enum(self):
        star = PrimordialIdeaStar()
        star.ignite()

        remnant = star.explode()

        self.assertIs(
            star.state,
            PrimordialIdeaStarState.EXPLODED,
        )
        self.assertEqual(
            remnant["type"],
            "primordial_nebula_remnant",
        )

    def test_string_state_is_rejected(self):
        star = PrimordialIdeaStar()

        with self.assertRaises(TypeError):
            star.state = "burning"

    def test_state_values_define_domain_names(self):
        self.assertEqual(
            {
                state.value
                for state in PrimordialIdeaStarState
            },
            {
                "created",
                "burning",
                "exploded",
            },
        )


if __name__ == "__main__":
    unittest.main()
