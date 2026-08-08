import math
from copy import deepcopy

from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J
)
from .cat_exploration_planner import (
    CatExplorationPlanner
)


class CatPerception:

    DEFAULT_VISION_RADIUS = 8.0
    NEARBY_CAT_RADIUS = 4.0

    HUNTABLE_SIZE_RATIO = 1.20

    def __init__(
        self,
        cats_layer
    ):
        self.cats_layer = cats_layer
        self.universe = cats_layer.universe
        self.history = []

    def observe(
        self,
        cat,
        vision_radius=None
    ):
        if not isinstance(
            cat,
            dict
        ):
            return {
                "name": "cat_observation_failed",
                "reason": "invalid_cat",
                "observed": False
            }

        if cat.get("type") != "cat":
            return {
                "name": "cat_observation_failed",
                "cat": cat.get("name"),
                "reason": "entity_is_not_cat",
                "observed": False
            }

        position = cat.get(
            "position"
        )

        if position is None:
            return {
                "name": "cat_observation_failed",
                "cat": cat.get("name"),
                "reason": "cat_has_no_position",
                "observed": False
            }

        radius = float(
            vision_radius
            if vision_radius is not None
            else self.DEFAULT_VISION_RADIUS
        )

        nearby_cats = (
            self._observe_nearby_cats(
                cat=cat,
                position=position,
                radius=min(
                    radius,
                    self.NEARBY_CAT_RADIUS
                )
            )
        )

        visible_cronenbergs = (
            self._observe_cronenbergs(
                position=position,
                radius=radius
            )
        )

        huntable_cronenbergs = (
            self._huntable_cronenbergs(
                cat=cat,
                cronenbergs=visible_cronenbergs
            )
        )

        visible_boxes = (
            self._observe_quantum_boxes(
                cat=cat,
                position=position,
                radius=radius
            )
        )

        unexplored_boxes = [
            item
            for item in visible_boxes
            if (
                not item.get(
                    "occupied",
                    False
                )
                and not self._box_was_explored(
                    cat=cat,
                    box_id=item["id"]
                )
            )
        ]

        occupied_transfer_boxes = [
            item
            for item in visible_boxes
            if item.get(
                "occupied",
                False
            )
        ]

        bar_observation = (
            self._observe_bar(
                cat=cat,
                position=position,
                radius=radius
            )
        )

        danger = (
            self._cronenberg_danger(
                cat=cat,
                cronenbergs=visible_cronenbergs
            )
        )

        current_layer = cat.get(
            "current_layer",
            "quantum_layer"
        )

        exploration_plan = (
            CatExplorationPlanner
            .choose_destination(
                cat=cat,
                universe=self.universe
            )
        )

        exploration_destination_layer = (
            exploration_plan.get(
                "layer"
            )
        )

        exploration_destination_position = (
            exploration_plan.get(
                "position"
            )
        )

        exploration_pair_energy_cost = (
            QUANTUM_BOX_ENERGY_COST_J
            * 2.0
        )

        available_cat_energy = float(
            cat.get(
                "idea_energy",
                0.0
            )
        )

        can_create_exploration_pair = bool(
            not unexplored_boxes
            and available_cat_energy
            >= exploration_pair_energy_cost
            and exploration_plan.get(
                "selected",
                False
            )
            and exploration_destination_layer
            != current_layer
        )

        active_cat_legends = [
            legend
            for legend in getattr(
                self.universe,
                "cat_legends",
                []
            )
            if legend.get(
                "active",
                True
            )
        ]

        shareable_legend_count = len(
            active_cat_legends
        )

        observations = {
            "cat": cat.get("name"),
            "position": deepcopy(
                position
            ),
            "vision_radius": radius,

            "bar_known": bar_observation[
                "known"
            ],
            "bar_visible": bar_observation[
                "visible"
            ],
            "bar_distance": bar_observation[
                "distance"
            ],

            "nearby_cats": [
                item["name"]
                for item in nearby_cats
            ],
            "nearby_cat_details": nearby_cats,

            "visible_cronenbergs": [
                item["id"]
                for item in visible_cronenbergs
            ],
            "visible_cronenberg_details": (
                visible_cronenbergs
            ),

            "huntable_cronenbergs": [
                item["id"]
                for item in huntable_cronenbergs
            ],
            "huntable_cronenberg_details": (
                huntable_cronenbergs
            ),
            "cronenberg_danger": danger,

            "visible_boxes": [
                item["id"]
                for item in visible_boxes
            ],
            "visible_box_details": visible_boxes,

            "unexplored_boxes": [
                item["id"]
                for item in unexplored_boxes
            ],

            "occupied_transfer_boxes": [
                item["id"]
                for item
                in occupied_transfer_boxes
            ],
            "occupied_transfer_box_details": (
                occupied_transfer_boxes
            ),

            "interesting_unknown": bool(
                unexplored_boxes
            ),

            "current_layer": current_layer,
            "available_cat_energy": (
                available_cat_energy
            ),
            "can_create_exploration_pair": (
                can_create_exploration_pair
            ),
            "exploration_pair_energy_cost": (
                exploration_pair_energy_cost
            ),
            "exploration_destination_layer": (
                exploration_destination_layer
            ),
            "exploration_destination_position": (
                exploration_destination_position
            ),
            "exploration_plan": deepcopy(
                exploration_plan
            ),

            "shareable_legend_count": (
                shareable_legend_count
            ),

            "observed": True
        }

        event = {
            "name": "cat_environment_observed",
            "cat": cat.get("name"),
            "observations": deepcopy(
                observations
            ),
            "observed": True
        }

        mind = cat.setdefault(
            "mind",
            {}
        )

        mind["last_observations"] = (
            deepcopy(observations)
        )

        mind.setdefault(
            "observation_history",
            []
        ).append(
            deepcopy(event)
        )

        self._record(
            event
        )

        return observations

    def _observe_nearby_cats(
        self,
        cat,
        position,
        radius
    ):
        observed = []

        for candidate in self.cats_layer.cats:
            if candidate is cat:
                continue

            candidate_position = (
                candidate.get("position")
                if isinstance(
                    candidate,
                    dict
                )
                else None
            )

            if candidate_position is None:
                continue

            distance = self._distance(
                position,
                candidate_position
            )

            if distance > radius:
                continue

            observed.append({
                "name": candidate.get(
                    "name"
                ),
                "distance": distance,
                "position": deepcopy(
                    candidate_position
                )
            })

        observed.sort(
            key=lambda item: item[
                "distance"
            ]
        )

        return observed

    def _observe_cronenbergs(
        self,
        position,
        radius
    ):
        observed = []

        for cronenberg in getattr(
            self.universe,
            "cronenbergs",
            []
        ):
            if not getattr(
                cronenberg,
                "is_alive",
                False
            ):
                continue

            cronenberg_position = getattr(
                cronenberg,
                "position",
                None
            )

            if cronenberg_position is None:
                continue

            distance = self._distance(
                position,
                cronenberg_position
            )

            if distance > radius:
                continue

            observed.append({
                "id": cronenberg.id,
                "name": getattr(
                    cronenberg,
                    "name",
                    cronenberg.id
                ),
                "size": float(
                    getattr(
                        cronenberg,
                        "size",
                        1.0
                    )
                ),
                "distance": distance,
                "position": deepcopy(
                    cronenberg_position
                )
            })

        observed.sort(
            key=lambda item: item[
                "distance"
            ]
        )

        return observed

    def _huntable_cronenbergs(
        self,
        cat,
        cronenbergs
    ):
        cat_size = max(
            0.000001,
            float(
                cat.get(
                    "size",
                    1.0
                )
            )
        )

        return [
            {
                **item,
                "size_ratio": (
                    item["size"]
                    / cat_size
                )
            }
            for item in cronenbergs
            if (
                item["size"]
                / cat_size
            ) <= self.HUNTABLE_SIZE_RATIO
        ]

    def _observe_quantum_boxes(
        self,
        cat,
        position,
        radius
    ):
        observed = []

        for box in getattr(
            self.universe,
            "quantum_boxes",
            []
        ):
            visible_to = getattr(
                box,
                "is_visible_to",
                None
            )

            if (
                callable(visible_to)
                and not visible_to(cat)
            ):
                continue

            box_position = getattr(
                box,
                "position",
                None
            )

            if box_position is None:
                continue

            distance = self._distance(
                position,
                box_position
            )

            if distance > radius:
                continue

            cat_observation = getattr(
                box,
                "cat_observation_state",
                None
            )

            occupancy = (
                cat_observation(cat)
                if callable(cat_observation)
                else {
                    "visible": True,
                    "occupied": False,
                    "occupancy_state": (
                        "unknown"
                    ),
                    "occupant_identity_visible": (
                        False
                    )
                }
            )

            observed.append({
                "id": box.id,
                "state": getattr(
                    box,
                    "state",
                    None
                ),
                "collapsed": bool(
                    getattr(
                        box,
                        "collapse",
                        {}
                    ).get(
                        "collapsed",
                        False
                    )
                ),
                "occupied": occupancy.get(
                    "occupied",
                    False
                ),
                "occupancy_state": (
                    occupancy.get(
                        "occupancy_state",
                        "unknown"
                    )
                ),
                "occupant_identity_visible": (
                    occupancy.get(
                        "occupant_identity_visible",
                        False
                    )
                ),
                "distance": distance,
                "position": deepcopy(
                    box_position
                )
            })

        observed.sort(
            key=lambda item: item[
                "distance"
            ]
        )

        return observed

    def _observe_bar(
        self,
        cat,
        position,
        radius
    ):
        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None
        )

        if quantum_space is None:
            return {
                "known": self._cat_knows_bar(
                    cat
                ),
                "visible": False,
                "distance": None
            }

        door = getattr(
            quantum_space,
            "bar_front_door",
            None
        )

        if not door:
            return {
                "known": self._cat_knows_bar(
                    cat
                ),
                "visible": False,
                "distance": None
            }

        door_position = door.get(
            "position"
        )

        distance = (
            self._distance(
                position,
                door_position
            )
            if door_position is not None
            else None
        )

        visible = bool(
            distance is not None
            and distance <= radius
        )

        return {
            "known": bool(
                visible
                or self._cat_knows_bar(
                    cat
                )
            ),
            "visible": visible,
            "distance": distance
        }

    def _cat_knows_bar(
        self,
        cat
    ):
        traits = cat.get(
            "special_traits",
            []
        )

        if (
            "sees_direct_path_to_bar"
            in traits
        ):
            return True

        memory = cat.get(
            "memory"
        )

        if memory is None:
            return False

        for event in getattr(
            memory,
            "events",
            []
        ):
            if event.get(
                "location"
            ) in {
                "meeting_place",
                "bar",
                "bar_front_door"
            }:
                return True

            if event.get(
                "event_type"
            ) in {
                "bar_entry",
                "cat_drank_milk_at_bar",
                "bouncer_petted_cat",
                "safe_at_bar"
            }:
                return True

        return False

    def _box_was_explored(
        self,
        cat,
        box_id
    ):
        memory = cat.get(
            "memory"
        )

        if memory is None:
            return False

        for event in getattr(
            memory,
            "events",
            []
        ):
            if event.get(
                "event_type"
            ) not in {
                "box_explored",
                "box_entered",
                "quantum_box_observed"
            }:
                continue

            if box_id in event.get(
                "participants",
                []
            ):
                return True

            details = event.get(
                "details",
                {}
            )

            if details.get(
                "box_id"
            ) == box_id:
                return True

        return False

    def _cronenberg_danger(
        self,
        cat,
        cronenbergs
    ):
        if not cronenbergs:
            return 0.0

        cat_size = max(
            0.000001,
            float(
                cat.get(
                    "size",
                    1.0
                )
            )
        )

        highest_ratio = max(
            item["size"] / cat_size
            for item in cronenbergs
        )

        return min(
            1.0,
            highest_ratio
            / 2.0
        )

    def _distance(
        self,
        first,
        second
    ):
        if first is None or second is None:
            return float("inf")

        return math.sqrt(
            (
                float(first.get("x", 0.0))
                - float(second.get("x", 0.0))
            ) ** 2
            + (
                float(first.get("y", 0.0))
                - float(second.get("y", 0.0))
            ) ** 2
            + (
                float(first.get("z", 0.0))
                - float(second.get("z", 0.0))
            ) ** 2
        )

    def _record(
        self,
        event
    ):
        self.history.append(
            deepcopy(event)
        )

        quantum_events = getattr(
            self.universe,
            "quantum_events",
            None
        )

        if quantum_events is not None:
            quantum_events.append(
                deepcopy(event)
            )

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None
        )

        if emit_event is not None:
            emit_event(
                deepcopy(event)
            )