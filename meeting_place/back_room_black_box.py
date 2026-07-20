class BackRoomBlackBox:

    def __init__(self):
        self.name = "back_room_black_box"
        self.type = "immutable_bar_system_recorder"
        self.location = "back_room"
        self.access = "bar_internal_only"
        self.entries = []

        print("BACK ROOM BLACK BOX CREATED")

    def record(
        self,
        event,
        data=None,
        source="meeting_place",
        tick=None
    ):
        entry = {
            "tick": tick,
            "source": source,
            "event": event,
            "data": data
        }

        self.entries.append(entry)

        print(
            "BACK ROOM BLACK BOX ENTRY: "
            f"[{source}] {event}"
        )

        return entry

    @property
    def entry_count(self):
        return len(self.entries)

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "access": self.access,
            "entry_count": self.entry_count
        }
