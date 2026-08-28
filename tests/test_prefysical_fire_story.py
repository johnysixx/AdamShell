import unittest

from universe.universe import Universe
from idea_entities import IdeaEntities


class FixedRng:

    def __init__(
        self,
        first_roll
    ):
        self.first_roll = (
            first_roll
        )

        self.roll_used = False

    def randint(
        self,
        start,
        end
    ):
        if not self.roll_used:
            self.roll_used = True

            return self.first_roll

        return start

    def random(
        self
    ):
        return 0.99

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

    def shuffle(
        self,
        sequence
    ):
        return None


class PrefysicalFireStoryTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()

        self.idea_entities = IdeaEntities(
            self.universe
        )

        # Existing masculine principle.
        self.universe.world[
            "pazuzu_masculine_principle"
        ] = {
            "name": "pazuzu",
            "type": "idea_entity",
            "energy_j": 100.0
        }

        self.fire_origin = (
            self.idea_entities
            .prefysical_fire_origin
        )

        self.fire_origin.begin()

    def test_serpent_finds_and_hands_over_sticks(
        self
    ):
        materials = (
            self.fire_origin
            .materials
        )

        self.assertEqual(
            materials[
                "found_by"
            ],
            "serpent"
        )

        self.assertEqual(
            materials[
                "handed_to"
            ],
            "pazuzu_masculine_principle"
        )

    def test_each_attempt_rolls_once_and_converts_energy(
        self
    ):
        masculine = (
            self.universe.world[
                "pazuzu_masculine_principle"
            ]
        )

        before_energy = (
            masculine[
                "energy_j"
            ]
        )

        before_rolls = (
            self.idea_entities
            .serpent_d20
            .roll_count
        )

        result = (
            self.fire_origin
            .attempt_ignition(
                rng=FixedRng(
                    10
                )
            )
        )

        after_energy = (
            masculine[
                "energy_j"
            ]
        )

        after_rolls = (
            self.idea_entities
            .serpent_d20
            .roll_count
        )

        self.assertEqual(
            after_rolls,
            before_rolls + 1
        )

        self.assertLess(
            after_energy,
            before_energy
        )

        converted = result[
            "energy_conversion"
        ][
            "converted_to_friction_heat_j"
        ]

        self.assertAlmostEqual(
            before_energy - after_energy,
            converted
        )

        self.assertAlmostEqual(
            converted,
            self.fire_origin
            .energy_conversion[
                "friction_heat_j"
            ]
        )

        self.assertEqual(
            result[
                "energy_conversion"
            ][
                "energy_destroyed_j"
            ],
            0.0
        )

    def test_success_creates_small_fire_with_accumulated_heat(
        self
    ):
        # First attempt fails but still creates heat.
        self.fire_origin.attempt_ignition(
            rng=FixedRng(
                10
            )
        )

        heat_before_success = (
            self.fire_origin
            .energy_conversion[
                "friction_heat_j"
            ]
        )

        result = (
            self.fire_origin
            .attempt_ignition(
                rng=FixedRng(
                    20
                )
            )
        )

        self.assertEqual(
            result[
                "result"
            ],
            "prefysical_fire_ignited"
        )

        fire = (
            self.idea_entities
            .eternal_fire
        )

        self.assertTrue(
            fire[
                "actualized"
            ]
        )

        self.assertEqual(
            fire[
                "flame_state"
            ],
            "small"
        )

        self.assertEqual(
            fire[
                "fuel"
            ][
                "wood_sticks"
            ],
            2.0
        )

        self.assertEqual(
            fire[
                "fuel"
            ][
                "wood_added_by"
            ],
            "pazuzu_masculine_principle"
        )

        self.assertGreater(
            fire[
                "heat_energy_j"
            ],
            heat_before_success
        )

    def test_fire_consumes_fuel_and_roles_split(
        self
    ):
        self.fire_origin.attempt_ignition(
            rng=FixedRng(
                20
            )
        )

        # Dry grass goes first.
        first = (
            self.fire_origin
            .advance_fire()
        )

        self.assertEqual(
            first[
                "details"
            ][
                "consumed"
            ][
                "dry_grass"
            ],
            1.0
        )

        # Then wood is eaten only gradually.
        before_wood = (
            self.idea_entities
            .eternal_fire[
                "fuel"
            ][
                "wood_sticks"
            ]
        )

        self.fire_origin.advance_fire()

        after_wood = (
            self.idea_entities
            .eternal_fire[
                "fuel"
            ][
                "wood_sticks"
            ]
        )

        self.assertLess(
            after_wood,
            before_wood
        )

        self.assertGreater(
            after_wood,
            0.0
        )

        understood = (
            self.fire_origin
            .understand_fire_significance()
        )

        self.assertEqual(
            understood[
                "details"
            ][
                "fire_guardian"
            ],
            "pazuzu_masculine_principle"
        )

        self.assertEqual(
            understood[
                "details"
            ][
                "fuel_seekers"
            ],
            [
                "lilith",
                "serpent"
            ]
        )

        self.assertTrue(
            self.idea_entities
            .eternal_fire[
                "meaning"
            ][
                "requires_fuel"
            ]
        )


if __name__ == "__main__":
    unittest.main()
