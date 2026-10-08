from dataclasses import dataclass, field

from core.entity.components import SpatialVector3


def _require_optional_position(
    value,
    field_name,
):
    if (
        value is not None
        and not isinstance(
            value,
            SpatialVector3,
        )
    ):
        raise TypeError(
            f"{field_name} must be "
            "SpatialVector3 or None."
        )

    return value


@dataclass(slots=True, frozen=True)
class CatScentBoxTransferFailedResult:

    cat: str
    reason: str
    identity: str | None = None
    source_box_id: object = None
    target_box_id: object = None
    source_layer: str | None = None
    target_layer: str | None = None
    arrived_at_box: bool = False

    name: str = field(
        default="cat_scent_box_transfer_failed",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )

    transferred: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatScentBoxFollowingEvent:

    cat: str
    identity: str | None
    source_box_id: object
    target_box_id: object
    route_id: str | None
    destination: SpatialVector3 | None
    position: SpatialVector3 | None = None
    route_result: str | None = None
    executed: bool = True

    name: str = field(
        default="cat_following_scent_to_box",
        init=False,
    )

    arrived_at_box: bool = field(
        default=False,
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    transferred: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        _require_optional_position(
            self.destination,
            "Scent box destination",
        )

        _require_optional_position(
            self.position,
            "Scent box current position",
        )


@dataclass(slots=True, frozen=True)
class CatScentBoxTransferredEvent:

    cat: str
    identity: str | None
    source_box_id: object
    target_box_id: object
    source_layer: str | None
    target_layer: str | None

    name: str = field(
        default="cat_followed_scent_through_box",
        init=False,
    )

    arrived_at_box: bool = field(
        default=True,
        init=False,
    )

    decision_source: str = field(
        default="cat_mind",
        init=False,
    )

    executed: bool = field(
        default=True,
        init=False,
    )

    transferred: bool = field(
        default=True,
        init=False,
    )


CAT_SCENT_BOX_RESULT_TYPES = (
    CatScentBoxTransferFailedResult,
    CatScentBoxFollowingEvent,
    CatScentBoxTransferredEvent,
)
