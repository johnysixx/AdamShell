import unittest
from universe.universe import Universe
from gods.gods import Gods
from library import Library
from library.god_book import GodBook
from library.god_book_library_status import (
    GodBookLibraryStatus,
)

class GodBookTests(unittest.TestCase):

    def test_god_is_born_without_book(self):
        universe = Universe()
        gods = Gods(universe)
        god = gods.create_god(name='god', role='librarian')
        self.assertFalse(god.book_created)
        self.assertFalse(hasattr(god, 'book'))

    def test_god_starts_day_zero_in_library_not_at_bar(self):
        from library import Library
        universe = Universe()
        gods = Gods(universe)
        library = Library(universe)
        god = gods.create_god(name='god', role='librarian')
        library.assign_librarian(god)
        library.god_enters(god)
        gods.create_book(god)
        library.shelve_book(god.book)
        self.assertEqual(god.role, 'librarian')
        self.assertTrue(library.god_present)
        self.assertEqual(library.door.god_sign, 'GOD IS: IN')
        self.assertIs(
            god.book.library_status,
            GodBookLibraryStatus.SHELVED,
        )
        self.assertIn(god.book, library.catalog)

    def test_god_places_his_book_on_library_shelf_and_catalogs_it(self):
        from library import Library
        universe = Universe()
        gods = Gods(universe)
        library = Library(universe)
        god = gods.create_god(name='god', role='librarian')
        library.assign_librarian(god)
        library.god_enters(god)
        gods.create_book(god)
        result = library.shelve_book(god.book)
        self.assertTrue(result)
        self.assertIn(god.book, library.books)
        self.assertEqual(god.book.location, 'library_shelf')
        self.assertIs(
            god.book.library_status,
            GodBookLibraryStatus.SHELVED,
        )
        self.assertIsNone(god.book.holder)
        self.assertIn(god.book, library.catalog)

    def test_god_can_check_out_his_book_for_edit_only_while_in_library(self):
        from library import Library
        universe = Universe()
        gods = Gods(universe)
        library = Library(universe)
        god = gods.create_god(name='god', role='librarian')
        library.assign_librarian(god)
        library.god_enters(god)
        gods.create_book(god)
        library.shelve_book(god.book)
        checked_out = library.check_out_for_edit(book=god.book, editor=god)
        self.assertTrue(checked_out)
        self.assertIs(
            god.book.library_status,
            GodBookLibraryStatus.CHECKED_OUT_FOR_EDIT,
        )
        self.assertIs(god.book.holder, god)
        self.assertEqual(god.book.location, 'with_god')
        library.return_book(god.book)
        library.god_leaves(god)
        with self.assertRaises(RuntimeError):
            library.check_out_for_edit(book=god.book, editor=god)

    def test_god_can_write_book_only_while_holding_it_for_edit(self):
        from library import Library
        universe = Universe()
        gods = Gods(universe)
        library = Library(universe)
        god = gods.create_god(name='god', role='librarian')
        library.assign_librarian(god)
        library.god_enters(god)
        gods.create_book(god)
        library.shelve_book(god.book)
        with self.assertRaises(RuntimeError):
            library.write_book_entry(book=god.book, editor=god, entry={'event': 'first_library_day'})
        library.check_out_for_edit(book=god.book, editor=god)
        written = library.write_book_entry(book=god.book, editor=god, entry={'event': 'first_library_day'})
        self.assertTrue(written)
        self.assertEqual(god.book.entries[-1]['event'], 'first_library_day')
        self.assertIs(god.book.holder, god)
        self.assertIs(
            god.book.library_status,
            GodBookLibraryStatus.CHECKED_OUT_FOR_EDIT,
        )
        library.return_book(god.book)
        self.assertIs(
            god.book.library_status,
            GodBookLibraryStatus.SHELVED,
        )

    def test_write_entry_detaches_nested_input_data(self):
        book = GodBook(author="god")
        entries = book.entries

        source = {
            "event": "first_record",
            "details": {
                "notes": ["original"],
                "metadata": {
                    "codes": [1],
                },
            },
        }

        book.write_entry(source)

        self.assertIs(
            book.entries,
            entries,
        )

        self.assertIsNot(
            book.entries[0],
            source,
        )

        self.assertIsNot(
            book.entries[0]["details"],
            source["details"],
        )

        source["details"]["notes"].append(
            "later_source_change"
        )

        source["details"]["metadata"][
            "codes"
        ].append(2)

        self.assertEqual(
            book.entries[0]["details"]["notes"],
            ["original"],
        )

        self.assertEqual(
            book.entries[0]["details"][
                "metadata"
            ]["codes"],
            [1],
        )

        self.assertEqual(
            book.entries[0]["event"],
            "first_record",
        )

    def test_book_entries_capture_separate_history_versions(self):
        book = GodBook(author="god")
        entries = book.entries

        source = {
            "event": "observation",
            "details": {
                "notes": ["original"],
            },
        }

        book.write_entry(source)

        first = book.entries[0]

        source["details"]["notes"].append(
            "later_source_change"
        )

        book.write_entry(source)

        second = book.entries[1]

        self.assertEqual(
            first["details"]["notes"],
            ["original"],
        )

        self.assertEqual(
            second["details"]["notes"],
            ["original", "later_source_change"],
        )

        first["details"]["notes"].append(
            "edited_first_entry"
        )

        self.assertEqual(
            second["details"]["notes"],
            ["original", "later_source_change"],
        )

        self.assertEqual(
            source["details"]["notes"],
            ["original", "later_source_change"],
        )

        self.assertIs(
            book.entries,
            entries,
        )

        self.assertIs(
            book.entries[0],
            first,
        )

        self.assertIs(
            book.entries[1],
            second,
        )

        self.assertIsNot(
            first["details"],
            second["details"],
        )

    def test_library_write_preserves_book_identity_and_history(self):
        universe = Universe()
        gods = Gods(universe)
        library = Library(universe)

        god = gods.create_god(
            name="god",
            role="librarian",
        )

        library.assign_librarian(god)
        library.god_enters(god)

        book = gods.create_book(god)

        library.shelve_book(book)
        library.check_out_for_edit(
            book=book,
            editor=god,
        )

        entries = book.entries

        source = {
            "event": "first_library_day",
            "details": {
                "witnesses": ["serpent"],
                "metadata": {
                    "notes": ["original"],
                },
            },
        }

        written = library.write_book_entry(
            book=book,
            editor=god,
            entry=source,
        )

        self.assertTrue(written)

        self.assertIs(
            god.book,
            book,
        )

        self.assertIs(
            library.books[0],
            book,
        )

        self.assertIs(
            library.catalog[0],
            book,
        )

        self.assertIs(
            universe.world["library"][
                "books"
            ],
            library.books,
        )

        self.assertIs(
            book.entries,
            entries,
        )

        source["details"]["witnesses"].append(
            "later_source_change"
        )

        source["details"]["metadata"][
            "notes"
        ].append("later_source_change")

        self.assertEqual(
            book.entries[0]["details"][
                "witnesses"
            ],
            ["serpent"],
        )

        self.assertEqual(
            book.entries[0]["details"][
                "metadata"
            ]["notes"],
            ["original"],
        )

        library.return_book(book)

        self.assertIs(
            book.library_status,
            GodBookLibraryStatus.SHELVED,
        )

        self.assertIs(
            library.catalog[0],
            book,
        )

        self.assertIs(
            book.entries,
            entries,
        )

        self.assertEqual(
            book.entries[0]["event"],
            "first_library_day",
        )

    def test_god_can_transfer_energy_into_book_only_while_editing_it(self):
        from library import Library
        universe = Universe()
        gods = Gods(universe)
        library = Library(universe)
        god = gods.create_god(name='god', role='librarian')
        library.assign_librarian(god)
        library.god_enters(god)
        gods.create_book(god)
        library.shelve_book(god.book)
        library.check_out_for_edit(book=god.book, editor=god)
        god_energy_before = god.energy_j
        book_energy_before = god.book.energy_j
        amount = 1.0
        result = library.transfer_energy_to_book(book=god.book, editor=god, amount_j=amount)
        self.assertTrue(result)
        self.assertEqual(god.energy_j, god_energy_before - amount)
        self.assertEqual(god.book.energy_j, book_energy_before + amount)
        self.assertEqual(god.energy_j + god.book.energy_j, god_energy_before + book_energy_before)
if __name__ == '__main__':
    unittest.main()
if __name__ == '__main__':
    unittest.main()
if __name__ == '__main__':
    unittest.main()
if __name__ == '__main__':
    unittest.main()
if __name__ == '__main__':
    unittest.main()
if __name__ == '__main__':
    unittest.main()
