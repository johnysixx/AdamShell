"""A44 canonical supported Cronenberg state checkpoint.

Captures a deterministic, detached, versioned entity-state
projection from an already existing live canonical publication.

Unknown runtime attributes and unsupported object components
fail closed instead of being silently dropped.

This checkpoint is NOT:
- an independently authenticated checkpoint;
- an atomic freeze of a concurrently mutable Universe;
- a complete Universe registry/event-history snapshot;
- a durable or rollback-protected transaction;
- authority to restore or republish a Cronenberg;
- a cross-process exactly-once publication mechanism.

The SHA-256 digest checks local data consistency, not trust.
"""

import hashlib
import json
import math

from dataclasses import dataclass, field, fields

from core.entities.ability_set import AbilitySet
from core.entity.cronenberg import Cronenberg
from core.entity.cronenberg_system.consumption import (
    CronenbergConsumptionRecord,
)
from core.entity.cronenberg_system.growth import CronenbergGrowth
from core.entity.cronenberg_system.hunger import CronenbergHunger
from core.entity.cronenberg_system.metabolism import (
    CronenbergMetabolism,
)
from core.entity.cronenberg_system.origin import CronenbergOrigin
from core.entity.cronenberg_system.quantum_links import (
    CronenbergQuantumLink,
    CronenbergQuantumLinkHistoryEvent,
    CronenbergQuantumLinks,
)
from core.entity.cronenberg_system.quantum_state import (
    CronenbergQuantumState,
)
from core.entity.cronenberg_system.traits import (
    CronenbergTraitInfluence,
    CronenbergTraits,
    CronenbergTraitValues,
)
from core.entity.cronenberg_system.travel import CronenbergTravel
from core.entity.components.spatial import (
    SpatialComponent,
    SpatialVector3,
)
from core.existence.history_receipt_trust_canonical_recovery import (
    CanonicalSecurityPublicationEvidence,
)
from core.existence.history_receipt_trust_incident_outbox import (
    _require_cronenberg_id,
    _require_incident_id,
    _require_operation,
)
from core.existence.history_receipt_trust_publication_witness import (
    _require_digest,
    _require_universe_id,
)
from universe.aroma_composition import (
    AromaComponent,
    AromaComposition,
)
from universe.aroma_profile import (
    AromaProfile,
    AromaSurfaceResidue,
)
from core.entity.cronenberg_system.chemical_marker import (
    CronenbergChemicalMarker,
)
from universe.universe import Universe


_VERSION = 1
_MAX_BYTES = 1024 * 1024
_MAX_COLLECTION = 4096

_NUMBER = object()
_INTEGER = object()
_TEXT = object()
_JSON = object()
_NUMBER_MAP = object()

_VECTOR = {
    "x": _NUMBER,
    "y": _NUMBER,
    "z": _NUMBER,
}

_LINK = {
    "target_id": _TEXT,
    "link_type": _TEXT,
    "strength": _NUMBER,
    "created_tick": ("optional", _INTEGER),
    "metadata": _JSON,
}

_SCALAR_SCHEMA = {
    "id": _TEXT,
    "name": _TEXT,
    "type": "cronenberg",
    "age": _INTEGER,
    "energy": _NUMBER,
    "state": _TEXT,
    "active": bool,
    "evolution_threshold": _NUMBER,
    "evolved": bool,
    "depth": _INTEGER,
    "birth_allowed": bool,
    "location": _TEXT,
    "size": _NUMBER,
    "juice_value": _NUMBER,
}

_TRAIT_NAMES = (
    "acidity",
    "sweetness",
    "bitterness",
    "viscosity",
    "stability",
    "dark_energy_affinity",
    "growth_efficiency",
    "cat_scent",
    "quantum_coherence",
)

_ORIGIN_BASE = {
    "layer": _TEXT,
    "source_component": _TEXT,
    "source_operation": _TEXT,
    "quantum_tick": ("optional", _INTEGER),
    "error_type": _TEXT,
    "error_message": _TEXT,
}

_ORIGIN_OPTIONAL = {
    "recombined_from": [_TEXT],
    "merged_from": [_TEXT],
    "former_pair_id": _TEXT,
    "consumption_location": _TEXT,
    "merge_location": _TEXT,
    "released_energy": _NUMBER,
    "dark_energy_created": _NUMBER,
    "counterpart_of": _TEXT,
    "pair_id": _TEXT,
    "spin_relation": _TEXT,
    "manifested_in": _TEXT,
}

_COMPONENT_SCHEMA = {
    "abilities": {
        "owner": _TEXT,
        "ability_count": _INTEGER,
        "abilities": [_TEXT],
    },
    "spatial": {
        "name": "spatial_component",
        "type": "entity_component",
        "position": ("optional", _VECTOR),
        "has_position": bool,
        "layer": ("optional", _TEXT),
        "zone": ("optional", _TEXT),
        "velocity": _VECTOR,
        "rotation": _VECTOR,
    },
    "aroma": {
        "identity": _TEXT,
        "base_components": _NUMBER_MAP,
        "base_intensity": _NUMBER,
        "surface_residues": [{
            "source": _TEXT,
            "components": _NUMBER_MAP,
            "intensity": _NUMBER,
            "decay_rate": _NUMBER,
            "age_ticks": _INTEGER,
        }],
        "type": "chemical_aroma_profile",
    },
    "aroma_chemical_marker": {
        "molecule": _TEXT,
        "formula": _TEXT,
    },
    "metabolism": {
        "dark_energy_output_rate": _NUMBER,
        "daily_energy_received": _NUMBER,
        "total_energy_received": _NUMBER,
        "pending_dark_energy": _NUMBER,
        "total_dark_energy_produced": _NUMBER,
    },
    "hunger": {
        "starvation_threshold_days": _INTEGER,
        "minimum_digestion_days": _INTEGER,
        "maximum_digestion_days": _INTEGER,
        "hungry_days": _INTEGER,
        "satiety_days_remaining": _INTEGER,
        "last_consumed_mass": _NUMBER,
        "last_digestion_days": _INTEGER,
        "is_satiated": bool,
        "is_hungry": bool,
        "can_hunt": bool,
    },
    "travel": {
        "layer_growth": _NUMBER,
        "energy_cost_rate": _NUMBER,
        "minimum_energy_cost": _NUMBER,
        "dark_energy_output_rate": _NUMBER,
        "layers_crossed": _INTEGER,
        "travel_steps": _INTEGER,
        "total_energy_consumed": _NUMBER,
        "total_dark_energy_produced": _NUMBER,
    },
    "growth": {
        "fed_growth": _NUMBER,
        "layer_growth": _NUMBER,
        "starvation_mass_loss": _NUMBER,
        "starvation_loss_starts_day": _INTEGER,
        "minimum_size": _NUMBER,
        "total_growth": _NUMBER,
        "total_mass_consumed": _NUMBER,
        "total_mass_lost": _NUMBER,
    },
    "consumed_cronenbergs": [{
        "name": _TEXT,
        "mass": _NUMBER,
        "energy": _NUMBER,
        "digestion_days": _INTEGER,
    }],
    "traits": {
        "values": {
            name: _NUMBER
            for name in _TRAIT_NAMES
        },
        "birth_influences": [{
            "trait": _TEXT,
            "amount": _NUMBER,
            "reason": _TEXT,
        }],
        "source_component": _TEXT,
        "source_operation": _TEXT,
        "error_type": _TEXT,
        "quantum_tick": ("optional", _INTEGER),
    },
    "quantum_link_system": {
        "owner_id": _TEXT,
        "link_count": _INTEGER,
        "links": [_LINK],
        "history": [{
            "event": "link_created",
            "link": _LINK,
        }],
    },
    "quantum_state": {
        "spin": _NUMBER,
        "entangled": bool,
        "pair_id": ("optional", _TEXT),
        "counterpart_id": ("optional", _TEXT),
        "counterpart_potential": bool,
        "counterpart_manifested": bool,
    },
    "origin": None,
    "profile": None,
    "bar_policy": None,
}

_STATE_SCHEMA = {
    **_SCALAR_SCHEMA,
    **_COMPONENT_SCHEMA,
}

_BODY_KEYS = frozenset({
    "schema_version",
    "universe_id",
    "incident_id",
    "source_operation",
    "cronenberg_id",
    "projection_sha256",
    "entity_state",
})

_PAYLOAD_KEYS = _BODY_KEYS | {"checkpoint_sha256"}


def _reject(message):
    raise ValueError(
        "Invalid canonical Cronenberg checkpoint: "
        + message
    )


def _finite_number(value, where):
    if type(value) not in (int, float):
        _reject(where)

    try:
        finite = math.isfinite(value)
    except (OverflowError, ValueError, TypeError):
        finite = False

    if not finite:
        _reject(where)


def _json_value(value, where, depth=0):
    """Strictly bounded JSON-only recursive data."""

    if depth > 32:
        _reject(where)

    if value is None or type(value) in (str, bool):
        return

    if type(value) in (int, float):
        _finite_number(value, where)
        return

    if type(value) is list:
        if len(value) > _MAX_COLLECTION:
            _reject(where)

        for entry in value:
            _json_value(
                entry,
                where,
                depth + 1,
            )
        return

    if type(value) is dict:
        if len(value) > _MAX_COLLECTION:
            _reject(where)

        for key, entry in value.items():
            if type(key) is not str:
                _reject(where)

            _json_value(
                entry,
                where,
                depth + 1,
            )
        return

    _reject(where)


def _check(value, specification, where):
    if specification is _NUMBER:
        _finite_number(value, where)
        return

    if specification is _INTEGER:
        if type(value) is not int or value < 0:
            _reject(where)
        return

    if specification is _TEXT:
        if type(value) is not str or not value:
            _reject(where)
        return

    if specification is _JSON:
        _json_value(value, where)
        return

    if specification is _NUMBER_MAP:
        if type(value) is not dict:
            _reject(where)

        if len(value) > _MAX_COLLECTION:
            _reject(where)

        for key, entry in value.items():
            _check(key, _TEXT, where)
            _check(entry, _NUMBER, where)
        return

    if (
        type(specification) is tuple
        and len(specification) == 2
        and specification[0] == "optional"
    ):
        if value is not None:
            _check(
                value,
                specification[1],
                where,
            )
        return

    if type(specification) is dict:
        if (
            type(value) is not dict
            or set(value) != set(specification)
        ):
            _reject(where)

        for key, sub_schema in specification.items():
            _check(
                value[key],
                sub_schema,
                where + "." + key,
            )
        return

    if type(specification) is list:
        if (
            type(value) is not list
            or len(specification) != 1
            or len(value) > _MAX_COLLECTION
        ):
            _reject(where)

        for index, entry in enumerate(value):
            _check(
                entry,
                specification[0],
                f"{where}[{index}]",
            )
        return

    if specification is bool:
        if type(value) is not bool:
            _reject(where)
        return

    if specification is None:
        if value is not None:
            _reject(where)
        return

    if type(specification) is str:
        if (
            type(value) is not str
            or value != specification
        ):
            _reject(where)
        return

    _reject(where)


def _validate_origin(value):
    if type(value) is not dict:
        _reject("origin")

    expected = dict(_ORIGIN_BASE)

    for key in value:
        if key not in _ORIGIN_BASE:
            if key not in _ORIGIN_OPTIONAL:
                _reject("origin unknown property")

            expected[key] = _ORIGIN_OPTIONAL[key]

    _check(
        value,
        expected,
        "origin",
    )

    if "recombined_from" in value:
        for required in (
            "former_pair_id",
            "consumption_location",
            "released_energy",
            "dark_energy_created",
        ):
            if required not in value:
                _reject("incomplete recombination origin")

    if "merged_from" in value:
        for required in (
            "former_pair_id",
            "merge_location",
        ):
            if required not in value:
                _reject("incomplete merge origin")

    if "counterpart_of" in value:
        for required in (
            "pair_id",
            "spin_relation",
            "manifested_in",
        ):
            if required not in value:
                _reject("incomplete counterpart origin")

    if (
        "former_pair_id" in value
        and "recombined_from" not in value
        and "merged_from" not in value
    ):
        _reject("orphan former pair origin")

    for marker, required in (
        ("consumption_location", "recombined_from"),
        ("released_energy", "recombined_from"),
        ("dark_energy_created", "recombined_from"),
        ("merge_location", "merged_from"),
        ("pair_id", "counterpart_of"),
        ("spin_relation", "counterpart_of"),
        ("manifested_in", "counterpart_of"),
    ):
        if marker in value and required not in value:
            _reject("orphan origin property")


def _validate_state(state, *, cronenberg_id, operation):
    if (
        type(state) is not dict
        or set(state) != set(_STATE_SCHEMA)
    ):
        _reject("entity-state inventory")

    for name, specification in _STATE_SCHEMA.items():
        if name == "origin":
            _validate_origin(
                state[name]
            )
        else:
            _check(
                state[name],
                specification,
                "entity_state." + name,
            )

    _require_cronenberg_id(
        state["id"]
    )

    if (
        state["id"] != cronenberg_id
        or state["name"] != cronenberg_id
    ):
        _reject("entity identity")

    if state["size"] <= 0:
        _reject("entity size")

    if state["juice_value"] != state["size"]:
        _reject("entity juice/size consistency")

    abilities = state["abilities"]

    if (
        abilities["owner"] != cronenberg_id
        or abilities["ability_count"] != 0
        or abilities["abilities"] != []
    ):
        _reject("unsupported abilities")

    spatial = state["spatial"]

    if spatial["has_position"] is not (
        spatial["position"] is not None
    ):
        _reject("spatial position consistency")

    hunger = state["hunger"]

    satiated = hunger["satiety_days_remaining"] > 0
    hungry = not satiated and hunger["hungry_days"] > 0
    can_hunt = (
        not satiated
        and hunger["hungry_days"]
        >= hunger["starvation_threshold_days"]
    )

    if (
        hunger["is_satiated"] is not satiated
        or hunger["is_hungry"] is not hungry
        or hunger["can_hunt"] is not can_hunt
    ):
        _reject("hunger derived-state consistency")

    links = state["quantum_link_system"]

    if (
        links["owner_id"] != cronenberg_id
        or links["link_count"] != len(links["links"])
    ):
        _reject("quantum links consistency")

    if (
        state["traits"]["source_operation"] != operation
        or state["origin"]["source_operation"] != operation
    ):
        _reject("Cronenberg source operation")

    if (
        state["traits"]["quantum_tick"]
        != state["origin"]["quantum_tick"]
    ):
        _reject("Cronenberg origin quantum tick")

    # Cross-check origin provenance against trait provenance.
    # A locally rehashed document cannot change just one side.
    origin_state = state["origin"]
    trait_state = state["traits"]

    if (
        origin_state["source_component"]
        != trait_state["source_component"]
    ):
        _reject("Cronenberg source component mismatch")

    if (
        origin_state["error_type"]
        != trait_state["error_type"]
    ):
        _reject("Cronenberg error type mismatch")

    # Trait influence names must belong to the supported
    # Cronenberg trait vocabulary.
    for influence in trait_state["birth_influences"]:
        if influence["trait"] not in _TRAIT_NAMES:
            _reject("unknown Cronenberg trait influence")

    # Link identity follows the CronenbergQuantumLinks
    # implementation: (target_id, link_type) must be unique.
    seen_link_identities = set()

    for link in links["links"]:
        identity = (
            link["target_id"],
            link["link_type"],
        )

        if identity in seen_link_identities:
            _reject("duplicate Cronenberg quantum link")

        seen_link_identities.add(
            identity
        )

    # A manifest counterpart requires an actual pair link.
    # Do not infer restoration authority from these fields.
    quantum = state["quantum_state"]

    if quantum["counterpart_manifested"] and (
        not quantum["entangled"]
        or quantum["pair_id"] is None
        or quantum["counterpart_id"] is None
    ):
        _reject("manifested counterpart lacks pair state")

    if state["aroma"]["base_intensity"] < 0:
        _reject("negative aroma intensity")


def _canonical_bytes(value):
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")

    except (
        TypeError,
        ValueError,
        OverflowError,
        RecursionError,
    ) as exc:
        raise ValueError(
            "Checkpoint is not canonically serializable."
        ) from exc

    if len(encoded) > _MAX_BYTES:
        _reject("checkpoint capacity")

    return encoded


def _validate_body(body):
    if (
        type(body) is not dict
        or set(body) != _BODY_KEYS
    ):
        _reject("checkpoint top-level schema")

    if (
        type(body["schema_version"]) is not int
        or body["schema_version"] != _VERSION
    ):
        _reject("checkpoint schema version")

    _require_universe_id(
        body["universe_id"]
    )

    _require_incident_id(
        body["incident_id"]
    )

    _require_operation(
        body["source_operation"]
    )

    _require_cronenberg_id(
        body["cronenberg_id"]
    )

    _require_digest(
        body["projection_sha256"]
    )

    _validate_state(
        body["entity_state"],
        cronenberg_id=body["cronenberg_id"],
        operation=body["source_operation"],
    )

    return _canonical_bytes(body)


def _raw_attributes(value, expected, where):
    try:
        actual = set(vars(value))
    except TypeError as exc:
        raise ValueError(
            "Unsupported checkpoint component: " + where
        ) from exc

    if actual != set(expected):
        _reject("component inventory: " + where)


_RAW_COMPONENTS = {
    "metabolism": (
        CronenbergMetabolism,
        {
            "dark_energy_output_rate",
            "daily_energy_received",
            "total_energy_received",
            "pending_dark_energy",
            "total_dark_energy_produced",
        },
    ),
    "hunger": (
        CronenbergHunger,
        {
            "starvation_threshold_days",
            "minimum_digestion_days",
            "maximum_digestion_days",
            "hungry_days",
            "satiety_days_remaining",
            "last_consumed_mass",
            "last_digestion_days",
        },
    ),
    "travel": (
        CronenbergTravel,
        {
            "layer_growth",
            "energy_cost_rate",
            "minimum_energy_cost",
            "dark_energy_output_rate",
            "layers_crossed",
            "travel_steps",
            "total_energy_consumed",
            "total_dark_energy_produced",
        },
    ),
    "growth": (
        CronenbergGrowth,
        {
            "fed_growth",
            "layer_growth",
            "starvation_mass_loss",
            "starvation_loss_starts_day",
            "minimum_size",
            "total_growth",
            "total_mass_consumed",
            "total_mass_lost",
        },
    ),
    "traits": (
        CronenbergTraits,
        {
            "source_component",
            "source_operation",
            "error_type",
            "quantum_tick",
            "values",
            "birth_influences",
        },
    ),
    "quantum_link_system": (
        CronenbergQuantumLinks,
        {
            "owner_id",
            "links",
            "history",
        },
    ),
    "abilities": (
        AbilitySet,
        {
            "owner",
            "_abilities",
        },
    ),
    "spatial": (
        SpatialComponent,
        {
            "name",
            "type",
            "_position",
            "layer",
            "zone",
            "velocity",
            "rotation",
        },
    ),
}


def _validate_live_components(entity):
    for name, (expected_type, raw_names) in (
        _RAW_COMPONENTS.items()
    ):
        component = getattr(entity, name)

        if type(component) is not expected_type:
            _reject("component type: " + name)

        _raw_attributes(
            component,
            raw_names,
            name,
        )

    if (
        entity.abilities.owner is not entity
        or type(entity.abilities._abilities) is not dict
        or entity.abilities._abilities
    ):
        _reject("unsupported live ability objects")

    if type(entity.spatial.velocity) is not SpatialVector3:
        _reject("spatial velocity type")

    if type(entity.spatial.rotation) is not SpatialVector3:
        _reject("spatial rotation type")

    if (
        entity.spatial.position is not None
        and type(entity.spatial.position)
        is not SpatialVector3
    ):
        _reject("spatial position type")

    if type(entity.aroma) is not AromaProfile:
        _reject("aroma profile type")

    _raw_attributes(
        entity.aroma,
        {
            "identity",
            "base_components",
            "base_intensity",
            "surface_residues",
        },
        "aroma",
    )

    def require_composition(composition):
        if type(composition) is not AromaComposition:
            _reject("aroma composition type")

        if type(composition.entries) is not tuple:
            _reject("aroma composition entries")

        for entry in composition.entries:
            if type(entry) is not AromaComponent:
                _reject("aroma component type")

    require_composition(
        entity.aroma.base_components
    )

    if type(entity.aroma.surface_residues) is not list:
        _reject("aroma residues type")

    for residue in entity.aroma.surface_residues:
        if type(residue) is not AromaSurfaceResidue:
            _reject("aroma residue element type")

        _raw_attributes(
            residue,
            {
                "source",
                "components",
                "intensity",
                "decay_rate",
                "age_ticks",
            },
            "aroma residue",
        )

        require_composition(
            residue.components
        )

    if (
        type(entity.aroma_chemical_marker)
        is not CronenbergChemicalMarker
    ):
        _reject("aroma chemical marker type")

    if type(entity.traits.values) is not CronenbergTraitValues:
        _reject("trait value type")

    if (
        {
            field.name
            for field in fields(entity.traits.values)
        }
        != set(_TRAIT_NAMES)
    ):
        _reject("trait value inventory")

    if type(entity.traits.birth_influences) is not list:
        _reject("trait influence collection")

    for influence in entity.traits.birth_influences:
        if type(influence) is not CronenbergTraitInfluence:
            _reject("trait influence type")

    if type(entity.quantum_state) is not CronenbergQuantumState:
        _reject("quantum state type")

    if type(entity.quantum_link_system.links) is not list:
        _reject("quantum links collection")

    for link in entity.quantum_link_system.links:
        if type(link) is not CronenbergQuantumLink:
            _reject("quantum link type")

    if type(entity.quantum_link_system.history) is not list:
        _reject("quantum link history")

    for event in entity.quantum_link_system.history:
        if type(event) is not CronenbergQuantumLinkHistoryEvent:
            _reject("quantum link history event")

    if type(entity.origin) is not CronenbergOrigin:
        _reject("Cronenberg origin type")

    if type(entity.consumed_cronenbergs) is not list:
        _reject("consumption collection")

    for record in entity.consumed_cronenbergs:
        if type(record) is not CronenbergConsumptionRecord:
            _reject("consumption record type")

    if entity.profile is not None:
        _reject("unsupported live profile")

    if entity.bar_policy is not None:
        _reject("unsupported live bar policy")


def _snapshot_entity(entity):
    if type(entity) is not Cronenberg:
        _reject("canonical Cronenberg type")

    raw_names = set(vars(entity))

    expected = set(_STATE_SCHEMA)

    if raw_names - {"universe"} != expected:
        _reject("unknown or missing runtime fields")

    _validate_live_components(
        entity
    )

    state = {
        name: getattr(entity, name)
        for name in _SCALAR_SCHEMA
    }

    for name in _RAW_COMPONENTS:
        state[name] = getattr(
            entity,
            name,
        ).public_state

    state["aroma"] = entity.aroma.to_dict()

    state["aroma_chemical_marker"] = {
        "molecule": entity.aroma_chemical_marker.molecule,
        "formula": entity.aroma_chemical_marker.formula,
    }

    state["consumed_cronenbergs"] = [
        record.to_dict()
        for record in entity.consumed_cronenbergs
    ]

    state["quantum_state"] = (
        entity.quantum_state.to_dict()
    )

    state["origin"] = entity.origin.to_dict()

    state["profile"] = None
    state["bar_policy"] = None

    _validate_state(
        state,
        cronenberg_id=entity.id,
        operation=entity.origin.source_operation,
    )

    # Serialization makes a detached primitive snapshot.
    return json.loads(
        _canonical_bytes(state)
    )


@dataclass(frozen=True, slots=True)
class CanonicalCronenbergStateCheckpoint:
    """Detached supported entity-state snapshot.

    Not a checkpoint authority, and not a restoration API.
    """

    schema_version: int
    universe_id: str
    incident_id: str
    source_operation: str
    cronenberg_id: str
    projection_sha256: str

    _canonical_body: str = field(
        repr=False,
    )

    checkpoint_sha256: str

    is_authoritative: bool = field(
        default=False,
        init=False,
    )

    is_restorable: bool = field(
        default=False,
        init=False,
    )

    can_republish: bool = field(
        default=False,
        init=False,
    )

    @classmethod
    def _from_body(cls, body):
        serialized = _validate_body(
            body
        )

        return cls(
            schema_version=body["schema_version"],
            universe_id=body["universe_id"],
            incident_id=body["incident_id"],
            source_operation=body["source_operation"],
            cronenberg_id=body["cronenberg_id"],
            projection_sha256=body["projection_sha256"],
            _canonical_body=serialized.decode("utf-8"),
            checkpoint_sha256=hashlib.sha256(
                serialized
            ).hexdigest(),
        )

    @classmethod
    def capture(
        cls,
        *,
        universe,
        incident_id,
        source_operation,
    ):
        """Capture only an existing live canonical publication."""

        if type(universe) is not Universe:
            _reject("live Universe type")

        evidence = (
            CanonicalSecurityPublicationEvidence.capture(
                universe=universe,
                incident_id=incident_id,
                source_operation=source_operation,
            )
        )

        if evidence.verify_live(universe) is not True:
            _reject("live canonical publication")

        matches = [
            entity
            for entity in universe.cronenbergs
            if getattr(entity, "id", None)
            == evidence.cronenberg_id
        ]

        if len(matches) != 1:
            _reject("unique Cronenberg identity")

        entity = matches[0]

        state = _snapshot_entity(
            entity
        )

        body = {
            "schema_version": _VERSION,
            "universe_id": evidence.universe_id,
            "incident_id": evidence.incident_id,
            "source_operation": evidence.source_operation,
            "cronenberg_id": evidence.cronenberg_id,
            "projection_sha256": evidence.projection_sha256,
            "entity_state": state,
        }

        return cls._from_body(
            body
        )

    @classmethod
    def parse_untrusted(cls, payload):
        """Validate consistency, not authenticity."""

        if (
            type(payload) is not dict
            or set(payload) != _PAYLOAD_KEYS
        ):
            _reject("serialized checkpoint schema")

        claimed_digest = _require_digest(
            payload["checkpoint_sha256"]
        )

        body = {
            key: value
            for key, value in payload.items()
            if key != "checkpoint_sha256"
        }

        canonical = _validate_body(
            body
        )

        expected_digest = hashlib.sha256(
            canonical
        ).hexdigest()

        if claimed_digest != expected_digest:
            _reject("checkpoint digest mismatch")

        return cls._from_body(
            body
        )

    def to_dict(self):
        """Detached serialization boundary."""

        body = json.loads(
            self._canonical_body
        )

        body["checkpoint_sha256"] = (
            self.checkpoint_sha256
        )

        return body

    def verify_live(self, universe):
        """Compare full supported entity state with live state.

        No Universe object, event or registry is modified.
        """

        self.parse_untrusted(
            self.to_dict()
        )

        current = type(self).capture(
            universe=universe,
            incident_id=self.incident_id,
            source_operation=self.source_operation,
        )

        if current.to_dict() != self.to_dict():
            _reject("live checkpoint state mismatch")

        return True
