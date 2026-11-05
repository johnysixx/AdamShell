from multiverse.registry import UniverseRegistryRecord


class UniverseManual:

    def __init__(self, universe_registry):
        self.name = "universe_manual"
        self.location = "back_room_table"
        self.allowed_reader = "bartender"
        self._universe_registry = universe_registry

    def read(self, reader):
        reader_name = getattr(
            reader,
            "name",
            None
        )

        if reader_name != self.allowed_reader:
            return None

        snapshot = {}

        for universe_id, record in (
            self._universe_registry.universes.items()
        ):
            if not isinstance(
                record,
                UniverseRegistryRecord,
            ):
                raise TypeError(
                    "Universe manual requires "
                    "UniverseRegistryRecord objects."
                )

            if record.id != universe_id:
                raise ValueError(
                    "Universe registry ID mismatch."
                )

            snapshot[universe_id] = record.to_dict()

        return snapshot

    @property
    def public_state(self):
        return {
            "name": self.name,
            "location": self.location,
            "allowed_reader": self.allowed_reader,
            "registered_universe_count": len(
                self._universe_registry.universes
            )
        }
