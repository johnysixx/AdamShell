from copy import deepcopy
from dataclasses import (
    fields,
    is_dataclass,
)

from core.entity.components import (
    SpatialVector3,
)
from cats.cat_memory_record import (
    CatMemoryRecord,
)
from cats.cat_cronenberg_encounter_memory_details import (
    CatCronenbergEncounterMemoryDetails,
)


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
        self._require_events()
        self.sequence += 1

        memory = CatMemoryRecord(
            memory_id=(
                f"{self.cat_name}_memory_"
                f"{self.sequence}"
            ),
            sequence=self.sequence,
            event_type=str(
                event_type
            ),
            universe_tick=universe_tick,
            location=deepcopy(
                location
            ),
            participants=list(
                participants or []
            ),
            details=deepcopy(
                details or {}
            ),
        )

        self.events.append(
            memory
        )

        return deepcopy(
            memory
        )

    def recall(
        self,
        event_type=None,
        participant=None
    ):
        memories = (
            self._require_events()
        )

        if event_type is not None:
            memories = [
                memory
                for memory in memories
                if (
                    memory.event_type
                    == event_type
                )
            ]

        if participant is not None:
            memories = [
                memory
                for memory in memories
                if participant
                in memory.participants
            ]

        return deepcopy(
            memories
        )

    def _require_events(
        self,
    ):
        if not isinstance(
            self.events,
            list,
        ):
            raise TypeError(
                "Cat memory events "
                "must be list."
            )

        for memory in self.events:

            if not isinstance(
                memory,
                CatMemoryRecord,
            ):
                raise TypeError(
                    "Cat memory record "
                    "must be "
                    "CatMemoryRecord."
                )

        return self.events

    def records(
        self,
    ):
        return tuple(
            self._require_events()
        )

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
        memories = (
            self.cronenberg_encounters
        )

        for memory in memories:
            if not isinstance(
                memory.details,
                CatCronenbergEncounterMemoryDetails,
            ):
                raise TypeError(
                    "Cronenberg encounter memory "
                    "details must use "
                    "CatCronenbergEncounterMemoryDetails."
                )

        return [
            memory
            for memory in memories
            if (
                memory.details.result
                == "cronenberg_hunted"
            )
        ]

    @property
    def routes(self):
        return [
            memory
            for memory
            in self._require_events()
            if memory.event_type.startswith(
                "route_"
            )
        ]

    @property
    def public_state(self):

        def snapshot_value(
            value,
        ):
            if isinstance(
                value,
                SpatialVector3,
            ):
                return value.to_dict()

            if is_dataclass(
                value
            ):
                return {
                    item.name:
                        snapshot_value(
                            getattr(
                                value,
                                item.name,
                            )
                        )
                    for item
                    in fields(value)
                }

            if isinstance(
                value,
                dict,
            ):
                return {
                    key:
                        snapshot_value(
                            item
                        )
                    for key, item
                    in value.items()
                }

            if isinstance(
                value,
                list,
            ):
                return [
                    snapshot_value(
                        item
                    )
                    for item
                    in value
                ]

            if isinstance(
                value,
                tuple,
            ):
                return tuple(
                    snapshot_value(
                        item
                    )
                    for item
                    in value
                )

            return deepcopy(
                value
            )

        return {
            "cat_name": self.cat_name,
            "memory_count": len(
                self.events
            ),
            "events": [
                {
                    "memory_id":
                        memory.memory_id,
                    "sequence":
                        memory.sequence,
                    "event_type":
                        memory.event_type,
                    "universe_tick":
                        memory.universe_tick,
                    "location":
                        snapshot_value(
                            memory.location
                        ),
                    "participants":
                        deepcopy(
                            memory.participants
                        ),
                    "details":
                        snapshot_value(
                            memory.details
                        ),
                }
                for memory
                in self._require_events()
            ],
        }
