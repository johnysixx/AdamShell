from universe.logger import UniverseLogger

class Library:

    def __init__(self, universe):
        self.universe = universe
        self.books = []
        self.catalog = []
        self.events = []
        self.visitors = []
        self.tick_count = 0

        self.librarian = None
        self.god_present = False
        self.is_open = True
        self.door_sign = "OPEN"

        self.door = {
            "state": "open",
            "sign": "OPEN",
            "god_sign": None
        }

        self.access = {
            "from": "quantum_layer",
            "exit_to": "meeting_place",
            "eden": False,
            "universe": False
        }

        self.permissions = {
            "god": "write",
            "serpent": "read",
            "pazuzu": "read",
            "classical_probe_debug_entity": "read",
            "meeting_place": "read"
        }

        self.state = {
            "type": "knowledge_layer",
            "state": "initialized",
            "librarian": self.librarian,
            "access": self.access,
            "permissions": self.permissions,
            "books": self.books
        }

        self.universe.world["library"] = self.state
        UniverseLogger.boot("LIBRARY INITIALIZED")

    def assign_librarian(
        self,
        god
    ):
        self.librarian = god

        self.state[
            "librarian"
        ] = god

        self.update_presence()

        return god

    def update_presence(self):
        self.is_open = True
        self.door_sign = "OPEN"

        self.door["state"] = "open"
        self.door["sign"] = "OPEN"

        self.state["god_present"] = (
            self.god_present
        )

        self.state["is_open"] = True
        self.state["door_sign"] = "OPEN"

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
            self.state["librarian"] = god

        self.god_present = True

        self.door["god_sign"] = (
            "GOD IS: IN"
        )

        self.state[
            "god_present"
        ] = True

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
                book.get("library_status")
                == "checked_out_for_edit"
                and book.get("holder") is god
            )
        ]

        if checked_out_books:
            raise RuntimeError(
                "God must return all books checked out for edit before leaving the library."
            )

        self.god_present = False

        self.door["god_sign"] = None

        self.state[
            "god_present"
        ] = False

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

        book["location"] = (
            "library_shelf"
        )

        book["library_status"] = (
            "shelved"
        )

        book["holder"] = None

        self.state[
            "books"
        ] = self.books

        self.state[
            "catalog"
        ] = self.catalog

        UniverseLogger.event(
            "BOOK SHELVED: "
            f"{book.get('author', 'unknown')}"
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

        if book.get(
            "library_status"
        ) != "shelved":
            raise RuntimeError(
                "Book is not available on the shelf."
            )

        book[
            "library_status"
        ] = "checked_out_for_edit"

        book[
            "holder"
        ] = editor

        book[
            "location"
        ] = "with_god"

        UniverseLogger.event(
            "BOOK CHECKED OUT FOR EDIT: "
            f"{book.get('author', 'unknown')}"
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

        book[
            "library_status"
        ] = "shelved"

        book[
            "holder"
        ] = None

        book[
            "location"
        ] = "library_shelf"

        UniverseLogger.event(
            "BOOK RETURNED: "
            f"{book.get('author', 'unknown')}"
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

        if book.get(
            "library_status"
        ) != "checked_out_for_edit":
            raise RuntimeError(
                "Book must be checked out for edit before writing."
            )

        if book.get(
            "holder"
        ) is not editor:
            raise RuntimeError(
                "Only the current holder may edit the book."
            )

        book[
            "entries"
        ].append(
            dict(entry)
        )

        UniverseLogger.event(
            "BOOK ENTRY WRITTEN: "
            f"{book.get('author', 'unknown')}"
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

        if book.get(
            "library_status"
        ) != "checked_out_for_edit":
            raise RuntimeError(
                "Book must be checked out for edit before receiving energy."
            )

        if book.get(
            "holder"
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

        available = editor.get(
            "energy_j",
            0.0
        )

        if amount_j > available:
            raise ValueError(
                "Editor does not have enough energy."
            )

        editor["energy_j"] -= amount_j

        book["energy_j"] = (
            book.get(
                "energy_j",
                0.0
            )
            + amount_j
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
        UniverseLogger.event(f"BOOK ADDED: {book['title']}")

    def read_books(self, entity_name):
        if not self.can_read(entity_name):
            UniverseLogger.event(f"LIBRARY READ DENIED: {entity_name}")
            return []

        UniverseLogger.event(f"LIBRARY READ GRANTED: {entity_name}")
        return self.books

    def emit_event(self, event):
        self.events.append(event)
        UniverseLogger.event(f"LIBRARY EVENT: {event}")

    def tick(self):
        self.tick_count += 1
        UniverseLogger.event(f"LIBRARY TICK {self.tick_count}")
        self._clear_events()

    def _clear_events(self):
        self.events = []




