import unittest

from idea_entities import IdeaEntities
from idea_entities.prefysical_fire_origin_state import (
    PrefysicalFireOriginState,
)
from universe.universe import Universe


class FixedRng:

    def randint(self, start, end):
        return 20

    def random(self):
        return 0.99

    def choice(self, sequence):
        return sequence[0]

    def sample(self, population, k):
        return list(population)[:k]

    def shuffle(self, sequence):
        return None


class PrefysicalFireOriginStateObjectStateTests(
    unittest.TestCase
):

    def _origin(self):
        universe = Universe()
        idea_entities = IdeaEntities(
            universe
        )

        universe.world[
            "pazuzu_masculine_principle"
        ] = {
            "name": "pazuzu",
            "type": "idea_entity",
            "energy_j": 100.0,
        }

        return (
            idea_entities
            .prefysical_fire_origin
        )

    def test_origin_starts_prepared_as_enum(self):
        origin = self._origin()

        self.assertIs(
            origin.state,
            PrefysicalFireOriginState.PREPARED,
        )
        self.assertEqual(
            origin.public_state["state"],
            "prepared",
        )

    def test_begin_enters_seeking_warmth(self):
        origin = self._origin()

        origin.begin()

        self.assertIs(
            origin.state,
            PrefysicalFireOriginState.SEEKING_WARMTH,
        )
        self.assertEqual(
            origin.public_state["state"],
            "seeking_warmth",
        )

    def test_ignition_enters_fire_burning(self):
        origin = self._origin()
        origin.begin()

        origin.attempt_ignition(
            rng=FixedRng()
        )

        self.assertIs(
            origin.state,
            PrefysicalFireOriginState.FIRE_BURNING,
        )
        self.assertEqual(
            origin.public_state["state"],
            "fire_burning",
        )

    def test_significance_enters_guarded_fuel_search(
        self
    ):
        origin = self._origin()
        origin.begin()
        origin.attempt_ignition(
            rng=FixedRng()
        )

        origin.understand_fire_significance()

        self.assertIs(
            origin.state,
            (
                PrefysicalFireOriginState
                .FIRE_GUARDED_FUEL_SEARCH_ACTIVE
            ),
        )
        self.assertEqual(
            origin.public_state["state"],
            "fire_guarded_fuel_search_active",
        )

    def test_string_state_is_rejected(self):
        origin = self._origin()

        with self.assertRaises(TypeError):
            origin.state = "prepared"

    def test_state_values_define_domain_names(self):
        self.assertEqual(
            {
                state.value
                for state
                in PrefysicalFireOriginState
            },
            {
                "prepared",
                "seeking_warmth",
                "fire_burning",
                "fire_guarded_fuel_search_active",
            },
        )


if __name__ == "__main__":
    unittest.main()
