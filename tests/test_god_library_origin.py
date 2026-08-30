import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import UniverseBootstrap

class GodLibraryOriginTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.registry = UniverseRegistry()
        bootstrap = UniverseBootstrap(universe_registry=self.registry, universe=self.universe)
        bootstrap.run()
        self.god = self.universe.god
        self.library = self.universe.library

    def test_god_is_librarian(self):
        self.assertEqual(self.god.role, 'librarian')
        self.assertIs(self.library.librarian, self.god)

    def test_god_enters_library_before_bar_history(self):
        self.assertTrue(self.library.god_present)
        self.assertTrue(self.library.state['god_present'])

    def test_god_book_is_created_as_separate_event(self):
        self.assertTrue(self.god.book_created)
        self.assertTrue(hasattr(self.god, 'book'))
        book = self.god.book
        self.assertEqual(book.type, 'god_book')
        self.assertEqual(book.entries, [])

    def test_god_book_is_shelved_in_library(self):
        book = self.god.book
        self.assertIn(book, self.library.books)
        self.assertIn(book, self.library.catalog)

    def test_god_is_not_creator(self):
        self.assertNotEqual(self.god.role, 'creator_entity')
        self.assertFalse(hasattr(self.god, 'creator_of'))
if __name__ == '__main__':
    unittest.main()
