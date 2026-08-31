import unittest
from universe.universe import Universe
from cats.cats import Cats
from cats.cat_family_system import CatFamilySystem

class CatFamilySystemTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.family = CatFamilySystem(self.cats)
        self.mother = self.cats.create_cat(name='mother', color='black', fur_length='short')
        self.mother.sex = 'female'
        self.father = self.cats.create_cat(name='father', color='orange', fur_length='short')
        self.father.sex = 'male'

    def _kitten(self, name, father_name='father'):
        kitten = self.cats.create_cat(name=name, color='white', fur_length='short')
        kitten.mother_name = self.mother.name
        kitten.father_name = father_name
        kitten.parents = {'mother': self.mother.name, 'father': father_name}
        return kitten

    def test_register_birth_sets_parents(self):
        kitten = self._kitten('kitten_1')
        self.family.register_birth(mother=self.mother, kittens=[kitten], cats=self.cats.cats)
        self.assertEqual(kitten.family.parents['mother'], self.mother.name)
        self.assertEqual(kitten.family.parents['father'], self.father.name)

    def test_mother_registers_child(self):
        kitten = self._kitten('kitten_1')
        self.family.register_birth(mother=self.mother, kittens=[kitten], cats=self.cats.cats)
        self.assertIn(kitten.name, self.mother.family.children)

    def test_known_father_registers_child(self):
        kitten = self._kitten('kitten_1')
        self.family.register_birth(mother=self.mother, kittens=[kitten], cats=self.cats.cats)
        self.assertIn(kitten.name, self.father.family.children)

    def test_same_parent_kittens_are_siblings_and_littermates(self):
        first = self._kitten('kitten_1')
        second = self._kitten('kitten_2')
        self.family.register_birth(mother=self.mother, kittens=[first, second], cats=self.cats.cats)
        self.assertIn(second.name, first.family.siblings)
        self.assertIn(second.name, first.family.littermates)
        self.assertEqual(self.family.relation(first, second), 'sibling_littermate')

    def test_different_fathers_make_half_sibling_littermates(self):
        first = self._kitten('kitten_1', father_name='father')
        second = self._kitten('kitten_2', father_name='other_father')
        self.family.register_birth(mother=self.mother, kittens=[first, second], cats=self.cats.cats)
        self.assertIn(second.name, first.family.half_siblings)
        self.assertIn(second.name, first.family.littermates)
        self.assertEqual(self.family.relation(first, second), 'half_sibling_littermate')

    def test_parent_child_relations_are_directional(self):
        kitten = self._kitten('kitten_1')
        self.family.register_birth(mother=self.mother, kittens=[kitten], cats=self.cats.cats)
        self.assertEqual(self.family.relation(kitten, self.mother), 'mother')
        self.assertEqual(self.family.relation(self.mother, kitten), 'child')

    def test_unrelated_cats_are_not_family(self):
        kitten = self._kitten('kitten_1')
        stranger = self.cats.create_cat(name='stranger', color='gray', fur_length='short')
        self.family.register_birth(mother=self.mother, kittens=[kitten], cats=self.cats.cats)
        self.assertFalse(self.family.are_related(kitten, stranger))
        self.assertIsNone(self.family.relation(kitten, stranger))
if __name__ == '__main__':
    unittest.main()
