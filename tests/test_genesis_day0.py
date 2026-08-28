import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from idea_entities import IdeaEntities
from genesis.day0 import GenesisDay0


class GenesisDay0Tests(
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

        # These principles already exist before
        # the fire-origin interaction.
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

    def test_day0_has_no_physical_time_or_space(
        self
    ):
        state = self.day0.public_state

        self.assertFalse(
            state[
                "physical_time_exists"
            ]
        )

        self.assertFalse(
            state[
                "physical_space_exists"
            ]
        )

    def test_day0_requires_existing_principles(
        self
    ):
        result = (
            self.day0
            .verify_principles()
        )

        self.assertEqual(
            result[
                "ordering_kind"
            ],
            "logical_precedence"
        )

        self.assertIsNone(
            result[
                "physical_time"
            ]
        )

        self.assertIsNone(
            result[
                "physical_space"
            ]
        )

    def test_eternal_fire_does_not_exist_initially(
        self
    ):
        self.assertFalse(
            self.day0
            .eternal_fire_exists
        )

        fire = (
            self.idea_entities
            .eternal_fire
        )

        self.assertFalse(
            fire[
                "actualized"
            ]
        )

        self.assertEqual(
            fire[
                "state"
            ],
            "unignited"
        )

    def test_fire_origin_is_prephysical(
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

    def test_eden_is_not_created_by_day0(
        self
    ):
        names = {
            value.get(
                "name"
            )
            for value
            in self.universe.world.values()
            if isinstance(
                value,
                dict
            )
        }

        self.assertNotIn(
            "eden",
            names
        )

        self.assertNotIn(
            "idea_eden",
            names
        )


if __name__ == "__main__":
    unittest.main()
