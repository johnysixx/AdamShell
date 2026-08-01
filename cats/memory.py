from copy import deepcopy


class CatMemory:

    def __init__(self, cat_name):
        self.cat_name = str(cat_name)
        self.events = []
        self.sequence = 0

    def remember(
        self,
        event_type,
        universe_tick=None,
        location=None,
        participants=None,
        details=None
    ):
        self.sequence += 1

        memory = {
            "memory_id": (
                f"{self.cat_name}_memory_"
                f"{self.sequence}"
            ),
            "sequence": self.sequence,
            "event_type": str(event_type),
            "universe_tick": universe_tick,
            "location": location,
            "participants": list(
                participants or []
            ),
            "details": deepcopy(
                details or {}
            )
        }

        self.events.append(memory)

        return deepcopy(memory)

    def recall(
        self,
        event_type=None,
        participant=None
    ):
        memories = self.events

        if event_type is not None:
            memories = [
                memory
                for memory in memories
                if memory["event_type"] == event_type
            ]

        if participant is not None:
            memories = [
                memory
                for memory in memories
                if participant
                in memory["participants"]
            ]

        return deepcopy(memories)

    def remember_entity(
        self,
        event_type,
        entity,
        universe_tick=None,
        location=None,
        extra_details=None
    ):
        entity_name = getattr(
            entity,
            "name",
            str(entity)
        )

        public_state = getattr(
            entity,
            "public_state",
            None
        )

        if callable(public_state):
            entity_state = public_state()
        elif public_state is not None:
            entity_state = public_state
        else:
            entity_state = {
                "name": entity_name,
                "state": getattr(
                    entity,
                    "state",
                    None
                ),
                "location": getattr(
                    entity,
                    "location",
                    None
                )
            }

        details = {
            "entity": deepcopy(
                entity_state
            )
        }

        details.update(
            deepcopy(extra_details or {})
        )

        return self.remember(
            event_type=event_type,
            universe_tick=universe_tick,
            location=location,
            participants=[entity_name],
            details=details
        )

    @property
    def cronenberg_encounters(self):
        return self.recall(
            event_type="cronenberg_encounter"
        )

    @property
    def cronenbergs_eaten(self):
        return [
            memory
            for memory in self.cronenberg_encounters
            if memory["details"].get(
                "result"
            ) == "cronenberg_hunted"
        ]

    @property
    def routes(self):
        return [
            memory
            for memory in self.events
            if memory["event_type"].startswith(
                "route_"
            )
        ]

    @property
    def public_state(self):
        return {
            "cat_name": self.cat_name,
            "memory_count": len(
                self.events
            ),
            "events": deepcopy(
                self.events
            )
        }
