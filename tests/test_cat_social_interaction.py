import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat import Cat
from cats.cat_social_system import (
    CatSocialSystem
)
from cats.development_resolver import (
    CatDevelopmentResolver
)


class CatSocialInteractionTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

    def test_created_cat_is_real_cat_object(
        self
    ):
        cat = self.cats.create_cat(
            name="social_cat",
            color="orange",
            fur_length="short"
        )

        self.assertIsInstance(
            cat,
            Cat
        )

        self.assertEqual(
            cat.name,
            "social_cat"
        )

    def test_cat_can_accept_pet(
        self
    ):
        cat = self.cats.create_cat(
            name="pet_cat",
            color="orange",
            fur_length="short"
        )

        human = {
            "name": "human_1",
            "type": "human"
        }

        result = cat.accept_pet(
            human
        )

        self.assertTrue(
            result["accepted"]
        )

        self.assertEqual(
            result["cat"],
            "pet_cat"
        )

        self.assertEqual(
            result["by"],
            "human_1"
        )

        self.assertEqual(
            cat.pet_count,
            1
        )

        self.assertIn(
            result,
            cat.social_interactions
        )

    def test_manifested_cat_can_meow_to_entity(
        self
    ):
        cat = self.cats.create_cat(
            name="talking_cat",
            color="black",
            fur_length="short",
            origin="dice_manifestation"
        )

        listener = {
            "name": "listener_1",
            "type": "idea_entity"
        }

        result = cat.meow_to(
            listener
        )

        self.assertTrue(
            result["spoken"]
        )

        self.assertEqual(
            result["listener"],
            "listener_1"
        )

        self.assertIn(
            "bar_knowledge",
            result["contains"]
        )

        self.assertEqual(
            cat.meow_count,
            1
        )

    def test_cat_can_meow_specific_known_topic(
        self
    ):
        cat = self.cats.create_cat(
            name="bar_cat",
            color="orange",
            fur_length="short"
        )

        listener = {
            "name": "listener_2"
        }

        result = cat.meow_to(
            listener,
            topic="bar_knowledge"
        )

        self.assertTrue(
            result["spoken"]
        )

        self.assertEqual(
            result["contains"],
            [
                "bar_knowledge"
            ]
        )

    def test_cat_refuses_unknown_meow_topic(
        self
    ):
        cat = self.cats.create_cat(
            name="honest_cat",
            color="white",
            fur_length="short"
        )

        result = cat.meow_to(
            {
                "name": "listener_3"
            },
            topic="knowledge_of_everything"
        )

        self.assertFalse(
            result["spoken"]
        )

        self.assertEqual(
            result["reason"],
            "unknown_meow_topic"
        )

    def test_newborn_cannot_use_adult_meow_before_learning(
        self
    ):
        kitten = self.cats.create_cat(
            name="kitten",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        kitten["mother_name"] = "mother"

        development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        development.initialize_newborn(
            kitten,
            birth_day=0
        )

        result = kitten.meow_to(
            {
                "name": "listener_4"
            }
        )

        self.assertFalse(
            result["spoken"]
        )

        self.assertEqual(
            result["reason"],
            "meow_not_learned"
        )


    def _social_pair(
        self
    ):
        first = self.cats.create_cat(
            name="first_cat",
            color="black",
            fur_length="short"
        )

        second = self.cats.create_cat(
            name="second_cat",
            color="white",
            fur_length="short"
        )

        position = {
            "x": 1.0,
            "y": 2.0,
            "z": 0.0
        }

        first.position = dict(
            position
        )

        second.position = dict(
            position
        )

        first.current_layer = (
            "quantum_layer"
        )

        second.current_layer = (
            "quantum_layer"
        )

        return (
            first,
            second
        )

    def test_unknown_cats_sniff_and_keep_distance(
        self
    ):
        first, second = (
            self._social_pair()
        )

        social = CatSocialSystem(
            self.cats
        )

        result = social.meet(
            first,
            second
        )

        self.assertTrue(
            result["socialized"]
        )

        self.assertEqual(
            result["attitude"],
            "uncertain"
        )

        names = [
            step["name"]
            for step
            in result["steps"]
        ]

        self.assertIn(
            "cat_sniffed_cat",
            names
        )

        self.assertIn(
            "cat_kept_social_distance",
            names
        )

        self.assertIn(
            second.name,
            first.relationships
        )

        self.assertIn(
            first.name,
            second.relationships
        )

    def test_friendly_cats_use_affiliative_greeting(
        self
    ):
        first, second = (
            self._social_pair()
        )

        first.relationships[
            second.name
        ] = {
            "familiarity": 0.8,
            "trust": 0.9,
            "affiliation": 0.8,
            "tension": 0.0
        }

        second.relationships[
            first.name
        ] = {
            "familiarity": 0.8,
            "trust": 0.9,
            "affiliation": 0.8,
            "tension": 0.0
        }

        social = CatSocialSystem(
            self.cats
        )

        result = social.meet(
            first,
            second
        )

        self.assertEqual(
            result["attitude"],
            "friendly"
        )

        names = [
            step["name"]
            for step
            in result["steps"]
        ]

        self.assertIn(
            "cat_nose_touch",
            names
        )

        self.assertIn(
            "cat_slow_blink",
            names
        )

        self.assertIn(
            "cat_head_bunt",
            names
        )

        self.assertIn(
            "cat_body_rub",
            names
        )

        self.assertGreater(
            first.relationships[
                second.name
            ]["shared_scent"],
            0.0
        )

    def test_hostile_cats_hiss_before_physical_escalation(
        self
    ):
        first, second = (
            self._social_pair()
        )

        first.relationships[
            second.name
        ] = {
            "familiarity": 0.5,
            "trust": 0.1,
            "affiliation": 0.0,
            "tension": 0.8
        }

        second.relationships[
            first.name
        ] = {
            "familiarity": 0.5,
            "trust": 0.1,
            "affiliation": 0.0,
            "tension": 0.8
        }

        social = CatSocialSystem(
            self.cats
        )

        result = social.meet(
            first,
            second
        )

        self.assertEqual(
            result["attitude"],
            "hostile"
        )

        names = [
            step["name"]
            for step
            in result["steps"]
        ]

        self.assertIn(
            "cat_hissed_at_cat",
            names
        )

        self.assertIn(
            "cat_warning_swat",
            names
        )

        self.assertNotIn(
            "cat_fight_started",
            names
        )

        self.assertGreater(
            first.relationships[
                second.name
            ]["tension"],
            0.8
        )

    def test_extreme_hostility_can_escalate_to_fight(
        self
    ):
        first, second = (
            self._social_pair()
        )

        first.relationships[
            second.name
        ] = {
            "familiarity": 1.0,
            "trust": 0.0,
            "affiliation": 0.0,
            "tension": 1.0
        }

        second.relationships[
            first.name
        ] = {
            "familiarity": 1.0,
            "trust": 0.0,
            "affiliation": 0.0,
            "tension": 1.0
        }

        first.personality.setdefault(
            "traits",
            {}
        )[
            "aggression"
        ] = 1.0

        second.personality.setdefault(
            "traits",
            {}
        )[
            "aggression"
        ] = 1.0

        social = CatSocialSystem(
            self.cats
        )

        result = social.meet(
            first,
            second
        )

        names = [
            step["name"]
            for step
            in result["steps"]
        ]

        self.assertEqual(
            result["attitude"],
            "hostile"
        )

        self.assertIn(
            "cat_hissed_at_cat",
            names
        )

        self.assertIn(
            "cat_warning_swat",
            names
        )

        self.assertIn(
            "cat_fight_started",
            names
        )

    def test_social_meeting_is_recorded_by_both_cats(
        self
    ):
        first, second = (
            self._social_pair()
        )

        social = CatSocialSystem(
            self.cats
        )

        social.meet(
            first,
            second
        )

        first_names = [
            event.get(
                "name"
            )
            for event
            in first.social_interactions
        ]

        second_names = [
            event.get(
                "name"
            )
            for event
            in second.social_interactions
        ]

        self.assertIn(
            "cat_social_meeting",
            first_names
        )

        self.assertIn(
            "cat_social_meeting",
            second_names
        )

    def test_approach_cat_triggers_social_meeting_when_near(
        self
    ):
        first, second = (
            self._social_pair()
        )

        first.mind[
            "current_intention"
        ] = {
            "type": "approach_cat",
            "target": second.name
        }

        result = (
            self.cats
            .execute_cat_intention(
                first
            )
        )

        self.assertEqual(
            result["name"],
            "cat_approach_completed"
        )

        self.assertTrue(
            result["executed"]
        )

        self.assertIn(
            "social",
            result
        )

        self.assertEqual(
            result[
                "social"
            ]["name"],
            "cat_social_meeting"
        )

    def test_social_system_does_not_repeat_greeting_while_still_near(
        self
    ):
        first, second = (
            self._social_pair()
        )

        social = CatSocialSystem(
            self.cats
        )

        first.state = (
            "near_target_cat"
        )

        first_result = social.meet(
            first,
            second
        )

        self.assertTrue(
            first_result["socialized"]
        )

        second_result = social.meet(
            first,
            second
        )

        self.assertFalse(
            second_result["socialized"]
        )

        self.assertEqual(
            second_result["reason"],
            "already_greeted_while_near"
        )


    def test_social_meeting_creates_memory_for_both_cats(
        self
    ):
        first, second = (
            self._social_pair()
        )

        social = CatSocialSystem(
            self.cats
        )

        result = social.meet(
            first,
            second
        )

        self.assertTrue(
            result["socialized"]
        )

        self.assertIn(
            second.name,
            first.social_memory
        )

        self.assertIn(
            first.name,
            second.social_memory
        )

        first_memory = (
            first.social_memory[
                second.name
            ]
        )

        self.assertEqual(
            first_memory["meet_count"],
            1
        )

        self.assertEqual(
            first_memory[
                "uncertain_count"
            ],
            1
        )

        self.assertEqual(
            first_memory[
                "last_outcome"
            ],
            "kept_distance"
        )

    def test_friendly_memory_biases_future_assessment(
        self
    ):
        first, second = (
            self._social_pair()
        )

        first.relationships[
            second.name
        ] = {
            "familiarity": 0.6,
            "trust": 0.65,
            "affiliation": 0.5,
            "tension": 0.0
        }

        first.social_memory[
            second.name
        ] = {
            "meet_count": 4,
            "friendly_count": 4,
            "uncertain_count": 0,
            "hostile_count": 0,
            "last_attitude": "friendly",
            "last_outcome": "head_bunt",
            "last_steps": [
                "cat_head_bunt"
            ],
            "recent_outcomes": [
                "nose_touch",
                "head_bunt"
            ]
        }

        social = CatSocialSystem(
            self.cats
        )

        assessment = social.assess(
            first,
            second
        )

        self.assertGreater(
            assessment[
                "memory_bias"
            ],
            0.0
        )

        self.assertEqual(
            assessment[
                "positive_social_memories"
            ],
            4
        )

        self.assertEqual(
            assessment[
                "last_social_outcome"
            ],
            "head_bunt"
        )

    def test_repeated_hostile_memory_can_make_cat_hostile(
        self
    ):
        first, second = (
            self._social_pair()
        )

        first.relationships[
            second.name
        ] = {
            "familiarity": 0.5,
            "trust": 0.5,
            "affiliation": 0.0,
            "tension": 0.2
        }

        first.social_memory[
            second.name
        ] = {
            "meet_count": 4,
            "friendly_count": 0,
            "uncertain_count": 0,
            "hostile_count": 4,
            "last_attitude": "hostile",
            "last_outcome": "hiss",
            "last_steps": [
                "cat_hissed_at_cat"
            ],
            "recent_outcomes": [
                "hiss",
                "warning_swat",
                "hiss",
                "hiss"
            ]
        }

        social = CatSocialSystem(
            self.cats
        )

        assessment = social.assess(
            first,
            second
        )

        self.assertEqual(
            assessment[
                "attitude"
            ],
            "hostile"
        )

        self.assertLess(
            assessment[
                "memory_bias"
            ],
            0.0
        )

        self.assertEqual(
            assessment[
                "negative_social_memories"
            ],
            4
        )

    def test_social_memory_keeps_only_five_recent_outcomes(
        self
    ):
        first, second = (
            self._social_pair()
        )

        social = CatSocialSystem(
            self.cats
        )

        for index in range(
            7
        ):
            social._remember_meeting(
                first,
                second,
                attitude="uncertain",
                outcome=f"outcome_{index}",
                steps=[]
            )

        memory = first.social_memory[
            second.name
        ]

        self.assertEqual(
            len(
                memory[
                    "recent_outcomes"
                ]
            ),
            5
        )

        self.assertEqual(
            memory[
                "recent_outcomes"
            ],
            [
                "outcome_2",
                "outcome_3",
                "outcome_4",
                "outcome_5",
                "outcome_6"
            ]
        )


if __name__ == "__main__":
    unittest.main()
