import unittest

from core.technology.dark_matter_technology import (
    DarkMatterTechnology,
)
from core.technology.technology import Technology
from core.technology.technology_state import (
    TechnologyState,
)


class TechnologyStateObjectStateTests(
    unittest.TestCase
):

    def test_technology_starts_discovered(self):
        technology = Technology(
            "test_technology"
        )

        self.assertIs(
            technology.state,
            TechnologyState.DISCOVERED,
        )

        self.assertTrue(
            technology.is_discovered
        )

    def test_advance_follows_enum_order(self):
        technology = Technology(
            "test_technology"
        )

        self.assertTrue(
            technology.advance()
        )

        self.assertIs(
            technology.state,
            TechnologyState.ANNOUNCED,
        )

        self.assertTrue(
            technology.advance()
        )

        self.assertIs(
            technology.state,
            TechnologyState.INFRASTRUCTURE,
        )

        self.assertTrue(
            technology.advance()
        )

        self.assertIs(
            technology.state,
            TechnologyState.ACTIVE,
        )

        self.assertFalse(
            technology.advance()
        )

    def test_set_state_requires_next_phase(self):
        technology = Technology(
            "test_technology"
        )

        with self.assertRaises(ValueError):
            technology.set_state(
                TechnologyState.ACTIVE
            )

        self.assertTrue(
            technology.set_state(
                TechnologyState.ANNOUNCED
            )
        )

        self.assertIs(
            technology.state,
            TechnologyState.ANNOUNCED,
        )

    def test_string_state_is_rejected(self):
        technology = Technology(
            "test_technology"
        )

        with self.assertRaises(TypeError):
            technology.state = "active"

        with self.assertRaises(TypeError):
            technology.set_state(
                "active"
            )

    def test_public_state_keeps_string_boundary(self):
        technology = Technology(
            "test_technology"
        )

        technology.advance()

        self.assertEqual(
            technology.public_state,
            {
                "name": "test_technology",
                "state": "announced",
            },
        )

    def test_dark_matter_technology_uses_enum_state(
        self
    ):
        technology = (
            DarkMatterTechnology()
        )

        self.assertIs(
            technology.state,
            TechnologyState.DISCOVERED,
        )

    def test_state_values_define_domain(self):
        self.assertEqual(
            {
                state.value
                for state in TechnologyState
            },
            {
                "discovered",
                "announced",
                "infrastructure",
                "active",
            },
        )


if __name__ == "__main__":
    unittest.main()
