from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType

from universe.logger import UniverseLogger


class _FrozenList(tuple):
    pass


class _FrozenSet(frozenset):
    pass


def _freeze_law_payload(value):
    if isinstance(value, dict):
        return MappingProxyType({
            key: _freeze_law_payload(item)
            for key, item in value.items()
        })

    if isinstance(value, list):
        return _FrozenList(
            _freeze_law_payload(item)
            for item in value
        )

    if isinstance(value, tuple):
        return tuple(
            _freeze_law_payload(item)
            for item in value
        )

    if isinstance(value, set):
        return _FrozenSet(
            _freeze_law_payload(item)
            for item in value
        )

    if isinstance(value, frozenset):
        return frozenset(
            _freeze_law_payload(item)
            for item in value
        )

    return deepcopy(value)


def _thaw_law_payload(value):
    if isinstance(
        value,
        MappingProxyType,
    ):
        return {
            key: _thaw_law_payload(item)
            for key, item in value.items()
        }

    if isinstance(value, _FrozenList):
        return [
            _thaw_law_payload(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return tuple(
            _thaw_law_payload(item)
            for item in value
        )

    if isinstance(value, _FrozenSet):
        return {
            _thaw_law_payload(item)
            for item in value
        }

    if isinstance(value, frozenset):
        return frozenset(
            _thaw_law_payload(item)
            for item in value
        )

    return deepcopy(value)


@dataclass(slots=True, frozen=True)
class LawNotFoundEvent:

    law: str
    name: str = field(
        default="law_not_found",
        init=False,
    )
    executed: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "law",
            str(self.law),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "law": self.law,
            "executed": self.executed,
        }


@dataclass(slots=True, frozen=True)
class LawTriggeredEvent:

    law: str
    context: object
    result: object
    name: str = field(
        default="law_triggered",
        init=False,
    )
    executed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "law",
            str(self.law),
        )

        object.__setattr__(
            self,
            "context",
            _freeze_law_payload(
                self.context
            ),
        )

        object.__setattr__(
            self,
            "result",
            _freeze_law_payload(
                self.result
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "law": self.law,
            "executed": self.executed,
            "context": _thaw_law_payload(
                self.context
            ),
            "result": _thaw_law_payload(
                self.result
            ),
        }


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
            event = LawNotFoundEvent(
                law=name,
            )

            self.record_trigger(
                event
            )

            return event.to_dict()

        context = dict(context or {})

        result = law.execute(
            context=context
        )

        event = LawTriggeredEvent(
            law=name,
            context=context,
            result=result,
        )

        self.record_trigger(
            event
        )

        UniverseLogger.event(
            f"LAW TRIGGERED: {name}"
        )

        return event.to_dict()

    def record_trigger(
        self,
        event,
    ):
        if not isinstance(
            event,
            (
                LawNotFoundEvent,
                LawTriggeredEvent,
            ),
        ):
            raise TypeError(
                "Law trigger history requires "
                "a law trigger event object."
            )

        self.trigger_history.append(
            event
        )

        return event

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
