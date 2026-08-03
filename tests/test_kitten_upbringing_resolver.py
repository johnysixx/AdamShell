import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver
)
from cats.kitten_upbringing_resolver import (
    KittenUpbringingResolver
)


class KittenUpbringingResolverTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats_layer = Cats(
            self.universe
        )

        self.development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        self.resolver = (
            KittenUpbringingResolver(
                self.universe
            )
        )

        self.mother = self.cats_layer.create_cat(
            name="mother",
            color="black",
            fur_length="short",
            origin="natural_birth"
        )

        self.father = self.cats_layer.create_cat(
            name="father",
            color="orange",
            fur_length="short",
            origin="natural_birth"
        )

        self.kitten = self.cats_layer.create_cat(
            name="kitten",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        self.kitten["parents"] = {
            "mother": "mother",
            "father": "father"
        }

        self.kitten["mother_name"] = "mother"

        self.development.initialize_newborn(
            self.kitten,
            birth_day=0
        )

    def run_at_age(
        self,
        age_days
    ):
        self.kitten["age_days"] = age_days

        return self.resolver.tick_day(
            kitten=self.kitten,
            cats=self.cats_layer.cats,
            current_day=age_days
        )

    def test_first_thirteen_days_are_care_only(self):
        result = self.run_at_age(10)

        self.assertTrue(
            result["processed"]
        )

        self.assertEqual(
            result["phase"],
            "complete_maternal_care"
        )

        event_names = {
            event["name"]
            for event in result["events"]
        }

        self.assertIn(
            "fed_by_mother",
            event_names
        )

        self.assertIn(
            "cleaned_by_mother",
            event_names
        )

        self.assertIn(
            "warmed_by_mother",
            event_names
        )

        self.assertFalse(
            self.kitten[
                "learning"
            ][
                "skills"
            ][
                "socialization"
            ][
                "learned"
            ]
        )

    def test_father_sometimes_brings_dead_cronenberg(self):
        result = self.run_at_age(10)

        event_names = {
            event["name"]
            for event in result["events"]
        }

        self.assertIn(
            "father_brought_dead_cronenberg",
            event_names
        )

        experience = self.kitten[
            "upbringing"
        ][
            "cronenberg_experience"
        ]

        self.assertEqual(
            experience[
                "father_food_deliveries"
            ],
            1
        )

    def test_day_fourteen_starts_socialization(self):
        result = self.run_at_age(14)

        self.assertEqual(
            result["phase"],
            "early_socialization"
        )

        event_names = {
            event["name"]
            for event in result["events"]
        }

        self.assertIn(
            "mother_left_kittens_alone_briefly",
            event_names
        )

        self.assertIn(
            "mother_brought_small_dead_cronenberg",
            event_names
        )

        socialization = self.kitten[
            "learning"
        ][
            "skills"
        ][
            "socialization"
        ]

        self.assertGreater(
            socialization["progress"],
            0.0
        )

    def test_day_eighteen_teaches_litter_box(self):
        self.run_at_age(18)

        skill = self.kitten[
            "learning"
        ][
            "skills"
        ][
            "litter_box"
        ]

        self.assertTrue(
            skill["learned"]
        )

        self.assertEqual(
            skill["teacher"],
            "mother"
        )

    def test_day_nineteen_teaches_boxes(self):
        self.run_at_age(19)

        skill = self.kitten[
            "learning"
        ][
            "skills"
        ][
            "box_travel"
        ]

        self.assertTrue(
            skill["learned"]
        )

    def test_day_twenty_teaches_cat_doors(self):
        self.run_at_age(20)

        skill = self.kitten[
            "learning"
        ][
            "skills"
        ][
            "cat_door_travel"
        ]

        self.assertTrue(
            skill["learned"]
        )

    def test_manifested_cat_skips_upbringing(self):
        manifested = (
            self.cats_layer.create_cat(
                name="manifested",
                color="gray",
                fur_length="short",
                origin="dice_manifestation"
            )
        )

        result = self.resolver.tick_day(
            kitten=manifested,
            cats=self.cats_layer.cats,
            current_day=1
        )

        self.assertFalse(
            result["processed"]
        )

        self.assertEqual(
            result["reason"],
            "maternal_teaching_not_required"
        )



    def test_day_twenty_one_introduces_live_prey(self):
        result = self.run_at_age(21)

        self.assertEqual(
            result["phase"],
            "live_prey_training"
        )

        event_names = {
            event["name"]
            for event in result["events"]
        }

        self.assertIn(
            "mother_brought_small_live_cronenberg",
            event_names
        )

        experience = self.kitten[
            "upbringing"
        ][
            "cronenberg_experience"
        ]

        self.assertEqual(
            experience["live_deliveries"],
            1
        )

    def test_early_live_prey_days_practice_chasing(self):
        result = self.run_at_age(24)

        hunting_events = [
            event
            for event in result["events"]
            if event["name"]
            == "kitten_hunting_step_practiced"
        ]

        self.assertEqual(
            len(hunting_events),
            1
        )

        self.assertEqual(
            hunting_events[0]["step"],
            "tracking_and_chasing"
        )

        hunting = self.kitten[
            "learning"
        ][
            "skills"
        ][
            "hunting"
        ]

        self.assertGreater(
            hunting["progress"],
            0.0
        )

        self.assertFalse(
            hunting["learned"]
        )

    def test_later_training_practices_killing_bite(self):
        result = self.run_at_age(30)

        hunting_event = next(
            event
            for event in result["events"]
            if event["name"]
            == "kitten_hunting_step_practiced"
        )

        self.assertEqual(
            hunting_event["step"],
            "capture_and_killing_bite"
        )

    def test_day_thirty_five_records_first_kill(self):
        result = self.run_at_age(35)

        self.assertEqual(
            result["phase"],
            "first_training_kill"
        )

        event_names = {
            event["name"]
            for event in result["events"]
        }

        self.assertIn(
            "kitten_completed_first_training_kill",
            event_names
        )

        experience = self.kitten[
            "upbringing"
        ][
            "cronenberg_experience"
        ]

        self.assertEqual(
            experience["successful_kills"],
            1
        )

        hunting = self.kitten[
            "learning"
        ][
            "skills"
        ][
            "hunting"
        ]

        self.assertGreaterEqual(
            hunting["progress"],
            0.85
        )

    def test_family_hunts_start_after_training_kill(self):
        self.run_at_age(35)

        result = self.run_at_age(36)

        self.assertEqual(
            result["phase"],
            "family_hunting"
        )

        event = next(
            event
            for event in result["events"]
            if event["name"]
            == "kitten_joined_family_cronenberg_hunt"
        )

        self.assertEqual(
            event["family_hunt_number"],
            1
        )

        self.assertFalse(
            event["father_joined"]
        )

    def test_father_joins_every_second_family_hunt(self):
        self.run_at_age(35)
        self.run_at_age(36)

        result = self.run_at_age(37)

        event = next(
            event
            for event in result["events"]
            if event["name"]
            == "kitten_joined_family_cronenberg_hunt"
        )

        self.assertEqual(
            event["family_hunt_number"],
            2
        )

        self.assertTrue(
            event["father_joined"]
        )

        self.assertEqual(
            self.kitten[
                "learning"
            ][
                "hunting_teacher_father"
            ],
            "father"
        )

    def test_hunting_finishes_after_family_experience(self):
        for age in range(21, 36):
            self.run_at_age(age)

        for age in range(36, 40):
            self.run_at_age(age)

        hunting = self.kitten[
            "learning"
        ][
            "skills"
        ][
            "hunting"
        ]

        experience = self.kitten[
            "upbringing"
        ][
            "cronenberg_experience"
        ]

        self.assertGreaterEqual(
            experience["successful_kills"],
            1
        )

        self.assertGreaterEqual(
            experience["family_hunts"],
            3
        )

        self.assertTrue(
            hunting["learned"]
        )

        self.assertEqual(
            hunting["progress"],
            1.0
        )


if __name__ == "__main__":
    unittest.main()