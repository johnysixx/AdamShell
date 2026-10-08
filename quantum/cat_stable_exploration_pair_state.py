from dataclasses import dataclass, field

from core.entity.components import (
    SpatialVector3,
    require_spatial_vector,
)


@dataclass(slots=True)
class CatStableExplorationPairState:
    pair_id: str
    creator_cat: str
    anchor_box_id: object
    remote_box_id: object
    anchor_layer: str
    remote_layer: str
    exploration_destination_position: SpatialVector3
    creation_energy_j: float
    remaining_energy_j: float
    created_tick: int

    stable: bool = True
    active: bool = True
    creator_departed: bool = False
    creator_returned: bool = False
    currently_in_use: bool = False
    current_user: str | None = None
    use_count: int = 0
    used_by: list[str] = field(
        default_factory=list
    )
    dissolved: bool = False
    dissolved_by_return_of: str | None = None

    pair_kind: str = field(
        default="cat_created_exploration_pair",
        init=False,
    )

    def __post_init__(self):
        self.pair_id = str(
            self.pair_id
        )

        self.creator_cat = str(
            self.creator_cat
        )

        self.anchor_layer = str(
            self.anchor_layer
        )

        self.remote_layer = str(
            self.remote_layer
        )

        self.exploration_destination_position = (
            require_spatial_vector(
                self.exploration_destination_position,
                field_name=(
                    "stable exploration pair "
                    "destination position"
                ),
            )
        )

        self.creation_energy_j = float(
            self.creation_energy_j
        )

        self.remaining_energy_j = float(
            self.remaining_energy_j
        )

        self.created_tick = int(
            self.created_tick
        )

        self.use_count = int(
            self.use_count
        )

        self.used_by = list(
            self.used_by
        )

    @property
    def available_to_other_cats(self):
        return (
            self.active
            and self.stable
        )

    @property
    def box_ids(self):
        return frozenset(
            (
                self.anchor_box_id,
                self.remote_box_id,
            )
        )

    def matches_boxes(
        self,
        source_box_id,
        target_box_id,
    ):
        return (
            self.active
            and self.box_ids
            == frozenset(
                (
                    source_box_id,
                    target_box_id,
                )
            )
        )

    def begin_use(
        self,
        cat_name,
    ):
        cat_name = str(
            cat_name
        )

        self.currently_in_use = True
        self.current_user = cat_name
        self.use_count += 1

        if cat_name not in self.used_by:
            self.used_by.append(
                cat_name
            )

    def finish_use(self):
        self.currently_in_use = False
        self.current_user = None

    def register_creator_transfer(
        self,
        cat_name,
        source_box_id,
        target_box_id,
    ):
        if (
            cat_name
            != self.creator_cat
        ):
            return False

        leaving_anchor = (
            source_box_id
            == self.anchor_box_id
        )

        returning_to_anchor = (
            target_box_id
            == self.anchor_box_id
        )

        if (
            leaving_anchor
            and not self.creator_departed
        ):
            self.creator_departed = True
            return False

        if (
            self.creator_departed
            and returning_to_anchor
        ):
            self.creator_returned = True
            return True

        return False

    def dissolve(
        self,
        returning_cat,
    ):
        self.active = False
        self.stable = False
        self.dissolved = True
        self.remaining_energy_j = 0.0
        self.dissolved_by_return_of = str(
            returning_cat
        )
