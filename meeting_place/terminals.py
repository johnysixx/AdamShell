import random


class BarTerminals:

    def __init__(self):
        self.terminals = {
            "book_count_terminal": {
                "type": "display",
                "purpose": "show_library_book_count"
            },
            "book_search_terminal": {
                "type": "reservation_placeholder",
                "purpose": "search_and_read_books_later"
            },
            "random_excerpt_terminal": {
                "type": "display",
                "purpose": "show_random_library_excerpt"
            }
        }

        print("BAR TERMINALS CREATED")

    def show_book_count(self, library):
        books = library.read_books("meeting_place")
        count = len(books)

        print(f"BOOK COUNT TERMINAL: {count}")
        return count

    def show_book_search_placeholder(self):
        print("BOOK SEARCH TERMINAL: reservation system pending")
        return None

    def show_random_excerpt(self, library):
        books = library.read_books("meeting_place")
        excerpts = self._collect_excerpts(books)

        if not excerpts:
            print("RANDOM EXCERPT TERMINAL: no excerpts available")
            return None

        excerpt = random.choice(excerpts)
        print(f"RANDOM EXCERPT TERMINAL: {excerpt}")
        return excerpt

    def _collect_excerpts(self, books):
        excerpts = []

        for book in books:
            if not isinstance(book, dict):
                continue

            if "excerpts" in book and isinstance(book["excerpts"], list):
                excerpts.extend(book["excerpts"])
                continue

            if "excerpt" in book:
                excerpts.append(book["excerpt"])
                continue

            if "content" in book:
                excerpts.append(book["content"][:160])
                continue

            if "text" in book:
                excerpts.append(book["text"][:160])
                continue

        return excerpts
    