import unittest

from universe.universe import Universe
from gods.gods import Gods


class GodBookTests(unittest.TestCase):

    def test_god_begins_writing_his_book_at_birth(
        self
    ):
        universe = Universe()

        gods = Gods(
            universe
        )

        god = gods.create_god(
            name="god",
            role="creator_entity"
        )

        book = god["book"]

        self.assertEqual(
            book["type"],
            "god_book"
        )

        self.assertEqual(
            book["author"],
            "god"
        )

        self.assertEqual(
            book["state"],
            "being_written"
        )

        self.assertEqual(
            book["energy_j"],
            0.0
        )

        self.assertEqual(
            book["location"],
            "with_author"
        )

        self.assertEqual(
            len(book["entries"]),
            1
        )

        self.assertEqual(
            book["entries"][0]["event"],
            "god_born"
        )

        self.assertEqual(
            book["entries"][0]["subject"],
            "god"
        )



    def test_god_starts_day_zero_in_library_not_at_bar(
        self
    ):
        from library import Library

        universe = Universe()

        gods = Gods(
            universe
        )

        library = Library(
            universe
        )

        god = gods.create_god(
            name="god",
            role="librarian"
        )

        library.assign_librarian(
            god
        )

        library.god_enters(
            god
        )

        library.shelve_book(
            god["book"]
        )

        self.assertEqual(
            god["role"],
            "librarian"
        )

        self.assertTrue(
            library.god_present
        )

        self.assertEqual(
            library.door["god_sign"],
            "GOD IS: IN"
        )

        self.assertEqual(
            god["book"]["library_status"],
            "shelved"
        )

        self.assertIn(
            god["book"],
            library.catalog
        )

    def test_god_places_his_book_on_library_shelf_and_catalogs_it(
        self
    ):
        from library import Library

        universe = Universe()

        gods = Gods(
            universe
        )

        library = Library(
            universe
        )

        god = gods.create_god(
            name="god",
            role="librarian"
        )

        library.assign_librarian(
            god
        )

        library.god_enters(
            god
        )

        result = library.shelve_book(
            god["book"]
        )

        self.assertTrue(
            result
        )

        self.assertIn(
            god["book"],
            library.books
        )

        self.assertEqual(
            god["book"]["location"],
            "library_shelf"
        )

        self.assertEqual(
            god["book"]["library_status"],
            "shelved"
        )

        self.assertIsNone(
            god["book"]["holder"]
        )

        self.assertIn(
            god["book"],
            library.catalog
        )



    def test_god_can_check_out_his_book_for_edit_only_while_in_library(
        self
    ):
        from library import Library

        universe = Universe()

        gods = Gods(
            universe
        )

        library = Library(
            universe
        )

        god = gods.create_god(
            name="god",
            role="librarian"
        )

        library.assign_librarian(
            god
        )

        library.god_enters(
            god
        )

        library.shelve_book(
            god["book"]
        )

        checked_out = (
            library
            .check_out_for_edit(
                book=god["book"],
                editor=god
            )
        )

        self.assertTrue(
            checked_out
        )

        self.assertEqual(
            god["book"]["library_status"],
            "checked_out_for_edit"
        )

        self.assertIs(
            god["book"]["holder"],
            god
        )

        self.assertEqual(
            god["book"]["location"],
            "with_god"
        )

        library.return_book(
            god["book"]
        )

        library.god_leaves(
            god
        )

        with self.assertRaises(
            RuntimeError
        ):
            library.check_out_for_edit(
                book=god["book"],
                editor=god
            )



    def test_god_can_write_book_only_while_holding_it_for_edit(
        self
    ):
        from library import Library

        universe = Universe()

        gods = Gods(
            universe
        )

        library = Library(
            universe
        )

        god = gods.create_god(
            name="god",
            role="librarian"
        )

        library.assign_librarian(
            god
        )

        library.god_enters(
            god
        )

        library.shelve_book(
            god["book"]
        )

        with self.assertRaises(
            RuntimeError
        ):
            library.write_book_entry(
                book=god["book"],
                editor=god,
                entry={
                    "event": "first_library_day"
                }
            )

        library.check_out_for_edit(
            book=god["book"],
            editor=god
        )

        written = library.write_book_entry(
            book=god["book"],
            editor=god,
            entry={
                "event": "first_library_day"
            }
        )

        self.assertTrue(
            written
        )

        self.assertEqual(
            god["book"]["entries"][-1]["event"],
            "first_library_day"
        )

        self.assertIs(
            god["book"]["holder"],
            god
        )

        self.assertEqual(
            god["book"]["library_status"],
            "checked_out_for_edit"
        )

        library.return_book(
            god["book"]
        )

        self.assertEqual(
            god["book"]["library_status"],
            "shelved"
        )



    def test_god_can_transfer_energy_into_book_only_while_editing_it(
        self
    ):
        from library import Library

        universe = Universe()

        gods = Gods(
            universe
        )

        library = Library(
            universe
        )

        god = gods.create_god(
            name="god",
            role="librarian"
        )

        library.assign_librarian(
            god
        )

        library.god_enters(
            god
        )

        library.shelve_book(
            god["book"]
        )

        library.check_out_for_edit(
            book=god["book"],
            editor=god
        )

        god_energy_before = god[
            "energy_j"
        ]

        book_energy_before = god[
            "book"
        ][
            "energy_j"
        ]

        amount = 1.0

        result = library.transfer_energy_to_book(
            book=god["book"],
            editor=god,
            amount_j=amount
        )

        self.assertTrue(
            result
        )

        self.assertEqual(
            god["energy_j"],
            god_energy_before - amount
        )

        self.assertEqual(
            god["book"]["energy_j"],
            book_energy_before + amount
        )

        self.assertEqual(
            god["energy_j"]
            + god["book"]["energy_j"],
            god_energy_before
            + book_energy_before
        )


if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()





