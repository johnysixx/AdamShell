from universe.logger import UniverseLogger
from dataclasses import dataclass
import random


@dataclass(slots=True, frozen=True)
class BarTerminalDefinition:
    name: str
    type: str
    purpose: str

    def __post_init__(self):
        for field_name in (
            "name",
            "type",
            "purpose",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value:
                raise TypeError(
                    "Bar terminal definitions require "
                    "nonempty strings."
                )

    def to_dict(self):
        return {
            "type": self.type,
            "purpose": self.purpose,
        }


class BarTerminals:

    def __init__(self):
        self.terminals = {
            "book_count_terminal": BarTerminalDefinition(
                name="book_count_terminal",
                type="display",
                purpose="show_library_book_count",
            ),
            "book_search_terminal": BarTerminalDefinition(
                name="book_search_terminal",
                type="reservation_placeholder",
                purpose="search_and_read_books_later",
            ),
            "random_excerpt_terminal": BarTerminalDefinition(
                name="random_excerpt_terminal",
                type="display",
                purpose="show_random_library_excerpt",
            ),
            "bar_story_count_terminal": BarTerminalDefinition(
                name="bar_story_count_terminal",
                type="display",
                purpose="show_bar_story_count",
            ),
        }

        UniverseLogger.event("BAR TERMINALS CREATED")

    def show_book_count(self, library):
        books = library.read_books("meeting_place")
        count = len(books)

        UniverseLogger.event(f"BOOK COUNT TERMINAL: {count}")
        return count

    def show_bar_story_count(self, bar_counter):
        stories = bar_counter.read_bar_stories()
        count = len(stories)

        UniverseLogger.event(f"BAR STORY COUNT TERMINAL: {count}")
        return count

    def show_book_search_placeholder(self):
        UniverseLogger.event("BOOK SEARCH TERMINAL: reservation system pending")
        return None

    def show_random_excerpt(self, library):
        books = library.read_books("meeting_place")
        excerpts = self._collect_excerpts(books)

        if not excerpts:
            UniverseLogger.event("RANDOM EXCERPT TERMINAL: no excerpts available")
            return None

        excerpt = random.choice(excerpts)
        UniverseLogger.event(f"RANDOM EXCERPT TERMINAL: {excerpt}")
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


