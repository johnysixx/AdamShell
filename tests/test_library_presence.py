import unittest

from universe.universe import Universe
from gods.gods import Gods
from library import Library


class LibraryPresenceTests(unittest.TestCase):

    def make_library(
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

        library = Library(
            universe
        )

        library.assign_librarian(
            god
        )

        return (
            universe,
            gods,
            god,
            library
        )


    def test_library_is_open_by_default(
        self
    ):
        _, _, _, library = (
            self.make_library()
        )

        self.assertTrue(
            library.is_open
        )

        self.assertEqual(
            library.door["state"],
            "open"
        )

        self.assertEqual(
            library.door["sign"],
            "OPEN"
        )


    def test_library_shows_god_is_in_only_when_physically_present(
        self
    ):
        _, _, god, library = (
            self.make_library()
        )

        library.god_enters(
            god
        )

        self.assertTrue(
            library.god_present
        )

        self.assertEqual(
            library.door["god_sign"],
            "GOD IS: IN"
        )

        library.god_leaves(
            god
        )

        self.assertFalse(
            library.god_present
        )

        self.assertIsNone(
            library.door["god_sign"]
        )

        self.assertTrue(
            library.is_open
        )


    def test_mask_changes_do_not_change_library_open_state(
        self
    ):
        _, gods, god, library = (
            self.make_library()
        )

        self.assertTrue(
            library.is_open
        )

        gods.assume_mask(
            god=god,
            mask_name="director",
            role="quantum_director"
        )

        self.assertTrue(
            library.is_open
        )

        self.assertEqual(
            library.door["sign"],
            "OPEN"
        )

        gods.release_mask(
            god=god,
            mask_name="director"
        )

        self.assertTrue(
            library.is_open
        )

        self.assertEqual(
            library.door["sign"],
            "OPEN"
        )


    def test_pilgrim_can_enter_when_god_is_absent(
        self
    ):
        _, _, god, library = (
            self.make_library()
        )

        library.god_leaves(
            god
        )

        pilgrim = {
            "name": "pilgrim_1",
            "type": "pilgrim"
        }

        entered = library.enter(
            pilgrim
        )

        self.assertTrue(
            entered
        )

        self.assertIn(
            pilgrim,
            library.visitors
        )

        self.assertFalse(
            library.god_present
        )

        self.assertEqual(
            library.door["sign"],
            "OPEN"
        )

        self.assertIsNone(
            library.door["god_sign"]
        )


    def test_pilgrim_can_enter_while_god_is_present(
        self
    ):
        _, _, god, library = (
            self.make_library()
        )

        library.god_enters(
            god
        )

        pilgrim = {
            "name": "pilgrim_2",
            "type": "pilgrim"
        }

        entered = library.enter(
            pilgrim
        )

        self.assertTrue(
            entered
        )

        self.assertIn(
            pilgrim,
            library.visitors
        )

        self.assertEqual(
            library.door["god_sign"],
            "GOD IS: IN"
        )



    def test_god_is_born_as_librarian_and_starts_in_library(
        self
    ):
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

        god["book"]["location"] = "library"

        self.assertEqual(
            god["role"],
            "librarian"
        )

        self.assertIs(
            library.librarian,
            god
        )

        self.assertTrue(
            library.god_present
        )

        self.assertEqual(
            library.door["god_sign"],
            "GOD IS: IN"
        )

        self.assertEqual(
            god["book"]["location"],
            "library"
        )

        self.assertEqual(
            god["book"]["entries"][0]["event"],
            "god_born"
        )


if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()

