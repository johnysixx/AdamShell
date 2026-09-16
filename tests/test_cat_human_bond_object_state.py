import unittest

from cats.cat_components import CatHumanBond
from cats.cat_human_bond_system import CatHumanBondSystem
from cats.cats import Cats
from universe.universe import Universe


class Human:

    def __init__(self, name):
        self.name = name


class CatHumanBondObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(
            name="bond_cat",
            color="black",
            fur_length="short",
        )
        self.human = Human("johny")
        self.system = CatHumanBondSystem(
            self.cats
        )

    def test_new_human_bond_is_object(self):
        self.system.remember_interaction(
            self.cat,
            self.human,
            positive=True,
            significance=0.1,
        )

        bond = self.cat.human_bonds[
            self.human.name
        ]

        self.assertIsInstance(
            bond,
            CatHumanBond,
        )
        self.assertEqual(
            bond.human,
            self.human.name,
        )
        self.assertEqual(
            bond.encounters,
            1,
        )

    def test_positive_interactions_update_object_state(self):
        self.system.remember_interaction(
            self.cat,
            self.human,
            positive=True,
            significance=0.2,
        )

        bond = self.cat.human_bonds[
            self.human.name
        ]

        self.assertEqual(
            bond.positive_interactions,
            1,
        )
        self.assertGreater(
            bond.trust,
            0.5,
        )
        self.assertGreater(
            bond.affection,
            0.0,
        )

    def test_evaluation_updates_object_state(self):
        for _ in range(8):
            self.system.remember_interaction(
                self.cat,
                self.human,
                positive=True,
                significance=0.15,
            )

        result = self.system.evaluate(
            self.cat,
            self.human,
        )
        bond = self.cat.human_bonds[
            self.human.name
        ]

        self.assertTrue(
            result["right_human"]
        )
        self.assertTrue(
            bond.recognized_as_right_human
        )
        self.assertEqual(
            bond.right_human_score,
            result["score"],
        )


if __name__ == "__main__":
    unittest.main()
