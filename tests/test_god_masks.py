import unittest
from dataclasses import FrozenInstanceError
from universe.universe import Universe
from gods.gods import Gods
from gods.gods_state import (
    GodMaskEntry,
    GodMaskRegistry,
    GodMaskReleasedResult,
)

class GodMaskTests(unittest.TestCase):

    def test_god_starts_with_empty_object_registry(self):
        universe = Universe()
        gods = Gods(universe)
        god = gods.create_god(
            name="god",
            role="creator_entity",
        )

        self.assertIsInstance(
            god.masks,
            GodMaskRegistry,
        )

        self.assertEqual(god.masks.entries, ())
        self.assertIsNone(god.active_mask)

        for method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(god.masks, method)
            )

        with self.assertRaises(TypeError):
            _ = god.masks["director"]

        with self.assertRaises(FrozenInstanceError):
            god.masks.entries = ()

        with self.assertRaises(TypeError):
            GodMaskRegistry(entries={})

    def test_mask_registry_is_replaced_immutably(self):
        universe = Universe()
        gods = Gods(universe)
        god = gods.create_god(
            name="god",
            role="creator_entity",
        )

        initial = god.masks

        director = gods.assume_mask(
            god=god,
            mask_name="director",
            role="quantum_director",
        )

        first = god.masks

        self.assertIsNot(first, initial)
        self.assertEqual(initial.entries, ())
        self.assertEqual(len(first.entries), 1)
        self.assertIsInstance(
            first.entries[0],
            GodMaskEntry,
        )
        self.assertIs(
            first.mask_named("director"),
            director,
        )
        self.assertIsNone(
            first.mask_named("creator")
        )

        marduk = gods.assume_mask(
            god=god,
            mask_name="marduk",
            role="divine_champion",
        )

        second = god.masks

        self.assertIsNot(second, first)
        self.assertEqual(len(first.entries), 1)
        self.assertEqual(len(second.entries), 2)
        self.assertIs(
            second.mask_named("director"),
            director,
        )
        self.assertIs(
            second.mask_named("marduk"),
            marduk,
        )

        result = gods.release_mask(
            god=god,
            mask_name="marduk",
        )

        self.assertIs(result.mask, marduk)
        self.assertIs(god.masks, second)
        self.assertFalse(marduk.active)
        self.assertIsNone(god.active_mask)

    def test_replacing_named_mask_keeps_registry_unique(self):
        universe = Universe()
        gods = Gods(universe)
        god = gods.create_god(
            name="god",
            role="creator_entity",
        )

        original = gods.assume_mask(
            god=god,
            mask_name="director",
            role="first_role",
        )

        old_registry = god.masks

        replacement = gods.assume_mask(
            god=god,
            mask_name="director",
            role="second_role",
        )

        self.assertIsNot(god.masks, old_registry)
        self.assertEqual(len(god.masks.entries), 1)

        self.assertIs(
            old_registry.mask_named("director"),
            original,
        )
        self.assertIs(
            god.masks.mask_named("director"),
            replacement,
        )

        with self.assertRaises(RuntimeError):
            gods.release_mask(
                god=god,
                mask_name="missing_mask",
            )

        self.assertIsInstance(
            god.masks,
            GodMaskRegistry,
        )


    def test_director_is_mask_of_existing_god(self):
        universe = Universe()
        gods = Gods(universe)
        god = gods.create_god(name='god', role='creator_entity')
        director = gods.assume_mask(god=god, mask_name='director', role='quantum_director')
        self.assertIs(director.mask_of, god)
        self.assertEqual(director.name, 'director')
        self.assertEqual(director.role, 'quantum_director')
        self.assertIs(director.knowledge, god.knowledge)
        self.assertIs(director.research_book, god.research_book)
        self.assertEqual(god.name, 'god')

    def test_quantum_director_wraps_god_director_mask(self):
        from quantum.director import QuantumDirector
        universe = Universe()
        gods = Gods(universe)
        god = gods.create_god(name='god', role='creator_entity')
        director = QuantumDirector(universe=universe, god=god, gods=gods)
        self.assertIs(director.god, god)
        self.assertIs(director.mask.mask_of, god)
        self.assertEqual(director.mask.name, 'director')
        self.assertIs(director.knowledge, god.knowledge)
        self.assertIs(director.research_book, god.research_book)

    def test_god_can_release_marduk_mask_without_losing_memory(self):
        universe = Universe()
        gods = Gods(universe)
        god = gods.create_god(name='god', role='creator_entity')
        marduk = gods.assume_mask(god=god, mask_name='marduk', role='divine_champion')
        god.knowledge.add('tiamat_defeated')
        god.research_book.append({'event': 'cosmos_ordered'})
        knowledge = god.knowledge
        research_book = god.research_book
        released = gods.release_mask(god=god, mask_name='marduk')
        self.assertIsInstance(
            released,
            GodMaskReleasedResult,
        )
        self.assertEqual(
            released.released_mask,
            'marduk',
        )
        self.assertIs(
            released.god,
            god,
        )
        self.assertIs(
            released.mask,
            marduk,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    released,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = released[
                'released_mask'
            ]
        self.assertIsNone(god.active_mask)
        self.assertIs(god.knowledge, knowledge)
        self.assertIs(god.research_book, research_book)
        self.assertIn('tiamat_defeated', god.knowledge)
        self.assertEqual(god.research_book[0]['event'], 'cosmos_ordered')
        self.assertEqual(god.name, 'god')
        self.assertFalse(getattr(marduk, 'active', False))

    def test_god_can_switch_from_marduk_to_director_without_losing_memory(self):
        universe = Universe()
        gods = Gods(universe)
        god = gods.create_god(name='god', role='creator_entity')
        marduk = gods.assume_mask(god=god, mask_name='marduk', role='divine_champion')
        god.knowledge.add('cosmos_ordered')
        god.research_book.append({'event': 'tiamat_defeated'})
        knowledge = god.knowledge
        research_book = god.research_book
        gods.release_mask(god=god, mask_name='marduk')
        director = gods.assume_mask(god=god, mask_name='director', role='quantum_director')
        self.assertFalse(marduk.active)
        self.assertTrue(director.active)
        self.assertEqual(god.active_mask, 'director')
        self.assertIs(director.knowledge, knowledge)
        self.assertIs(director.research_book, research_book)
        self.assertIn('cosmos_ordered', director.knowledge)
        self.assertEqual(director.research_book[0]['event'], 'tiamat_defeated')
if __name__ == '__main__':
    unittest.main()
if __name__ == '__main__':
    unittest.main()
if __name__ == '__main__':
    unittest.main()
if __name__ == '__main__':
    unittest.main()
