import unittest

from cats.cat_social_objects import CatSocialMemory
from cats.cat_social_system import CatSocialSystem
from cats.cats import Cats
from universe.universe import Universe


class CatSocialMemoryObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.first = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short",
        )
        self.second = self.cats.create_cat(
            name="second",
            color="white",
            fur_length="short",
        )
        self.first.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }
        self.second.position = dict(
            self.first.position
        )
        self.system = CatSocialSystem(
            self.cats
        )

    def test_meeting_creates_social_memory_object(self):
        self.system.meet(
            self.first,
            self.second,
        )

        memory = self.first.social_memory[
            self.second.name
        ]

        self.assertIsInstance(
            memory,
            CatSocialMemory,
        )
        self.assertEqual(
            memory.meet_count,
            1,
        )

    def test_social_memory_tracks_last_outcome(self):
        result = self.system.meet(
            self.first,
            self.second,
        )
        memory = self.first.social_memory[
            self.second.name
        ]

        self.assertEqual(
            memory.last_attitude,
            result["attitude"],
        )
        self.assertEqual(
            memory.last_outcome,
            result["outcome"],
        )

    def test_social_memory_limits_recent_outcomes(self):
        for index in range(7):
            self.system._remember_meeting(
                self.first,
                self.second,
                attitude="uncertain",
                outcome=f"outcome_{index}",
                steps=[],
            )

        memory = self.first.social_memory[
            self.second.name
        ]

        self.assertEqual(
            memory.recent_outcomes,
            [
                "outcome_2",
                "outcome_3",
                "outcome_4",
                "outcome_5",
                "outcome_6",
            ],
        )


if __name__ == "__main__":
    unittest.main()
