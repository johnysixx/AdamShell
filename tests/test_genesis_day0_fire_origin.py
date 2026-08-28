import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from idea_entities import IdeaEntities
from genesis.day0 import GenesisDay0


class FixedRng:

    def __init__(
        self,
        values,
        random_values=None
    ):
        self.values = iter(
            values
        )

        self.random_values = iter(
            random_values
            or [0.99] * 20
        )

    def randint(
        self,
        start,
        end
    ):
        return next(
            self.values
        )

    def random(
        self
    ):
        return next(
            self.random_values
        )

    def choice(
        self,
        sequence
    ):
        return sequence[0]

    def sample(
        self,
        population,
        k
    ):
        return list(
            population
        )[:k]


class GenesisDay0FireOriginTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.idea_entities = IdeaEntities(
            self.universe
        )

        # These principles already exist
        # before this particular Day 0 event.
        for name in (
            "serpent",
            "lilith",
            "pazuzu_masculine_principle"
        ):
            self.universe.world[
                name
            ] = {
                "name": name,
                "type": "idea_entity"
            }

        self.day0 = GenesisDay0(
            self.universe,
            self.idea_entities
        )

    def test_eternal_fire_is_only_potential_before_origin(
        self
    ):
        fire = (
            self.idea_entities
            .eternal_fire
        )

        self.assertFalse(
            fire["actualized"]
        )

        self.assertEqual(
            fire["state"],
            "unignited"
        )

        self.assertEqual(
            fire["type"],
            "idea_fire_potential"
        )

    def test_fire_origin_has_no_physical_time_or_space(
        self
    ):
        event = (
            self.day0
            .begin_fire_origin()
        )

        self.assertIsNone(
            event[
                "universe_tick"
            ]
        )

        self.assertIsNone(
            event[
                "location"
            ]
        )

        self.assertEqual(
            event[
                "ordering_kind"
            ],
            "logical_precedence"
        )

    def test_failed_attempt_does_not_create_eternal_fire(
        self
    ):
        result = (
            self.day0
            .attempt_fire(
                rng=FixedRng(
                    [10, 1]
                )
            )
        )

        self.assertEqual(
            result["result"],
            "fire_not_ignited"
        )

        self.assertFalse(
            self.day0
            .eternal_fire_exists
        )

    def test_successful_attempt_creates_eternal_fire(
        self
    ):
        result = (
            self.day0
            .attempt_fire(
                rng=FixedRng(
                    [20, 1]
                )
            )
        )

        self.assertEqual(
            result["result"],
            "prefysical_fire_ignited"
        )

        self.assertTrue(
            self.day0
            .eternal_fire_exists
        )

        fire = (
            self.idea_entities
            .eternal_fire
        )

        self.assertTrue(
            fire["actualized"]
        )

        self.assertEqual(
            fire["state"],
            "burning"
        )

        self.assertEqual(
            fire["type"],
            "idea_focal_point"
        )

        self.assertIsNone(
            fire[
                "ignited_at_idea_tick"
            ]
        )


if __name__ == "__main__":
    unittest.main()
