import unittest

from library.god_book import GodBook
from library.god_book_library_status import (
    GodBookLibraryStatus,
)


class GodBookLibraryStatusObjectStateTests(
    unittest.TestCase
):

    def test_book_starts_unregistered_as_enum(self):
        book = GodBook(
            author="god"
        )

        self.assertIs(
            book.library_status,
            GodBookLibraryStatus.UNREGISTERED,
        )

    def test_shelve_sets_enum_status(self):
        book = GodBook(
            author="god"
        )

        book.shelve()

        self.assertIs(
            book.library_status,
            GodBookLibraryStatus.SHELVED,
        )

    def test_check_out_and_return_use_enum_status(self):
        book = GodBook(
            author="god"
        )

        holder = object()

        book.shelve()
        book.check_out_for_edit(
            holder
        )

        self.assertIs(
            book.library_status,
            GodBookLibraryStatus.CHECKED_OUT_FOR_EDIT,
        )

        self.assertTrue(
            book.is_checked_out_by(
                holder
            )
        )

        book.return_to_shelf()

        self.assertIs(
            book.library_status,
            GodBookLibraryStatus.SHELVED,
        )

    def test_string_status_is_rejected(self):
        book = GodBook(
            author="god"
        )

        with self.assertRaises(TypeError):
            book.library_status = "shelved"

    def test_status_values_define_domain(self):
        self.assertEqual(
            {
                status.value
                for status
                in GodBookLibraryStatus
            },
            {
                "unregistered",
                "shelved",
                "checked_out_for_edit",
            },
        )


if __name__ == "__main__":
    unittest.main()
