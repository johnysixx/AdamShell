class Library:

    def __init__(self, universe):
        self.universe = universe
        self.books = []
        self.events = []
        self.tick_count = 0

        self.librarian = "god"

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
        print("LIBRARY INITIALIZED")

    def can_read(self, entity_name):
        return self.permissions.get(entity_name) in ["read", "write"]

    def can_write(self, entity_name):
        return self.permissions.get(entity_name) == "write"

    def add_book(self, entity_name, book):
        if not self.can_write(entity_name):
            print(f"LIBRARY WRITE DENIED: {entity_name}")
            return

        self.books.append(book)
        print(f"BOOK ADDED: {book['title']}")

    def read_books(self, entity_name):
        if not self.can_read(entity_name):
            print(f"LIBRARY READ DENIED: {entity_name}")
            return []

        print(f"LIBRARY READ GRANTED: {entity_name}")
        return self.books

    def emit_event(self, event):
        self.events.append(event)
        print(f"LIBRARY EVENT: {event}")

    def tick(self):
        self.tick_count += 1
        print(f"LIBRARY TICK {self.tick_count}")
        self._clear_events()

    def _clear_events(self):
        self.events = []

