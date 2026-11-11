"""Safe, data-only HistoryRecord snapshots."""

import json
import math
from copy import deepcopy

from core.actualization.possibility import (
    PossibilityActualizedEvent,
)

_TAG = "__a44_snapshot_type__"


def _encode(value, depth=0):
    if depth > 64:
        raise TypeError("History snapshot is too deeply nested.")

    if value is None or type(value) in (bool, int, str):
        return value

    if type(value) is float:
        if not math.isfinite(value):
            raise TypeError("Non-finite history value.")
        return value

    if type(value) is PossibilityActualizedEvent:
        if type(value.name) is not str:
            raise TypeError("Event name must be a string.")
        return {
            _TAG: "possibility_event",
            "name": value.name,
        }

    if type(value) in (list, tuple):
        return {
            _TAG: (
                "tuple" if type(value) is tuple else "list"
            ),
            "items": [
                _encode(item, depth + 1)
                for item in value
            ],
        }

    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise TypeError(
                "History mapping keys must be strings."
            )

        return {
            _TAG: "dict",
            "items": [
                [key, _encode(item, depth + 1)]
                for key, item in value.items()
            ],
        }

    raise TypeError(
        "Unsupported history snapshot value: "
        + type(value).__qualname__
    )


def _decode(value, depth=0):
    if depth > 64:
        raise ValueError("History snapshot is too deeply nested.")

    if value is None or type(value) in (bool, int, str):
        return value

    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("Non-finite snapshot value.")
        return value

    if (
        type(value) is not dict
        or type(value.get(_TAG)) is not str
    ):
        raise ValueError("Invalid history snapshot encoding.")

    tag = value[_TAG]

    if tag == "possibility_event":
        if (
            set(value) != {_TAG, "name"}
            or type(value["name"]) is not str
        ):
            raise ValueError("Invalid possibility event.")

        return PossibilityActualizedEvent(
            name=value["name"]
        )

    if tag in ("list", "tuple"):
        if (
            set(value) != {_TAG, "items"}
            or type(value["items"]) is not list
        ):
            raise ValueError("Invalid sequence snapshot.")

        items = [
            _decode(item, depth + 1)
            for item in value["items"]
        ]

        return tuple(items) if tag == "tuple" else items

    if tag == "dict":
        if (
            set(value) != {_TAG, "items"}
            or type(value["items"]) is not list
        ):
            raise ValueError("Invalid mapping snapshot.")

        result = {}

        for pair in value["items"]:
            if (
                type(pair) is not list
                or len(pair) != 2
                or type(pair[0]) is not str
                or pair[0] in result
            ):
                raise ValueError(
                    "Invalid or duplicate mapping key."
                )

            result[pair[0]] = _decode(
                pair[1], depth + 1
            )

        return result

    raise ValueError("Unknown history snapshot tag.")


def encode_snapshot(state):
    return json.dumps(
        {
            "format": 1,
            "state": _encode(state),
        },
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def decode_snapshot(payload):
    def reject_constant(value):
        raise ValueError(
            "Invalid numeric constant in snapshot."
        )

    document = json.loads(
        payload,
        parse_constant=reject_constant,
    )

    if (
        type(document) is not dict
        or set(document) != {"format", "state"}
        or type(document["format"]) is not int
        or document["format"] != 1
    ):
        raise ValueError(
            "Unsupported history snapshot format."
        )

    return _decode(document["state"])


class RestoredPotentialBlueprint:
    """An inert blueprint without an executable action."""

    def __init__(self, state):
        if (
            type(state) is not dict
            or type(state.get("name")) is not str
        ):
            raise ValueError(
                "Invalid restored potential blueprint."
            )

        self._state = deepcopy(state)
        self.name = state["name"]

    @property
    def public_state(self):
        return deepcopy(self._state)

    def create_potential(self, cycle_id):
        raise RuntimeError(
            "Restored history action is unbound; "
            "explicit action binding required."
        )


class RestoredHistoryRecord:
    """Read-only historical data view; no executable callbacks."""

    def __init__(self, state):
        required = {
            "cycle_id",
            "branch_id",
            "parent_branch_id",
            "created_by",
            "events",
            "actualized",
            "unrealized",
            "potential_blueprints",
        }

        if type(state) is not dict or set(state) != required:
            raise ValueError(
                "Invalid restored history record fields."
            )

        if (
            type(state["cycle_id"]) is not str
            or not state["cycle_id"]
            or type(state["branch_id"]) is not str
            or not state["branch_id"]
        ):
            raise ValueError(
                "Invalid restored history identity."
            )

        collection_names = (
            "events",
            "actualized",
            "unrealized",
            "potential_blueprints",
        )

        if any(
            type(state[name]) is not list
            for name in collection_names
        ):
            raise ValueError(
                "Invalid restored history collections."
            )

        if any(
            type(item) is not dict
            for item in (
                state["actualized"]
                + state["unrealized"]
            )
        ):
            raise ValueError(
                "Invalid restored potential state."
            )

        self._state = deepcopy(state)
        self.cycle_id = state["cycle_id"]
        self.branch_id = state["branch_id"]
        self.parent_branch_id = state["parent_branch_id"]
        self.created_by = deepcopy(state["created_by"])
        self.events = tuple(deepcopy(state["events"]))
        self.actualized = tuple(
            deepcopy(state["actualized"])
        )
        self.unrealized = tuple(
            deepcopy(state["unrealized"])
        )
        self.potential_blueprints = tuple(
            RestoredPotentialBlueprint(item)
            for item in state["potential_blueprints"]
        )

    @property
    def public_state(self):
        return deepcopy(self._state)
