import unittest

from universe.universe import Universe
from cats import Cats
from cats.cat import Cat
from cats.mating_resolver import (
    CatMatingResolver
)
from cats.reproduction import (
    CatReproduction
)


class MultiSireRng:

    def __init__(self):
        self.next_father = 0

    def randint(self, minimum, maximum):
        return minimum

    def choice(self, values):
        values = list(values)

        if (
            values
            and isinstance(
                values[0],
                Cat
            )
            and values[0].type == "cat"
        ):
            value = values[
                self.next_father
                % len(values)
            ]

            self.next_father += 1
            return value

        return values[0]


class CatMatingResolverTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.start_big_bang()
        self.cats = Cats(
            self.universe
        )

        self.female = self.cats.create_cat(
            name="mother",
            color="black",
            fur_length="short",
            sex="female"
        )

        self.first_male = self.cats.create_cat(
            name="father_one",
            color="orange",
            fur_length="long",
            sex="male"
        )

        self.second_male = self.cats.create_cat(
            name="father_two",
            color="black",
            fur_length="short",
            sex="male"
        )

        self.female[
            "reproduction"
        ]["ovulation_threshold"] = 1

        self.resolver = (
            CatMatingResolver(
                self.universe
            )
        )
        self.female[
            "reproduction"
        ]["estrus_active"] = True

        self.female[
        "reproduction"
        ]["estrous_phase"] = "estrus"

    def test_first_contact_opens_window_without_pregnancy(self):
        event = self.resolver.mate(
            self.female,
            self.first_male,
            current_day=10
        )

        reproduction = self.female[
            "reproduction"
        ]

        self.assertTrue(
            reproduction[
                "mating_window_open"
            ]
        )

        self.assertTrue(
            reproduction[
                "estrus_active"
            ]
        )

        self.assertFalse(
            reproduction["pregnant"]
        )

        self.assertFalse(
            event["pregnancy_started"]
        )

    def test_window_accepts_multiple_males(self):
        self.resolver.mate(
            self.female,
            self.first_male
        )

        self.resolver.mate(
            self.female,
            self.second_male
        )

        reproduction = self.female[
            "reproduction"
        ]

        self.assertEqual(
            reproduction[
                "potential_fathers"
            ],
            [
                "father_one",
                "father_two"
            ]
        )

        self.assertEqual(
            len(
                reproduction[
                    "mating_contacts"
                ]
            ),
            2
        )

    def test_repeated_contact_weights_same_male(self):
        self.resolver.mate(
            self.female,
            self.first_male
        )

        self.resolver.mate(
            self.female,
            self.first_male
        )

        self.resolver.mate(
            self.female,
            self.second_male
        )

        contacts = self.female[
            "reproduction"
        ]["mating_contacts"]

        selected = (
            self.resolver
            .paternity_resolver
            .select_father(
                contacts,
                rng=MultiSireRng()
            )
        )

        self.assertEqual(
            selected["event"][
                "weighted_candidate_names"
            ],
            [
                "father_one",
                "father_one",
                "father_two"
            ]
        )

    def test_closing_window_starts_pregnancy(self):
        self.resolver.mate(
            self.female,
            self.first_male,
            current_day=10
        )

        event = (
            self.resolver
            .close_mating_window(
                self.female,
                current_day=12,
                embryo_count=3,
                rng=MultiSireRng()
            )
        )

        reproduction = self.female[
            "reproduction"
        ]

        self.assertTrue(
            event["started"]
        )

        self.assertTrue(
            reproduction["pregnant"]
        )

        self.assertFalse(
            reproduction[
                "mating_window_open"
            ]
        )

        self.assertEqual(
            reproduction[
                "expected_birth_day"
            ],
            77
        )

        self.assertEqual(
            len(
                reproduction["embryos"]
            ),
            3
        )

    def test_one_litter_can_have_multiple_fathers(self):
        self.resolver.mate(
            self.female,
            self.first_male
        )

        self.resolver.mate(
            self.female,
            self.second_male
        )

        event = (
            self.resolver
            .close_mating_window(
                self.female,
                embryo_count=4,
                rng=MultiSireRng()
            )
        )

        fathers = [
            result["father"]
            for result in event[
                "paternity_results"
            ]
        ]

        self.assertEqual(
            fathers,
            [
                "father_one",
                "father_two",
                "father_one",
                "father_two"
            ]
        )

        self.assertTrue(
            event["multiple_sires"]
        )

        self.assertEqual(
            set(event["father_names"]),
            {
                "father_one",
                "father_two"
            }
        )

        embryos = self.female[
            "reproduction"
        ]["embryos"]

        self.assertEqual(
            {
                embryo["father_name"]
                for embryo in embryos
            },
            {
                "father_one",
                "father_two"
            }
        )

    def test_pregnancy_advances_to_birth_day(self):
        self.resolver.mate(
            self.female,
            self.first_male
        )

        self.resolver.close_mating_window(
            self.female,
            embryo_count=2,
            rng=MultiSireRng()
        )

        before = (
            self.resolver
            .advance_pregnancy(
                self.female,
                days=64
            )
        )

        self.assertFalse(
            before["ready_for_birth"]
        )

        final = (
            self.resolver
            .advance_pregnancy(
                self.female,
                days=1
            )
        )

        self.assertTrue(
            final["ready_for_birth"]
        )

    def test_neutered_female_cannot_open_window(self):
        self.female[
            "reproduction"
        ] = (
            CatReproduction.create_state(
                sex="female",
                neutered=True
            )
        )

        with self.assertRaises(
            ValueError
        ):
            self.resolver.mate(
                self.female,
                self.first_male
            )

    def test_neutered_male_cannot_be_candidate(self):
        self.first_male[
            "reproduction"
        ] = (
            CatReproduction.create_state(
                sex="male",
                neutered=True
            )
        )

        with self.assertRaises(
            ValueError
        ):
            self.resolver.mate(
                self.female,
                self.first_male
            )

    def test_window_without_contacts_cannot_close(self):
        reproduction = self.female[
            "reproduction"
        ]

        reproduction[
            "mating_window_open"
        ] = True

        with self.assertRaises(
            ValueError
        ):
            self.resolver.close_mating_window(
                self.female,
                embryo_count=2,
                rng=MultiSireRng()
            )


if __name__ == "__main__":
    unittest.main()