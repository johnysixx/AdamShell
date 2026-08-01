class MeetingBootstrap:

    def __init__(self, layers, god, serpent, pazuzu):
        self.layers = layers
        self.god = god
        self.serpent = serpent
        self.pazuzu = pazuzu

    def run(self):
        meeting = self.layers.get("meeting")
        library = self.layers.get("library")

        meeting.add_entity(self.god)
        meeting.add_entity(self.serpent)
        meeting.add_entity(self.pazuzu)
        meeting.add_entity(self.pazuzu)

        meeting.show_library_book_count(library)
        meeting.show_book_search_terminal()
        meeting.show_random_library_excerpt(library)
        meeting.show_cronenberg_pen_terminal()

        meeting.serve_lemonade(
            self.god,
            location="inside_bar"
        )

        meeting.emit_event("eden idea was born in the bar")

