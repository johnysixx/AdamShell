from library.library_state import LibraryState
from universe.logger import UniverseLogger


class Library:

    def __init__(self, universe):
        self.universe = universe
        self.library_state = LibraryState()
        self.state = self.library_state

        self.write_to_world()
        UniverseLogger.boot("LIBRARY INITIALIZED")

    @property
    def books(self):
        return self.library_state.books

    @books.setter
    def books(self, value):
        self.library_state.books = value

    @property
    def catalog(self):
        return self.library_state.catalog

    @catalog.setter
    def catalog(self, value):
        self.library_state.catalog = value

    @property
    def events(self):
        return self.library_state.events

    @events.setter
    def events(self, value):
        self.library_state.events = value

    @property
    def visitors(self):
        return self.library_state.visitors

    @visitors.setter
    def visitors(self, value):
        self.library_state.visitors = value

    @property
    def tick_count(self):
        return self.library_state.tick_count

    @tick_count.setter
    def tick_count(self, value):
        self.library_state.tick_count = value

    @property
    def librarian(self):
        return self.library_state.librarian

    @librarian.setter
    def librarian(self, value):
        self.library_state.librarian = value

    @property
    def god_present(self):
        return self.library_state.god_present

    @god_present.setter
    def god_present(self, value):
        self.library_state.god_present = value

    @property
    def is_open(self):
        return self.library_state.is_open

    @is_open.setter
    def is_open(self, value):
        self.library_state.is_open = value

    @property
    def door_sign(self):
        return self.library_state.door_sign

    @door_sign.setter
    def door_sign(self, value):
        self.library_state.door_sign = value

    @property
    def door(self):
        return self.library_state.door

    @door.setter
    def door(self, value):
        self.library_state.door = value

    @property
    def access(self):
        return self.library_state.access

    @access.setter
    def access(self, value):
        self.library_state.access = value

    @property
    def permissions(self):
        return self.library_state.permissions

    @permissions.setter
    def permissions(self, value):
        self.library_state.permissions = value

    @property
    def public_state(self):
        return {
            "type": self.library_state.layer_type,
            "state": self.library_state.status,
            "librarian": self.librarian,
            "access": self.access,
            "permissions": self.permissions,
            "books": self.books,
            "catalog": self.catalog,
            "god_present": self.god_present,
            "is_open": self.is_open,
            "door_sign": self.door_sign,
            "library_state": self.library_state.to_dict(),
        }

    def write_to_world(self):
        self.universe.world["library"] = self.public_state
        self.universe.world["library_state"] = (
            self.library_state
        )

    def assign_librarian(
        self,
        god
    ):
        self.librarian = god

        self.update_presence()

        return god

    def update_presence(self):
        self.is_open = True
        self.door_sign = "OPEN"

        self.door["state"] = "open"
        self.door["sign"] = "OPEN"

        self.write_to_world()

        return {
            "god_present": self.god_present,
            "is_open": True,
            "door_sign": "OPEN"
        }

    def enter(
        self,
        visitor
    ):
        self.update_presence()

        name = visitor.get(
            "name",
            "unknown"
        )

        if not self.is_open:
            UniverseLogger.event(
                f"LIBRARY ENTRY DENIED: {name}"
            )
            return False

        if visitor not in self.visitors:
            self.visitors.append(
                visitor
            )

        self.write_to_world()

        UniverseLogger.event(
            f"LIBRARY ENTRY GRANTED: {name}"
        )

        return True

    def god_enters(
        self,
        god
    ):
        if self.librarian is not god:
            self.librarian = god

        self.god_present = True

        self.door["god_sign"] = (
            "GOD IS: IN"
        )

        self.write_to_world()

        return {
            "event": "god_entered_library",
            "god": god,
            "door_sign": self.door["god_sign"]
        }

    def god_leaves(
        self,
        god
    ):
        if self.librarian is not god:
            raise RuntimeError(
                "God is not the assigned librarian."
            )

        checked_out_books = [
            book
            for book in self.catalog
            if (
                getattr(
                    book,
                    "library_status",
                    None
                )
                == "checked_out_for_edit"
                and getattr(
                    book,
                    "holder",
                    None
                ) is god
            )
        ]

        if checked_out_books:
            raise RuntimeError(
                "God must return all books checked out for edit before leaving the library."
            )

        self.god_present = False

        self.door["god_sign"] = None

        self.write_to_world()

        return {
            "event": "god_left_library",
            "god": god
        }

    def shelve_book(
        self,
        book
    ):
        if book not in self.books:
            self.books.append(
                book
            )

        if book not in self.catalog:
            self.catalog.append(
                book
            )

        book.shelve()

        self.write_to_world()

        UniverseLogger.event(
            "BOOK SHELVED: "
            f"{getattr(book, 'author', 'unknown')}"
        )

        return True

    def check_out_for_edit(
        self,
        book,
        editor
    ):
        if editor is self.librarian:
            if not self.god_present:
                raise RuntimeError(
                    "God must be physically present in the library to edit a book."
                )

        if book not in self.catalog:
            raise RuntimeError(
                "Book is not registered in the library catalog."
            )

        if getattr(
            book,
            "library_status",
            None
        ) != "shelved":
            raise RuntimeError(
                "Book is not available on the shelf."
            )

        book.check_out_for_edit(
            editor
        )

        UniverseLogger.event(
            "BOOK CHECKED OUT FOR EDIT: "
            f"{getattr(book, 'author', 'unknown')}"
        )

        return True

    def return_book(
        self,
        book
    ):
        if book not in self.catalog:
            raise RuntimeError(
                "Book is not registered in the library catalog."
            )

        book.return_to_shelf()

        UniverseLogger.event(
            "BOOK RETURNED: "
            f"{getattr(book, 'author', 'unknown')}"
        )

        return True

    def write_book_entry(
        self,
        book,
        editor,
        entry
    ):
        if book not in self.catalog:
            raise RuntimeError(
                "Book is not registered in the library catalog."
            )

        if getattr(
            book,
            "library_status",
            None
        ) != "checked_out_for_edit":
            raise RuntimeError(
                "Book must be checked out for edit before writing."
            )

        if getattr(
            book,
            "holder",
            None
        ) is not editor:
            raise RuntimeError(
                "Only the current holder may edit the book."
            )

        book.write_entry(
            entry
        )

        UniverseLogger.event(
            "BOOK ENTRY WRITTEN: "
            f"{getattr(book, 'author', 'unknown')}"
        )

        return True

    def transfer_energy_to_book(
        self,
        book,
        editor,
        amount_j
    ):
        if book not in self.catalog:
            raise RuntimeError(
                "Book is not registered in the library catalog."
            )

        if getattr(
            book,
            "library_status",
            None
        ) != "checked_out_for_edit":
            raise RuntimeError(
                "Book must be checked out for edit before receiving energy."
            )

        if getattr(
            book,
            "holder",
            None
        ) is not editor:
            raise RuntimeError(
                "Only the current holder may transfer energy into the book."
            )

        if editor is self.librarian:
            if not self.god_present:
                raise RuntimeError(
                    "God must be physically present in the library."
                )

        if amount_j <= 0.0:
            raise ValueError(
                "Transferred energy must be positive."
            )

        available = getattr(
            editor,
            "energy_j",
            0.0
        )

        if amount_j > available:
            raise ValueError(
                "Editor does not have enough energy."
            )

        editor.energy_j -= amount_j

        book.receive_energy(
            amount_j
        )

        UniverseLogger.event(
            "ENERGY TRANSFERRED TO BOOK: "
            f"{amount_j} J"
        )

        return True

    def can_read(self, entity_name):
        return self.permissions.get(entity_name) in ["read", "write"]

    def can_write(self, entity_name):
        return self.permissions.get(entity_name) == "write"

    def add_book(self, entity_name, book):
        if not self.can_write(entity_name):
            UniverseLogger.event(f"LIBRARY WRITE DENIED: {entity_name}")
            return

        self.books.append(book)
        self.write_to_world()
        UniverseLogger.event(
            f"BOOK ADDED: {book.title}"
        )

    def read_books(self, entity_name):
        if not self.can_read(entity_name):
            UniverseLogger.event(f"LIBRARY READ DENIED: {entity_name}")
            return []

        UniverseLogger.event(f"LIBRARY READ GRANTED: {entity_name}")
        return self.books

    def emit_event(self, event):
        self.events.append(event)
        self.write_to_world()
        UniverseLogger.event(f"LIBRARY EVENT: {event}")

    def tick(self):
        self.tick_count += 1
        UniverseLogger.event(f"LIBRARY TICK {self.tick_count}")
        self._clear_events()
        self.write_to_world()

    def _clear_events(self):
        self.events = []


