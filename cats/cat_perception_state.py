from dataclasses import dataclass, field
from core.entity.components import SpatialVector3, require_optional_spatial_vector, require_spatial_vector

from .cat_exploration_state import (
    CatExplorationPlan
)
from .cat_olfaction_state import (
    CatOlfactionState
)


@dataclass(slots=True)
class CatPerceptionFailure:
    reason: str
    cat: str | None = None
    name: str = "cat_observation_failed"
    observed: bool = False


@dataclass(slots=True)
class CatBarObservation:
    known: bool
    visible: bool
    distance: float | None


@dataclass(slots=True)
class CatCronenbergObservation:
    id: str
    name: str
    size: float
    distance: float
    position: SpatialVector3
    size_ratio: float | None = None


    def __post_init__(self):
        self.position = require_spatial_vector(self.position, field_name="cronenberg observation position")


@dataclass(slots=True)
class CatNearbyCatObservation:
    name: str
    distance: float
    position: SpatialVector3


    def __post_init__(self):
        self.position = require_spatial_vector(self.position, field_name="nearby cat observation position")


@dataclass(slots=True)
class CatVisibleBoxObservation:
    id: str
    explored: bool
    occupied: bool
    occupancy_state: str
    occupant_identity_visible: bool
    distance: float
    position: SpatialVector3

    state: object | None = None
    collapsed: bool | None = None
    recognized_as_quantum_box: bool | None = None
    paired: bool | None = None
    counterpart_known: bool | None = None


    def __post_init__(self):
        self.position = require_spatial_vector(self.position, field_name="visible box observation position")


@dataclass(slots=True)
class CatScentTransferCandidate:
    box_id: object = None
    counterpart_box_id: object = None

    identity: str | None = None
    similarity: float = 0.0

    source_layer: str | None = None
    target_layer: str | None = None

    box_position: SpatialVector3 | None = None
    counterpart_position: SpatialVector3 | None = None


    def __post_init__(self):
        self.box_position = require_optional_spatial_vector(self.box_position, field_name="scent transfer box position")
        self.counterpart_position = require_optional_spatial_vector(self.counterpart_position, field_name="scent transfer counterpart position")


@dataclass(slots=True)
class CatPerceptionState:
    cat: str | None = None
    position: SpatialVector3 | None = None
    vision_radius: float = 0.0

    bar_known: bool = False
    bar_visible: bool = False
    bar_distance: float | None = None

    nearby_cats: list = field(
        default_factory=list
    )
    nearby_cat_details: list = field(
        default_factory=list
    )

    visible_cronenbergs: list = field(
        default_factory=list
    )
    visible_cronenberg_details: list = field(
        default_factory=list
    )
    huntable_cronenbergs: list = field(
        default_factory=list
    )
    huntable_cronenberg_details: list = field(
        default_factory=list
    )
    cronenberg_danger: float = 0.0

    visible_boxes: list = field(
        default_factory=list
    )
    visible_box_details: list = field(
        default_factory=list
    )
    unexplored_boxes: list = field(
        default_factory=list
    )
    occupied_transfer_boxes: list = field(
        default_factory=list
    )
    occupied_transfer_box_details: list = field(
        default_factory=list
    )
    interesting_unknown: bool = False

    quantum_counterpart_observation: object = None
    current_layer: str | None = None

    available_cat_energy: float = 0.0
    can_create_exploration_pair: bool = False
    exploration_pair_energy_cost: float = 0.0
    exploration_destination_layer: str | None = None
    exploration_destination_position: SpatialVector3 | None = None
    exploration_plan: CatExplorationPlan = field(
        default_factory=CatExplorationPlan
    )

    shareable_legend_count: int = 0

    olfaction: CatOlfactionState = field(
        default_factory=CatOlfactionState
    )
    scent_memories: list = field(
        default_factory=list
    )
    scent_transfer_candidates: list[CatScentTransferCandidate] = field(
        default_factory=list
    )
    smelled_entities: list = field(
        default_factory=list
    )
    ozone_detected: bool = False
    cronenberg_scent_recognized: bool = False
    smelled_cronenbergs: list = field(
        default_factory=list
    )

    observed: bool = True

    def __post_init__(self):
        self.position = require_optional_spatial_vector(self.position, field_name="cat perception position")
        self.exploration_destination_position = require_optional_spatial_vector(self.exploration_destination_position, field_name="cat exploration destination position")
