import unittest

from gods.gods import Gods
from library import Library
from library.library_state import LibraryState
from universe.universe import Universe


class LibraryObjectStateTests(unittest.TestCase):

    def _library(self):
        universe = Universe()
        library = Library(universe)

        return universe, library

    def _library_with_god(self):
        universe, library = self._library()
        gods = Gods(universe)
        god = gods.create_god(
            name="god",
            role="librarian",
        )

        library.assign_librarian(god)

        return universe, library, gods, god

    def test_state_is_object_only(self):
        state = LibraryState()

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(state, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = state["god_present"]

    def test_initial_values_are_preserved(self):
        _, library = self._library()
        state = library.library_state

        self.assertIs(library.state, state)
        self.assertEqual(state.layer_type, "knowledge_layer")
        self.assertEqual(state.status, "initialized")
        self.assertIsNone(state.librarian)
        self.assertFalse(state.god_present)
        self.assertTrue(state.is_open)
        self.assertEqual(state.door_sign, "OPEN")
        self.assertEqual(state.books, [])
        self.assertEqual(state.catalog, [])
        self.assertEqual(state.events, [])
        self.assertEqual(state.visitors, [])
        self.assertEqual(state.tick_count, 0)

    def test_collections_are_owned_by_state_object(self):
        _, library = self._library()
        state = library.library_state

        self.assertIs(library.books, state.books)
        self.assertIs(library.catalog, state.catalog)
        self.assertIs(library.events, state.events)
        self.assertIs(library.visitors, state.visitors)
        self.assertIs(library.door, state.door)
        self.assertIs(library.access, state.access)
        self.assertIs(library.permissions, state.permissions)

    def test_world_keeps_object_and_dict_boundaries(self):
        universe, library = self._library()

        self.assertIs(
            universe.world["library_state"],
            library.library_state,
        )
        self.assertIsInstance(
            universe.world["library"],
            dict,
        )
        self.assertIsInstance(
            universe.world["library"]["library_state"],
            dict,
        )

    def test_public_collections_remain_live_boundaries(self):
        universe, library = self._library()
        boundary = universe.world["library"]

        self.assertIs(boundary["books"], library.books)
        self.assertIs(boundary["catalog"], library.catalog)
        self.assertIs(boundary["access"], library.access)
        self.assertIs(
            boundary["permissions"],
            library.permissions,
        )

    def test_librarian_presence_mutates_same_state_object(self):
        universe, library, _, god = self._library_with_god()
        state = library.library_state

        library.god_enters(god)

        self.assertIs(library.library_state, state)
        self.assertIs(state.librarian, god)
        self.assertTrue(state.god_present)
        self.assertEqual(state.door["god_sign"], "GOD IS: IN")
        self.assertTrue(
            universe.world["library"]["god_present"]
        )

        library.god_leaves(god)

        self.assertFalse(state.god_present)
        self.assertIsNone(state.door["god_sign"])

    def test_visitor_entry_mutates_same_state_object(self):
        universe, library = self._library()
        state = library.library_state
        visitor = {
            "name": "pilgrim",
            "type": "pilgrim",
        }

        result = library.enter(visitor)

        self.assertTrue(result)
        self.assertIs(library.library_state, state)
        self.assertEqual(state.visitors, [visitor])
        self.assertEqual(
            universe.world["library"]["library_state"][
                "visitors"
            ],
            [visitor],
        )

    def test_shelving_mutates_same_state_object(self):
        universe, library, gods, god = self._library_with_god()
        state = library.library_state
        book = gods.create_book(god)

        library.shelve_book(book)

        self.assertIs(library.library_state, state)
        self.assertEqual(state.books, [book])
        self.assertEqual(state.catalog, [book])
        self.assertIs(
            universe.world["library"]["books"],
            state.books,
        )

    def test_permissions_remain_collection_boundary(self):
        _, library = self._library()

        self.assertTrue(library.can_read("serpent"))
        self.assertTrue(library.can_write("god"))
        self.assertFalse(library.can_write("serpent"))

    def test_events_and_tick_mutate_same_state_object(self):
        _, library = self._library()
        state = library.library_state

        library.emit_event("book_opened")

        self.assertEqual(state.events, ["book_opened"])

        library.tick()

        self.assertIs(library.library_state, state)
        self.assertEqual(state.tick_count, 1)
        self.assertEqual(state.events, [])

    def test_public_state_snapshot_is_detached(self):
        _, library = self._library()
        snapshot = library.public_state["library_state"]

        snapshot["permissions"]["god"] = "read"
        snapshot["books"].append("changed")
        snapshot["door"]["state"] = "closed"

        self.assertEqual(
            library.library_state.permissions["god"],
            "write",
        )
        self.assertEqual(library.library_state.books, [])
        self.assertEqual(
            library.library_state.door["state"],
            "open",
        )

    def test_to_dict_is_detached_boundary(self):
        state = LibraryState()
        snapshot = state.to_dict()

        snapshot["access"]["eden"] = True
        snapshot["events"].append("changed")

        self.assertFalse(state.access["eden"])
        self.assertEqual(state.events, [])


if __name__ == "__main__":
    unittest.main()
