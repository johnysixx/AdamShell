import random

from universe.logger import UniverseLogger
from cats.cat_personality import CatPersonality


class CatCronenbergEncounter:

    def __init__(
        self,
        default_cat_size=1.0
    ):
        self.default_cat_size = float(
            default_cat_size
        )

        self.history = []

    def resolve(
        self,
        cat,
        cronenberg,
        route,
        universe,
        rng=None
    ):
        rng = rng or random

        cronenberg_position = self._position_of(
            cronenberg
        )

        if cronenberg_position is None:
            return {
                "result": "no_position",
                "encountered": False
            }

        if not route.position_matches(
            cronenberg_position
        ):
            return {
                "result": "paths_do_not_cross",
                "encountered": False
            }

        cat_name = self._cat_name(cat)
        cat_size = self._cat_size(cat)

        cronenberg_size = float(
            cronenberg.size
        )

        size_ratio = (
            cronenberg_size
            / cat_size
        )

        if size_ratio > 1.20:
            detour = route.make_minimal_detour(
                cronenberg_position
            )

            event = {
                "result": "cat_avoids_cronenberg",
                "encountered": True,
                "cat": cat_name,
                "cronenberg": cronenberg.name,
                "size_ratio": size_ratio,
                "detour": detour,
                "destination": route.destination
            }

            route.record_encounter(event)
            self.history.append(event)

            UniverseLogger.event(
                f"CAT AVOIDS LARGE CRONENBERG: "
                f"{cat_name} AVOIDS "
                f"{cronenberg.name}"
            )

            self._remember_encounter(
                cat=cat,
                cronenberg=cronenberg,
                universe=universe,
                result="cat_avoids_cronenberg",
                size_ratio=size_ratio,
                location=getattr(
                    cronenberg,
                    "location",
                    "quantum_layer"
                ),
                details={
                    "detour": dict(detour),
                    "destination": route.destination
                }
            )

            event["personality"] = (
                self._apply_personality_experience(
                    cat=cat,
                    source="avoided_large_cronenberg",
                    changes={
                        "patience": 0.03,
                        "courage": 0.01
                    },
                    metadata={
                        "cronenberg": cronenberg.name,
                        "size_ratio": size_ratio,
                        "decision": "minimal_detour"
                    }
                )
            )
            return event

        escape_chance = (
            self._escape_chance(
                size_ratio
            )
        )

        escaped = (
            rng.random()
            < escape_chance
        )

        if escaped:
            cronenberg.state = (
                "escaped_cat_encounter"
            )

            event = {
                "result": "cronenberg_escaped",
                "encountered": True,
                "cat": cat_name,
                "cronenberg": cronenberg.name,
                "size_ratio": size_ratio,
                "escape_chance": escape_chance,
                "destination": route.destination
            }

            route.record_encounter(event)
            self.history.append(event)

            UniverseLogger.event(
                f"CRONENBERG ESCAPES CAT: "
                f"{cronenberg.name} ESCAPES "
                f"{cat_name}"
            )

            self._remember_encounter(
                cat=cat,
                cronenberg=cronenberg,
                universe=universe,
                result="cronenberg_escaped",
                size_ratio=size_ratio,
                location=getattr(
                    cronenberg,
                    "location",
                    "quantum_layer"
                ),
                details={
                    "escape_chance": escape_chance,
                    "destination": route.destination
                }
            )

            event["personality"] = (
                self._apply_personality_experience(
                    cat=cat,
                    source="cronenberg_escaped",
                    changes={
                        "patience": 0.02,
                        "curiosity": 0.01
                    },
                    metadata={
                        "cronenberg": cronenberg.name,
                        "size_ratio": size_ratio,
                        "escape_chance": escape_chance
                    }
                )
            )
            return event

        encounter_layer = getattr(
            cronenberg,
            "location",
            "quantum_layer"
        )

        cat_growth = cronenberg_size * 0.05
        strength_gain = cronenberg_size * 0.10

        if isinstance(cat, dict):
            cat["size"] = float(
                cat.get(
                    "size",
                    self.default_cat_size
                )
            ) + cat_growth

            cat["strength"] = float(
                cat.get(
                    "strength",
                    1.0
                )
            ) + strength_gain

            cat["cronenbergs_eaten"] = int(
                cat.get(
                    "cronenbergs_eaten",
                    0
                )
            ) + 1

            cat["cronenberg_mass_eaten"] = float(
                cat.get(
                    "cronenberg_mass_eaten",
                    0.0
                )
            ) + cronenberg_size
        else:
            cat.size = float(
                getattr(
                    cat,
                    "size",
                    self.default_cat_size
                )
            ) + cat_growth

            cat.strength = float(
                getattr(
                    cat,
                    "strength",
                    1.0
                )
            ) + strength_gain

            cat.cronenbergs_eaten = int(
                getattr(
                    cat,
                    "cronenbergs_eaten",
                    0
                )
            ) + 1

            cat.cronenberg_mass_eaten = float(
                getattr(
                    cat,
                    "cronenberg_mass_eaten",
                    0.0
                )
            ) + cronenberg_size


        self._remember_encounter(
            cat=cat,
            cronenberg=cronenberg,
            universe=universe,
            result="cronenberg_hunted",
            size_ratio=size_ratio,
            location=encounter_layer,
            details={
                "escape_chance": escape_chance,
                "cat_growth": cat_growth,
                "strength_gain": strength_gain
            }
        )

        cronenberg.state = (
            "hunted_by_cat"
        )

        cronenberg.location = (
            "inside_cat"
        )

        event_result = (
            universe.quantum_event_bus.publish(
                "cronenberg_hunted",
                predator=cat_name,
                prey=cronenberg.name,
                layer=getattr(
                    cronenberg,
                    "location",
                    "quantum_layer"
                ),
                cronenberg_size=cronenberg_size,
                cat_size=cat_size
            )
        )

        event = {
            "result": "cronenberg_hunted",
            "encountered": True,
            "cat": cat_name,
            "cronenberg": cronenberg.name,
            "size_ratio": size_ratio,
            "escape_chance": escape_chance,
            "cat_growth": cat_growth,
            "strength_gain": strength_gain,
            "destination": route.destination,
            "subscriber_count": (
                event_result[
                    "subscriber_count"
                ]
            )
        }

        route.record_encounter(event)
        self.history.append(event)

        UniverseLogger.event(
            f"CAT HUNTS SMALL CRONENBERG: "
            f"{cat_name} HUNTS "
            f"{cronenberg.name}"
        )

        event["personality"] = (
            self._apply_personality_experience(
                cat=cat,
                source="successful_cronenberg_hunt",
                changes={
                    "courage": 0.04,
                    "aggression": 0.025,
                    "curiosity": 0.01
                },
                metadata={
                    "cronenberg": cronenberg.name,
                    "size_ratio": size_ratio
                }
            )
        )

        return event

    def _apply_personality_experience(
        self,
        cat,
        source,
        changes,
        metadata=None
    ):
        if not isinstance(
            cat,
            dict
        ):
            return {
                "name": (
                    "cat_personality_experience_skipped"
                ),
                "reason": (
                    "unsupported_cat_representation"
                ),
                "source": source,
                "applied": False
            }

        return CatPersonality.apply_experience(
            cat=cat,
            source=source,
            changes=changes,
            metadata=metadata
        )

    def _remember_encounter(
        self,
        cat,
        cronenberg,
        universe,
        result,
        size_ratio,
        location,
        details=None
    ):
        memory = (
            cat.get("memory")
            if isinstance(cat, dict)
            else getattr(cat, "memory", None)
        )

        if memory is None:
            return None

        encounter_details = {
            "result": result,
            "size_ratio": float(size_ratio),
            "cronenberg_id": cronenberg.name,
            "cronenberg_size": float(
                getattr(cronenberg, "size", 0.0)
            ),
            "cronenberg_energy": float(
                getattr(cronenberg, "energy", 0.0)
            ),
            "origin": dict(
                getattr(cronenberg, "origin", {})
            ),
            "traits": (
                cronenberg.traits.snapshot()
                if hasattr(cronenberg, "traits")
                else {}
            ),
            "trait_birth_influences": (
                list(
                    cronenberg.traits.birth_influences
                )
                if hasattr(cronenberg, "traits")
                else []
            ),
            "quantum_links": list(
                getattr(
                    cronenberg,
                    "quantum_links",
                    []
                )
            )
        }

        encounter_details.update(
            details or {}
        )

        return memory.remember(
            event_type="cronenberg_encounter",
            universe_tick=getattr(
                universe,
                "universe_tick",
                None
            ),
            location=location,
            participants=[
                cronenberg.name
            ],
            details=encounter_details
        )

    def _escape_chance(
        self,
        size_ratio
    ):
        if size_ratio < 0.50:
            return 0.05

        if size_ratio < 0.80:
            return 0.25

        return 0.50

    def _cat_name(self, cat):
        if isinstance(cat, dict):
            return cat.get(
                "name",
                "cat"
            )

        return getattr(
            cat,
            "name",
            "cat"
        )

    def _cat_size(self, cat):
        if isinstance(cat, dict):
            return float(
                cat.get(
                    "size",
                    self.default_cat_size
                )
            )

        return float(
            getattr(
                cat,
                "size",
                self.default_cat_size
            )
        )

    def _position_of(self, cronenberg):
        position = getattr(
            cronenberg,
            "position",
            None
        )

        if not isinstance(
            position,
            dict
        ):
            return None

        if not all(
            axis in position
            for axis in (
                "x",
                "y",
                "z"
            )
        ):
            return None

        return dict(position)

    @property
    def public_state(self):
        return {
            "default_cat_size": (
                self.default_cat_size
            ),
            "encounter_count": len(
                self.history
            ),
            "history": list(
                self.history
            )
        }
