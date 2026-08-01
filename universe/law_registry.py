from copy import deepcopy

from universe.logger import UniverseLogger


class LawRegistry:

    def __init__(self):
        self.name = "law_registry"
        self.laws = {}
        self.trigger_history = []

        UniverseLogger.boot(
            "LAW REGISTRY CREATED"
        )

    def register(self, name, law):
        name = self._normalize_name(name)

        if name in self.laws:
            return False

        if not self._is_law(law):
            raise TypeError(
                "Registered law must provide "
                "an execute() method."
            )

        self.laws[name] = law

        UniverseLogger.boot(
            f"LAW REGISTERED: {name}"
        )

        return True

    def unregister(self, name):
        name = self._normalize_name(name)

        if name not in self.laws:
            return False

        del self.laws[name]

        UniverseLogger.event(
            f"LAW UNREGISTERED: {name}"
        )

        return True

    def get(self, name):
        name = self._normalize_name(name)

        return self.laws.get(name)

    def has(self, name):
        name = self._normalize_name(name)

        return name in self.laws

    def trigger(
        self,
        name,
        context=None
    ):
        name = self._normalize_name(name)

        law = self.get(name)

        if law is None:
            event = {
                "name": "law_not_found",
                "law": name,
                "executed": False
            }

            self.trigger_history.append(
                event
            )

            return deepcopy(event)

        context = dict(context or {})

        result = law.execute(
            context=context
        )

        event = {
            "name": "law_triggered",
            "law": name,
            "executed": True,
            "context": deepcopy(context),
            "result": deepcopy(result)
        }

        self.trigger_history.append(
            event
        )

        UniverseLogger.event(
            f"LAW TRIGGERED: {name}"
        )

        return deepcopy(event)

    def _normalize_name(self, name):
        if not isinstance(name, str):
            raise TypeError(
                "Law name must be a string."
            )

        normalized = (
            name
            .strip()
            .lower()
        )

        if not normalized:
            raise ValueError(
                "Law name cannot be empty."
            )

        return normalized

    def _is_law(self, law):
        return callable(
            getattr(
                law,
                "execute",
                None
            )
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "law_count": len(
                self.laws
            ),
            "law_names": list(
                self.laws.keys()
            ),
            "trigger_count": len(
                self.trigger_history
            )
        }
