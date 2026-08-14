from copy import deepcopy

from cats.cat_knowledge import (
    CatKnowledge
)
from cats.cat_olfaction import (
    CatOlfaction
)


class CatIntentionExecutor:


    NAVIGATION_INTENTS = {
        "visit_bar": "return_to_bar",
        "hunt_cronenberg": (
            "hunt_nearest_cronenberg"
        ),
        "track_cronenberg_scent": (
            "hunt_nearest_cronenberg"
        ),
        "avoid_cronenberg_scent": (
            "return_to_bar"
        )
    }

    DEFERRED_INTENTS = {
        "approach_cat": (
            "cat_social_body_system"
        ),
        "observe": (
            "cat_observation_body_system"
        )
    }

    def __init__(
        self,
        cats_layer
    ):
        self.cats_layer = cats_layer
        self.universe = cats_layer.universe
        self.history = []

    def execute_current_intention(
        self,
        cat,
        cronenbergs=None,
        step_size=None
    ):
        if not isinstance(
            cat,
            dict
        ):
            return self._record({
                "name": (
                    "cat_intention_execution_failed"
                ),
                "reason": "invalid_cat",
                "executed": False
            })

        if cat.get("type") != "cat":
            return self._record({
                "name": (
                    "cat_intention_execution_failed"
                ),
                "cat": cat.get("name"),
                "reason": "entity_is_not_cat",
                "executed": False
            })

        mind = cat.get(
            "mind",
            {}
        )

        intention = mind.get(
            "current_intention"
        )

        if not intention:
            return self._record({
                "name": (
                    "cat_intention_execution_skipped"
                ),
                "cat": cat.get("name"),
                "reason": "no_current_intention",
                "executed": False
            })

        intention_type = intention.get(
            "type"
        )

        if intention_type in (
            self.NAVIGATION_INTENTS
        ):
            return self._execute_navigation(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs,
                step_size=step_size
            )

        if intention_type == "rest":
            return self._execute_rest(
                cat=cat,
                intention=intention
            )

        if intention_type == "follow_scent_through_box":
            return (
                self._execute_follow_scent_through_box(
                    cat=cat,
                    intention=intention,
                    cronenbergs=cronenbergs,
                    step_size=step_size
                )
            )

        if intention_type == "sense_quantum_counterpart":
            return self._execute_sense_quantum_counterpart(
                cat=cat,
                intention=intention
            )

        if (
            intention_type
            == "travel_through_known_quantum_box"
        ):
            return (
                self._execute_travel_through_known_quantum_box(
                    cat=cat,
                    intention=intention
                )
            )


        if intention_type == "explore_box":
            return self._execute_explore_box(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs,
                step_size=step_size
            )

        if intention_type == "search_for_scent":
            return self._execute_search_for_scent(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs,
                step_size=step_size
            )

        if intention_type == "follow_known_scent":
            return self._execute_follow_known_scent(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs,
                step_size=step_size
            )

        if intention_type == "share_legend":
            return self._execute_share_legend(
                cat=cat,
                intention=intention
            )

        if (
            intention_type
            == "create_exploration_pair"
        ):
            return (
                self._execute_exploration_pair_creation(
                    cat=cat,
                    intention=intention
                )
            )

        if intention_type in (
            self.DEFERRED_INTENTS
        ):
            return self._defer_intention(
                cat=cat,
                intention=intention
            )

        return self._record({
            "name": (
                "cat_intention_execution_failed"
            ),
            "cat": cat.get("name"),
            "intention": intention_type,
            "reason": "unsupported_intention",
            "executed": False
        })

    def _execute_navigation(
        self,
        cat,
        intention,
        cronenbergs,
        step_size
    ):
        intention_type = intention[
            "type"
        ]

        body_intent = (
            self.NAVIGATION_INTENTS[
                intention_type
            ]
        )

        previous_suggestion = cat.get(
            "suggested_intent"
        )

        cat["suggested_intent"] = (
            body_intent
        )

        offer = (
            self.cats_layer
            .offer_navigation_for_suggested_intent(
                cat=cat,
                cronenbergs=cronenbergs,
                step_size=step_size
            )
        )

        if not offer.get(
            "offered",
            False
        ):
            event = {
                "name": (
                    "cat_intention_body_action_failed"
                ),
                "cat": cat.get("name"),
                "intention": intention_type,
                "body_intent": body_intent,
                "reason": offer.get(
                    "result",
                    "navigation_not_offered"
                ),
                "navigation_offer": offer,
                "previous_suggested_intent": (
                    previous_suggestion
                ),
                "executed": False
            }

            return self._record(
                event
            )

        # KoÄŤka uĹľ se rozhodla ve svĂ© mysli.
        # Executor jejĂ­ vĹŻli znovu nehĂˇzĂ­.
        acceptance = (
            self.cats_layer
            .accept_navigation_offer(
                cat
            )
        )

        if not acceptance.get(
            "accepted",
            False
        ):
            return self._record({
                "name": (
                    "cat_intention_body_action_failed"
                ),
                "cat": cat.get("name"),
                "intention": intention_type,
                "body_intent": body_intent,
                "reason": acceptance.get(
                    "result",
                    "navigation_not_accepted"
                ),
                "navigation_offer": offer,
                "acceptance": acceptance,
                "executed": False
            })

        cat["state"] = (
            "acting_on_own_intention"
        )

        event = {
            "name": (
                "cat_intention_navigation_started"
            ),
            "cat": cat.get("name"),
            "intention": intention_type,
            "body_intent": body_intent,
            "target": intention.get(
                "target"
            ),
            "route_id": acceptance.get(
                "route_id"
            ),
            "destination": acceptance.get(
                "destination"
            ),
            "decision_source": "cat_mind",
            "navigation_offer": {
                key: value
                for key, value
                in offer.items()
                if key not in {
                    "route",
                    "plan"
                }
            },
            "executed": True
        }

        mind = cat.get(
            "mind",
            {}
        )

        mind[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _execute_follow_scent_through_box(
        self,
        cat,
        intention,
        cronenbergs=None,
        step_size=None
    ):
        target = intention.get(
            "target",
            {}
        )

        source_box_id = target.get(
            "box_id"
        )

        target_box_id = target.get(
            "counterpart_box_id"
        )

        if (
            source_box_id is None
            or target_box_id is None
        ):
            return self._record({
                "name": (
                    "cat_scent_box_transfer_failed"
                ),
                "cat": cat.get("name"),
                "reason": "missing_box_pair",
                "executed": False
            })

        transfer_system = getattr(
            self.universe,
            "cat_box_transfer",
            None
        )

        if transfer_system is None:
            return self._record({
                "name": (
                    "cat_scent_box_transfer_failed"
                ),
                "cat": cat.get("name"),
                "reason": (
                    "cat_box_transfer_unavailable"
                ),
                "executed": False
            })

        source_box = next(
            (
                box
                for box
                in getattr(
                    self.universe,
                    "quantum_boxes",
                    []
                )
                if getattr(
                    box,
                    "id",
                    None
                ) == source_box_id
            ),
            None
        )

        if source_box is None:
            return self._finish_scent_box_follow(
                cat=cat,
                intention=intention,
                event={
                    "name": (
                        "cat_scent_box_transfer_failed"
                    ),
                    "cat": cat.get("name"),
                    "identity": target.get(
                        "identity"
                    ),
                    "source_box_id": source_box_id,
                    "target_box_id": target_box_id,
                    "reason": "source_box_not_found",
                    "executed": False
                }
            )

        if getattr(
            source_box,
            "current_layer",
            None
        ) != cat.get(
            "current_layer"
        ):
            return self._finish_scent_box_follow(
                cat=cat,
                intention=intention,
                event={
                    "name": (
                        "cat_scent_box_transfer_failed"
                    ),
                    "cat": cat.get("name"),
                    "identity": target.get(
                        "identity"
                    ),
                    "source_box_id": source_box_id,
                    "target_box_id": target_box_id,
                    "reason": (
                        "source_box_not_in_cat_layer"
                    ),
                    "executed": False
                }
            )

        follow = cat.get(
            "scent_box_follow"
        )

        if (
            isinstance(follow, dict)
            and follow.get(
                "active",
                False
            )
            and follow.get(
                "source_box_id"
            ) == source_box_id
            and follow.get(
                "target_box_id"
            ) == target_box_id
        ):
            return self._advance_scent_box_follow(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs
            )

        cat_position = cat.get(
            "position"
        )

        source_position = getattr(
            source_box,
            "position",
            None
        )

        if (
            not isinstance(
                cat_position,
                dict
            )
            or not isinstance(
                source_position,
                dict
            )
        ):
            return self._record({
                "name": (
                    "cat_scent_box_transfer_failed"
                ),
                "cat": cat.get("name"),
                "reason": "missing_position",
                "executed": False
            })

        if self._same_position(
            cat_position,
            source_position
        ):
            return self._transfer_scent_box_follow(
                cat=cat,
                intention=intention,
                source_box_id=source_box_id,
                target_box_id=target_box_id
            )

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None
        )

        if quantum_space is None:
            return self._record({
                "name": (
                    "cat_scent_box_transfer_failed"
                ),
                "cat": cat.get("name"),
                "reason": (
                    "quantum_space_unavailable"
                ),
                "executed": False
            })

        planned = (
            quantum_space
            .plan_direct_cat_route(
                cat_id=cat.get(
                    "name"
                ),
                start_position=dict(
                    cat_position
                ),
                destination_position=dict(
                    source_position
                ),
                destination=(
                    f"scent_box:"
                    f"{source_box_id}"
                ),
                step_size=step_size
            )
        )

        route = planned["route"]
        route.state = "ready"

        cat["active_route_id"] = (
            route.route_id
        )

        cat["scent_box_follow"] = {
            "active": True,
            "arrived_at_box": False,
            "route_id": route.route_id,
            "source_box_id": source_box_id,
            "target_box_id": target_box_id,
            "identity": target.get(
                "identity"
            ),
            "destination": dict(
                source_position
            )
        }

        cat["state"] = (
            "following_scent_to_quantum_box"
        )

        event = {
            "name": (
                "cat_following_scent_to_box"
            ),
            "cat": cat.get("name"),
            "identity": target.get(
                "identity"
            ),
            "source_box_id": source_box_id,
            "target_box_id": target_box_id,
            "route_id": route.route_id,
            "destination": dict(
                source_position
            ),
            "arrived_at_box": False,
            "decision_source": "cat_mind",
            "executed": True
        }

        cat.setdefault(
            "mind",
            {}
        )[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _advance_scent_box_follow(
        self,
        cat,
        intention,
        cronenbergs=None
    ):
        follow = cat[
            "scent_box_follow"
        ]

        result = (
            self.universe
            .quantum_space
            .advance_cat_route(
                cat=cat,
                cronenbergs=(
                    cronenbergs
                    if cronenbergs is not None
                    else getattr(
                        self.universe,
                        "cronenbergs",
                        []
                    )
                ),
                encounter_system=(
                    self.universe
                    .cat_cronenberg_encounter
                ),
                universe=self.universe
            )
        )

        position = result.get(
            "position"
        )

        if position is not None:
            cat["position"] = dict(
                position
            )

        if result.get(
            "arrived",
            False
        ):
            follow[
                "arrived_at_box"
            ] = True

            follow["active"] = False

            return self._transfer_scent_box_follow(
                cat=cat,
                intention=intention,
                source_box_id=follow[
                    "source_box_id"
                ],
                target_box_id=follow[
                    "target_box_id"
                ]
            )

        event = {
            "name": (
                "cat_following_scent_to_box"
            ),
            "cat": cat.get("name"),
            "identity": follow.get(
                "identity"
            ),
            "source_box_id": follow[
                "source_box_id"
            ],
            "target_box_id": follow[
                "target_box_id"
            ],
            "route_id": follow[
                "route_id"
            ],
            "position": (
                dict(position)
                if position is not None
                else None
            ),
            "route_result": result.get(
                "result"
            ),
            "arrived_at_box": False,
            "decision_source": "cat_mind",
            "executed": (
                result.get(
                    "result"
                )
                != "no_active_route"
            )
        }

        cat.setdefault(
            "mind",
            {}
        )[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _transfer_scent_box_follow(
        self,
        cat,
        intention,
        source_box_id,
        target_box_id
    ):
        target = intention.get(
            "target",
            {}
        )

        result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                cat=cat,
                source_box_id=source_box_id,
                target_box_id=target_box_id
            )
        )

        event = {
            "name": (
                "cat_followed_scent_through_box"
                if result.get(
                    "transferred",
                    False
                )
                else (
                    "cat_scent_box_transfer_failed"
                )
            ),
            "cat": cat.get("name"),
            "identity": target.get(
                "identity"
            ),
            "source_box_id": source_box_id,
            "target_box_id": target_box_id,
            "source_layer": target.get(
                "source_layer"
            ),
            "target_layer": target.get(
                "target_layer"
            ),
            "transfer": result,
            "arrived_at_box": True,
            "decision_source": "cat_mind",
            "executed": result.get(
                "transferred",
                False
            )
        }

        return self._finish_scent_box_follow(
            cat=cat,
            intention=intention,
            event=event
        )

    def _finish_scent_box_follow(
        self,
        cat,
        intention,
        event
    ):
        mind = cat.setdefault(
            "mind",
            {}
        )

        mind[
            "previous_intention"
        ] = deepcopy(
            intention
        )

        mind[
            "current_intention"
        ] = None

        mind[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        cat.pop(
            "active_route_id",
            None
        )

        follow = cat.get(
            "scent_box_follow"
        )

        if isinstance(
            follow,
            dict
        ):
            follow["active"] = False

        return self._record(
            event
        )

    @staticmethod
    def _same_position(
        first,
        second,
        tolerance=1e-9
    ):
        return all(
            abs(
                float(
                    first.get(
                        axis,
                        0.0
                    )
                )
                - float(
                    second.get(
                        axis,
                        0.0
                    )
                )
            ) <= tolerance
            for axis in (
                "x",
                "y",
                "z"
            )
        )

    def _execute_travel_through_known_quantum_box(
            self,
            cat,
            intention,
    ):

        target = intention.get(
            "target",
            {}
        )

        if not isinstance(
            target,
            dict
        ):
            return self._record({
                "name":(
                    "cat_quantum_box_travel_failed"
                        ),
                "cat": cat.get("name"),
                "reason": "invalid_target",
                "executed": False
            })

        source_box_id = target.get(
            "source_box_id"
        )
        counterpart_box_id = target.get(
            "counterpart_box_id"
        )

        if (
            source_box_id is None
            or counterpart_box_id is None
        ):
            return self._record({
                "name": (
                    "cat_quantum_box_travel_failed"
                ),
                "cat": cat.get("name"),
                "reason": "missing_box_pair",
                "executed": False
            })

        observation = cat.get(
            "current_quantum_counterpart_observation"
        )

        if not isinstance(
            observation,
            dict
        ):
            return self._record({
                "name":(
                    "cat_quantum_box_travel_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "counterpart_box_id": (
                    counterpart_box_id
                ),
                "reason": (
                    "counterpart_observation_missing"
                ),
                "executed": False
            })

        if not observation.get(
            "pair_currently_valid",
            False
        ):
            return self._record({
                "name":(
                    "cat_quantum_box_travel_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "counterpart_box_id": (
                    counterpart_box_id
                ),
                "reason": (
                    "counterpart_observation_invalid"
                ),
                "executed": False
            })

        if (
            observation.get(
                "source_box_id"
            ) != source_box_id
        ):
            return self._record({
                "name":(
                    "cat_quantum_box_travel_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "counterpart_box_id": (
                    counterpart_box_id
                ),
                "reason": (
                    "observation_pair_mismatch"
                ),
                "executed": False
            })

        source_box = next(
            (
                box for box in getattr(
                self.universe,
                "quantum_boxes",
                []
            )
                if getattr(
                box,
                "id",
                None
            ) == source_box_id

            ),
            None
        )

        if source_box is None:
            return self._record({
                "name":(
                    "cat_quantum_box_travel_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "counterpart_box_id": (
                    counterpart_box_id
                ),
                "reason": (
                    "source_box_no_longer_exists"
                ),
                "executed": False
            })

        if getattr(
            source_box,
            "current_layer",
            None
        ) != cat.get(
            "current_layer",
        ):
            return self._record({
                "name":(
                    "cat_quantum_box_travel_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "counterpart_box_id": (
                    counterpart_box_id
                ),
                "reason": (
                    "source_box_not_in_cat_layer"
                ),
                "executed": False
            })

        source_position = getattr(
            source_box,
            "position",
            None
        )

        cat_possition = cat.get(
            "position"
        )

        if (
            not isinstance(
                source_position,
                dict
            )
        ):
            return self._record({
                "name":(
                    "cat_quantum_box_travel_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "counterpart_box_id": (
                    counterpart_box_id
                ),
                "reason": "missing_position",
                "executed": False
            })

        if not self._same_position(
            cat_possition,
            source_position
        ):
            return self._record({
                "name":(
                    "cat_quantum_box_travel_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "counterpart_box_id": (
                    counterpart_box_id
                ),
                "reason": (
                    "cat_not_at_source_box"
                ),
                "executed": False
            })

        transfer_system = getattr(
            self.universe,
            "cat_box_transfer",
            None
        )

        if transfer_system is None:
            return self._record({
                "name":(
                    "cat_quantum_box_travel_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "counterpart_box_id": (
                    counterpart_box_id
                ),
                "reason": (
                    "cat_box_tranfer_unavaible"
                ),
                "executed": False
            })

        result =(
            transfer_system
            .transfer_cat(
                cat=cat,source_box_id =source_box_id,
                target_box_id=counterpart_box_id
            )
        )

        transferred = result.get(
            "transferred",
            False
        )

        event = {
            "name": (
                "cat_traveled_through_known_quantum_box"
                if transferred
                else "cat_quantum_box_travel_failed"
            ),
            "cat": cat.get("name"),
            "source_box_id": source_box_id,
            "counterpart_box_id": (
                counterpart_box_id
            ),
            "source_layer": target.get(
                "source_layer"
            ),
            "transfer": deepcopy(
                result
            ),
            "decision_source": "cat_mind",
            "executed": transferred
        }

        mind = cat.setdefault(
            "mind",
            {}
        )

        mind[
            "previous_intention"
        ] = deepcopy(
            intention
        )

        mind[
            "current_intention"
        ] = None

        if transferred:
            mind[
                "active_body_execution"
            ] = deepcopy(
                event
            )

            cat.pop(
                "current_quantum_counterpart_observation",
                None
            )

            return self._record(
                event
            )

        failure_reason = result.get(
            "reason",
            "quantum_transfer_failed"
        )

        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Cat quantum box transfer failed: "
                    f"{failure_reason}"
                ),
                source_component=(
                    "cat_intention_executor"
                ),
                source_operation=(
                    "quantum_box_travel_failed"
                )
            )
        )

        memory = cat[
            "memory"
        ].remember(
            event_type=(
                "quantum_box_layer_transfer_failed"
            ),
            universe_tick=(
                self.universe
                .quantum_state.get(
                    "tick_count",
                    0
                )
            ),
            location=deepcopy(
                cat.get(
                    "position"
                )
            ),
            participants=[
                source_box_id,
                counterpart_box_id
            ],
            details={
                "source_layer": target.get(
                    "source_layer"
                ),
                "target_layer": target.get(
                    "target_layer"
                ),
                "reason": failure_reason,
                "cronenberg_id": cronenberg.id
            }
        )

        event[
            "reason"
        ] = failure_reason

        event[
            "cronenberg_id"
        ] = cronenberg.id

        event[
            "memory"
        ] = deepcopy(
            memory
        )

        mind[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _execute_sense_quantum_counterpart(
        self,
        cat,
        intention
    ):
        target = intention.get(
            "target",
            {}
        )

        if isinstance(
            target,
            dict
        ):
            source_box_id = target.get(
                "box_id"
            )
        else:
            source_box_id = target

        if source_box_id is None:
            return self._record({
                "name": (
                    "cat_quantum_counterpart_"
                    "sensing_failed"
                ),
                "cat": cat.get("name"),
                "reason": "missing_box_id",
                "executed": False
            })

        source_box = next(
            (
                box
                for box
                in getattr(
                    self.universe,
                    "quantum_boxes",
                    []
                )
                if getattr(
                    box,
                    "id",
                    None
                ) == source_box_id
            ),
            None
        )

        if source_box is None:
            return self._record({
                "name": (
                    "cat_quantum_counterpart_"
                    "sensing_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "reason": (
                    "source_box_no_longer_exists"
                ),
                "executed": False
            })

        if getattr(
            source_box,
            "current_layer",
            None
        ) != cat.get(
            "current_layer"
        ):
            return self._record({
                "name": (
                    "cat_quantum_counterpart_"
                    "sensing_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "reason": (
                    "source_box_not_in_cat_layer"
                ),
                "executed": False
            })

        source_position = getattr(
            source_box,
            "position",
            None
        )

        if (
            not isinstance(
                source_position,
                dict
            )
            or not self._same_position(
                cat.get(
                    "position",
                    {}
                ),
                source_position
            )
        ):
            return self._record({
                "name": (
                    "cat_quantum_counterpart_"
                    "sensing_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "reason": (
                    "cat_not_at_source_box"
                ),
                "executed": False
            })

        pairing = getattr(
            source_box,
            "quantum_counterpart",
            {}
        )

        if not pairing.get(
            "paired",
            False
        ):
            return self._record({
                "name": (
                    "cat_quantum_counterpart_"
                    "sensing_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "reason": (
                    "pair_no_longer_exists"
                ),
                "executed": False
            })

        counterpart_id = pairing.get(
            "box_id"
        )

        counterpart = next(
            (
                box
                for box
                in getattr(
                    self.universe,
                    "quantum_boxes",
                    []
                )
                if getattr(
                    box,
                    "id",
                    None
                ) == counterpart_id
            ),
            None
        )

        if counterpart is None:
            return self._record({
                "name": (
                    "cat_quantum_counterpart_"
                    "sensing_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "reason": (
                    "counterpart_no_longer_exists"
                ),
                "executed": False
            })

        reverse_pairing = getattr(
            counterpart,
            "quantum_counterpart",
            {}
        )

        if (
            not reverse_pairing.get(
                "paired",
                False
            )
            or reverse_pairing.get(
                "box_id"
            ) != source_box_id
        ):
            return self._record({
                "name": (
                    "cat_quantum_counterpart_"
                    "sensing_failed"
                ),
                "cat": cat.get("name"),
                "source_box_id": source_box_id,
                "reason": (
                    "pair_not_reciprocal"
                ),
                "executed": False
            })

        observation = {
            "source_box_id": source_box_id,
            "counterpart_box_id": (
                counterpart.id
            ),
            "source_layer": getattr(
                source_box,
                "current_layer",
                None
            ),
            "counterpart_layer": getattr(
                counterpart,
                "current_layer",
                None
            ),
            "counterpart_position": deepcopy(
                getattr(
                    counterpart,
                    "position",
                    {}
                )
            ),
            "observed_tick": getattr(
                self.universe,
                "universe_tick",
                None
            ),
            "temporary": True,
            "pair_currently_valid": True
        }

        # NEN? to knowledge ani permanentn? mapa.
        # Je to jen pr?v? platn? pozorov?n?.
        cat[
            "current_quantum_counterpart_observation"
        ] = deepcopy(
            observation
        )

        mind = cat.setdefault(
            "mind",
            {}
        )

        mind[
            "previous_intention"
        ] = deepcopy(
            intention
        )

        mind[
            "current_intention"
        ] = None

        event = {
            "name": (
                "cat_sensed_quantum_counterpart"
            ),
            "cat": cat.get("name"),
            "observation": deepcopy(
                observation
            ),
            "decision_source": "cat_mind",
            "executed": True
        }

        mind[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _execute_explore_box(
        self,
        cat,
        intention,
        cronenbergs=None,
        step_size=None
    ):
        target = intention.get(
            "target"
        )

        if isinstance(
            target,
            dict
        ):
            box_id = (
                target.get("id")
                or target.get("box_id")
            )
        else:
            box_id = target

        if box_id is None:
            return self._record({
                "name": (
                    "cat_box_exploration_failed"
                ),
                "cat": cat.get("name"),
                "reason": "missing_box_id",
                "executed": False
            })

        box = next(
            (
                candidate
                for candidate
                in getattr(
                    self.universe,
                    "quantum_boxes",
                    []
                )
                if getattr(
                    candidate,
                    "id",
                    None
                ) == box_id
            ),
            None
        )

        if box is None:
            return self._record({
                "name": (
                    "cat_box_exploration_failed"
                ),
                "cat": cat.get("name"),
                "box_id": box_id,
                "reason": "box_not_found",
                "executed": False
            })

        if getattr(
            box,
            "current_layer",
            None
        ) != cat.get(
            "current_layer",
            "quantum_layer"
        ):
            return self._record({
                "name": (
                    "cat_box_exploration_failed"
                ),
                "cat": cat.get("name"),
                "box_id": box_id,
                "reason": (
                    "box_not_in_cat_layer"
                ),
                "executed": False
            })

        exploration = cat.get(
            "box_exploration"
        )

        if (
            isinstance(
                exploration,
                dict
            )
            and exploration.get(
                "active",
                False
            )
            and exploration.get(
                "box_id"
            ) == box_id
        ):
            return self._advance_box_exploration(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs
            )

        cat_position = cat.get(
            "position",
            {}
        )

        box_position = getattr(
            box,
            "position",
            None
        )

        if not isinstance(
            box_position,
            dict
        ):
            return self._record({
                "name": (
                    "cat_box_exploration_failed"
                ),
                "cat": cat.get("name"),
                "box_id": box_id,
                "reason": (
                    "box_position_missing"
                ),
                "executed": False
            })

        if self._same_position(
            cat_position,
            box_position
        ):
            return self._finish_box_exploration(
                cat=cat,
                intention=intention,
                box=box
            )

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None
        )

        if quantum_space is None:
            return self._record({
                "name": (
                    "cat_box_exploration_failed"
                ),
                "cat": cat.get("name"),
                "box_id": box_id,
                "reason": (
                    "quantum_space_unavailable"
                ),
                "executed": False
            })

        planned = (
            quantum_space
            .plan_direct_cat_route(
                cat_id=cat.get(
                    "name"
                ),
                start_position=dict(
                    cat_position
                ),
                destination_position=dict(
                    box_position
                ),
                destination=(
                    f"explore_box:{box_id}"
                ),
                step_size=step_size
            )
        )

        route = planned["route"]
        route.state = "ready"

        cat["active_route_id"] = (
            route.route_id
        )

        cat["box_exploration"] = {
            "active": True,
            "arrived": False,
            "box_id": box_id,
            "route_id": route.route_id,
            "destination": dict(
                box_position
            )
        }

        event = {
            "name": (
                "cat_approaching_box_to_explore"
            ),
            "cat": cat.get("name"),
            "box_id": box_id,
            "route_id": route.route_id,
            "destination": dict(
                box_position
            ),
            "arrived": False,
            "decision_source": (
                "cat_mind"
            ),
            "executed": True
        }

        cat.setdefault(
            "mind",
            {}
        )[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _advance_box_exploration(
        self,
        cat,
        intention,
        cronenbergs=None
    ):
        exploration = cat[
            "box_exploration"
        ]

        result = (
            self.universe
            .quantum_space
            .advance_cat_route(
                cat=cat,
                cronenbergs=(
                    cronenbergs
                    if cronenbergs is not None
                    else getattr(
                        self.universe,
                        "cronenbergs",
                        []
                    )
                ),
                encounter_system=(
                    self.universe
                    .cat_cronenberg_encounter
                ),
                universe=self.universe
            )
        )

        position = result.get(
            "position"
        )

        if position is not None:
            cat["position"] = dict(
                position
            )

        if result.get(
            "arrived",
            False
        ):
            box = next(
                (
                    candidate
                    for candidate
                    in getattr(
                        self.universe,
                        "quantum_boxes",
                        []
                    )
                    if getattr(
                        candidate,
                        "id",
                        None
                    ) == exploration.get(
                        "box_id"
                    )
                ),
                None
            )

            if box is None:
                return self._record({
                    "name": (
                        "cat_box_exploration_failed"
                    ),
                    "cat": cat.get("name"),
                    "reason": (
                        "box_disappeared"
                    ),
                    "executed": False
                })

            return self._finish_box_exploration(
                cat=cat,
                intention=intention,
                box=box
            )

        event = {
            "name": (
                "cat_approaching_box_to_explore"
            ),
            "cat": cat.get("name"),
            "box_id": exploration.get(
                "box_id"
            ),
            "route_id": exploration.get(
                "route_id"
            ),
            "position": (
                dict(position)
                if position is not None
                else None
            ),
            "destination": dict(
                exploration[
                    "destination"
                ]
            ),
            "arrived": False,
            "decision_source": (
                "cat_mind"
            ),
            "executed": (
                result.get(
                    "result"
                )
                != "no_active_route"
            )
        }

        cat.setdefault(
            "mind",
            {}
        )[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _finish_box_exploration(
        self,
        cat,
        intention,
        box
    ):
        box_id = getattr(
            box,
            "id",
            None
        )

        observation = (
            box.cat_observation_state(
                cat
            )
            if callable(
                getattr(
                    box,
                    "cat_observation_state",
                    None
                )
            )
            else {}
        )

        memory = cat.get(
            "memory"
        )

        remembered = None

        if memory is not None:
            remembered = memory.remember(
                event_type=(
                    "quantum_box_observed"
                ),
                universe_tick=getattr(
                    self.universe,
                    "universe_tick",
                    None
                ),
                location=cat.get(
                    "current_layer"
                ),
                participants=[
                    box_id
                ],
                details={
                    "box_id": box_id,
                    "position": deepcopy(
                        getattr(
                            box,
                            "position",
                            {}
                        )
                    ),
                    "observation": deepcopy(
                        observation
                    )
                }
            )

        exploration = cat.setdefault(
            "box_exploration",
            {}
        )

        exploration.update({
            "active": False,
            "arrived": True,
            "box_id": box_id,
            "observed": True
        })

        cat.pop(
            "active_route_id",
            None
        )

        mind = cat.setdefault(
            "mind",
            {}
        )

        mind[
            "previous_intention"
        ] = deepcopy(
            intention
        )

        mind[
            "current_intention"
        ] = None

        event = {
            "name": (
                "cat_explored_quantum_box"
            ),
            "cat": cat.get("name"),
            "box_id": box_id,
            "position": deepcopy(
                getattr(
                    box,
                    "position",
                    {}
                )
            ),
            "observation": deepcopy(
                observation
            ),
            "memory": deepcopy(
                remembered
            ),
            "arrived": True,
            "decision_source": (
                "cat_mind"
            ),
            "executed": True
        }

        mind[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _execute_search_for_scent(
        self,
        cat,
        intention,
        cronenbergs=None,
        step_size=None
    ):
        target = intention.get(
            "target",
            {}
        )

        identity = target.get(
            "identity"
        )

        direction = target.get(
            "trail_direction",
            {}
        )

        unit_vector = direction.get(
            "unit_vector"
        )

        if (
            identity is None
            or not isinstance(
                unit_vector,
                dict
            )
        ):
            return self._record({
                "name": "cat_scent_search_failed",
                "cat": cat.get("name"),
                "reason": "invalid_search_direction",
                "executed": False
            })

        search = cat.get(
            "scent_search"
        )

        if (
            isinstance(search, dict)
            and search.get("active", False)
            and search.get("identity") == identity
        ):
            return self._advance_scent_search(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs
            )

        start = cat.get(
            "position",
            {}
        )

        distance = float(
            target.get(
                "search_distance",
                1.0
            )
        )

        destination = {
            axis: (
                float(
                    start.get(
                        axis,
                        0.0
                    )
                )
                + float(
                    unit_vector.get(
                        axis,
                        0.0
                    )
                )
                * distance
            )
            for axis in (
                "x",
                "y",
                "z"
            )
        }

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None
        )

        if quantum_space is None:
            return self._record({
                "name": "cat_scent_search_failed",
                "cat": cat.get("name"),
                "reason": "quantum_space_unavailable",
                "executed": False
            })

        planned = (
            quantum_space
            .plan_direct_cat_route(
                cat_id=cat.get("name"),
                start_position=dict(start),
                destination_position=dict(
                    destination
                ),
                destination=(
                    f"scent_search:{identity}"
                ),
                step_size=step_size
            )
        )

        route = planned["route"]
        route.state = "ready"

        cat["active_route_id"] = (
            route.route_id
        )

        cat["scent_search"] = {
            "active": True,
            "identity": identity,
            "layer": cat.get(
                "current_layer"
            ),
            "route_id": route.route_id,
            "attempts": int(
                target.get(
                    "attempt",
                    1
                )
            ) - 1,
            "current_attempt": int(
                target.get(
                    "attempt",
                    1
                )
            ),
            "max_attempts": int(
                target.get(
                    "max_attempts",
                    1
                )
            ),
            "start_position": dict(start),
            "destination": dict(
                destination
            ),
            "trail_direction": deepcopy(
                direction
            ),
            "arrived": False
        }

        event = {
            "name": "cat_searching_for_scent",
            "cat": cat.get("name"),
            "identity": identity,
            "attempt": target.get(
                "attempt",
                1
            ),
            "max_attempts": target.get(
                "max_attempts",
                1
            ),
            "route_id": route.route_id,
            "start_position": dict(start),
            "destination": dict(
                destination
            ),
            "arrived": False,
            "decision_source": "cat_mind",
            "executed": True
        }

        cat.setdefault(
            "mind",
            {}
        )[
            "active_body_execution"
        ] = deepcopy(event)

        return self._record(event)

    def _advance_scent_search(
        self,
        cat,
        intention,
        cronenbergs=None
    ):
        search = cat[
            "scent_search"
        ]

        result = (
            self.universe
            .quantum_space
            .advance_cat_route(
                cat=cat,
                cronenbergs=(
                    cronenbergs
                    if cronenbergs is not None
                    else getattr(
                        self.universe,
                        "cronenbergs",
                        []
                    )
                ),
                encounter_system=(
                    self.universe
                    .cat_cronenberg_encounter
                ),
                universe=self.universe
            )
        )

        position = result.get(
            "position"
        )

        if position is not None:
            cat["position"] = dict(
                position
            )

        olfaction = CatOlfaction.sniff(
            cat=cat,
            universe=self.universe
        )

        reacquired = next(
            (
                item
                for item
                in olfaction.get(
                    "detected_aromas",
                    []
                )
                if item.get(
                    "recognition",
                    {}
                ).get(
                    "recognized",
                    False
                )
                and item.get(
                    "recognition",
                    {}
                ).get(
                    "identity"
                ) == search.get(
                    "identity"
                )
            ),
            None
        )

        if reacquired is not None:
            CatKnowledge.remember_olfaction(
                cat=cat,
                olfaction=olfaction,
                current_layer=cat.get(
                    "current_layer",
                    "unknown"
                ),
                universe_tick=getattr(
                    self.universe,
                    "universe_tick",
                    None
                )
            )

            route = (
                self.universe
                .quantum_space
                .find_cat_route(
                    cat.get("name")
                )
            )

            if route is not None:
                route.stop_observation()

            search["active"] = False
            search["arrived"] = False
            search["reacquired"] = True
            search["reacquired_at"] = dict(
                cat.get(
                    "position",
                    {}
                )
            )
            search[
                "reacquired_source_id"
            ] = reacquired.get(
                "entity_id"
            )

            cat.pop(
                "active_route_id",
                None
            )

            mind = cat.setdefault(
                "mind",
                {}
            )

            mind[
                "previous_intention"
            ] = deepcopy(
                intention
            )

            mind[
                "current_intention"
            ] = None

            event = {
                "name": (
                    "cat_reacquired_scent_"
                    "during_search"
                ),
                "cat": cat.get("name"),
                "identity": search.get(
                    "identity"
                ),
                "source_id": reacquired.get(
                    "entity_id"
                ),
                "position": dict(
                    cat.get(
                        "position",
                        {}
                    )
                ),
                "olfaction": deepcopy(
                    olfaction
                ),
                "search_interrupted": True,
                "decision_source": "cat_mind",
                "executed": True
            }

            mind[
                "active_body_execution"
            ] = deepcopy(
                event
            )

            return self._record(
                event
            )

        if result.get(
            "arrived",
            False
        ):
            return self._finish_scent_search(
                cat=cat,
                intention=intention
            )

        event = {
            "name": "cat_searching_for_scent",
            "cat": cat.get("name"),
            "identity": search.get(
                "identity"
            ),
            "attempt": search.get(
                "current_attempt"
            ),
            "max_attempts": search.get(
                "max_attempts"
            ),
            "route_id": search.get(
                "route_id"
            ),
            "position": (
                dict(position)
                if position is not None
                else None
            ),
            "destination": dict(
                search["destination"]
            ),
            "arrived": False,
            "decision_source": "cat_mind",
            "executed": (
                result.get("result")
                != "no_active_route"
            )
        }

        cat.setdefault(
            "mind",
            {}
        )[
            "active_body_execution"
        ] = deepcopy(event)

        return self._record(event)

    def _finish_scent_search(
        self,
        cat,
        intention
    ):
        search = cat[
            "scent_search"
        ]

        search["active"] = False
        search["arrived"] = True

        search["attempts"] = int(
            search.get(
                "current_attempt",
                1
            )
        )

        cat.pop(
            "active_route_id",
            None
        )

        mind = cat.setdefault(
            "mind",
            {}
        )

        mind[
            "previous_intention"
        ] = deepcopy(
            intention
        )

        mind[
            "current_intention"
        ] = None

        event = {
            "name": (
                "cat_completed_scent_search_step"
            ),
            "cat": cat.get("name"),
            "identity": search.get(
                "identity"
            ),
            "attempt": search.get(
                "attempts"
            ),
            "max_attempts": search.get(
                "max_attempts"
            ),
            "position": dict(
                cat.get(
                    "position",
                    {}
                )
            ),
            "trail_direction": deepcopy(
                search.get(
                    "trail_direction"
                )
            ),
            "arrived": True,
            "decision_source": "cat_mind",
            "executed": True
        }

        mind[
            "active_body_execution"
        ] = deepcopy(event)

        return self._record(event)

    def _execute_follow_known_scent(
        self,
        cat,
        intention,
        cronenbergs=None,
        step_size=None
    ):
        target = intention.get(
            "target",
            {}
        )

        layer = target.get(
            "layer"
        )

        position = target.get(
            "position"
        )

        if (
            layer is None
            or not isinstance(
                position,
                dict
            )
        ):
            return self._record({
                "name": (
                    "cat_known_scent_follow_failed"
                ),
                "cat": cat.get("name"),
                "reason": "invalid_scent_target",
                "executed": False
            })

        if (
            layer
            != cat.get(
                "current_layer"
            )
        ):
            return self._record({
                "name": (
                    "cat_known_scent_follow_failed"
                ),
                "cat": cat.get("name"),
                "identity": target.get(
                    "identity"
                ),
                "reason": (
                    "cross_layer_scent_navigation_"
                    "not_available_yet"
                ),
                "executed": False
            })

        follow = cat.get(
            "known_scent_follow"
        )

        if (
            isinstance(
                follow,
                dict
            )
            and follow.get(
                "active",
                False
            )
            and follow.get(
                "source_id"
            ) == target.get(
                "source_id"
            )
            and follow.get(
                "destination"
            ) == position
        ):
            return self._advance_known_scent_follow(
                cat=cat,
                intention=intention,
                cronenbergs=cronenbergs
            )

        cat_position = cat.get(
            "position",
            {}
        )

        already_there = all(
            abs(
                float(
                    cat_position.get(
                        axis,
                        0.0
                    )
                )
                - float(
                    position.get(
                        axis,
                        0.0
                    )
                )
            ) <= 1e-9
            for axis in (
                "x",
                "y",
                "z"
            )
        )

        if already_there:
            return self._finish_known_scent_follow(
                cat=cat,
                intention=intention,
                position=position
            )

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None
        )

        if quantum_space is None:
            return self._record({
                "name": (
                    "cat_known_scent_follow_failed"
                ),
                "cat": cat.get("name"),
                "reason": (
                    "quantum_space_unavailable"
                ),
                "executed": False
            })

        planned = (
            quantum_space
            .plan_direct_cat_route(
                cat_id=cat.get(
                    "name"
                ),
                start_position=dict(
                    cat_position
                ),
                destination_position=dict(
                    position
                ),
                destination=(
                    "known_scent:"
                    f"{target.get('identity')}"
                ),
                step_size=step_size
            )
        )

        route = planned["route"]
        route.state = "ready"

        cat["active_route_id"] = (
            route.route_id
        )

        cat["known_scent_follow"] = {
            "active": True,
            "arrived": False,
            "route_id": route.route_id,
            "identity": target.get(
                "identity"
            ),
            "source_id": target.get(
                "source_id"
            ),
            "destination": dict(
                position
            ),
            "trail_direction": deepcopy(
                target.get(
                    "trail_direction"
                )
            )
        }

        event = {
            "name": (
                "cat_following_known_scent"
            ),
            "cat": cat.get("name"),
            "identity": target.get(
                "identity"
            ),
            "layer": layer,
            "destination": dict(
                position
            ),
            "route_id": route.route_id,
            "arrived": False,
            "decision_source": (
                "cat_mind"
            ),
            "executed": True
        }

        cat.setdefault(
            "mind",
            {}
        )[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _advance_known_scent_follow(
        self,
        cat,
        intention,
        cronenbergs=None
    ):
        follow = cat[
            "known_scent_follow"
        ]

        result = (
            self.universe
            .quantum_space
            .advance_cat_route(
                cat=cat,
                cronenbergs=(
                    cronenbergs
                    if cronenbergs is not None
                    else getattr(
                        self.universe,
                        "cronenbergs",
                        []
                    )
                ),
                encounter_system=(
                    self.universe
                    .cat_cronenberg_encounter
                ),
                universe=self.universe
            )
        )

        position = result.get(
            "position"
        )

        if position is not None:
            cat["position"] = dict(
                position
            )

        if result.get(
            "arrived",
            False
        ):
            return self._finish_known_scent_follow(
                cat=cat,
                intention=intention,
                position=cat[
                    "position"
                ]
            )

        event = {
            "name": (
                "cat_following_known_scent"
            ),
            "cat": cat.get("name"),
            "identity": follow.get(
                "identity"
            ),
            "layer": cat.get(
                "current_layer"
            ),
            "destination": dict(
                follow[
                    "destination"
                ]
            ),
            "route_id": follow[
                "route_id"
            ],
            "position": (
                dict(position)
                if position is not None
                else None
            ),
            "arrived": False,
            "decision_source": (
                "cat_mind"
            ),
            "executed": (
                result.get(
                    "result"
                )
                != "no_active_route"
            )
        }

        cat.setdefault(
            "mind",
            {}
        )[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _finish_known_scent_follow(
        self,
        cat,
        intention,
        position
    ):
        target = intention.get(
            "target",
            {}
        )

        follow = cat.setdefault(
            "known_scent_follow",
            {}
        )

        follow.update({
            "active": False,
            "arrived": True,
            "identity": target.get(
                "identity"
            ),
            "source_id": target.get(
                "source_id"
            ),
            "destination": dict(
                position
            ),
            "trail_direction": deepcopy(
                target.get(
                    "trail_direction"
                )
            )
        })

        cat.pop(
            "active_route_id",
            None
        )

        mind = cat.setdefault(
            "mind",
            {}
        )

        mind[
            "previous_intention"
        ] = deepcopy(
            intention
        )

        mind[
            "current_intention"
        ] = None

        event = {
            "name": (
                "cat_reached_known_scent"
            ),
            "cat": cat.get("name"),
            "identity": target.get(
                "identity"
            ),
            "layer": cat.get(
                "current_layer"
            ),
            "destination": dict(
                position
            ),
            "trail_direction": deepcopy(
                target.get(
                    "trail_direction"
                )
            ),
            "arrived": True,
            "decision_source": (
                "cat_mind"
            ),
            "executed": True
        }

        mind[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _execute_share_legend(
        self,
        cat,
        intention
    ):
        target = intention.get(
            "target"
        )

        listener = None

        if isinstance(
            target,
            dict
        ):
            target_name = (
                target.get("name")
                or target.get("id")
            )
        else:
            target_name = target

        for candidate in getattr(
            self.universe,
            "entities",
            []
        ):
            if not isinstance(
                candidate,
                dict
            ):
                continue

            if candidate.get(
                "name"
            ) == target_name:
                listener = candidate
                break

        if listener is None:
            return self._record({
                "name": "cat_legend_not_shared",
                "cat": cat.get("name"),
                "listener": target_name,
                "reason": "listener_not_found",
                "executed": False
            })

        result = CatKnowledge.share_legend(
            storyteller=cat,
            listener=listener,
            universe=self.universe
        )

        mind = cat.setdefault(
            "mind",
            {}
        )

        mind["previous_intention"] = deepcopy(
            intention
        )

        mind["current_intention"] = None

        event = {
            **result,
            "cat": cat.get("name"),
            "intention": "share_legend",
            "decision_source": "cat_mind",
            "executed": True
        }

        mind[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _execute_exploration_pair_creation(
        self,
        cat,
        intention
    ):
        """
        Ko?ka vytvo?? stabiln? pr?zkumn? p?r
        a ihned jej pou?ije.

        Rozhodnut? u? prob?hlo v CatMind.
        Executor pouze vytvo?? t?lesnou cestu
        a zah?j? p?enos.
        """
        target = intention.get(
            "target",
            {}
        )

        destination_layer = target.get(
            "layer"
        )

        destination_position = target.get(
            "position"
        )

        if (
            destination_layer is None
            or destination_position is None
        ):
            return self._record({
                "name": (
                    "cat_exploration_pair_"
                    "creation_failed"
                ),
                "cat": cat.get("name"),
                "intention": (
                    "create_exploration_pair"
                ),
                "reason": (
                    "missing_exploration_destination"
                ),
                "executed": False
            })

        transfer_system = getattr(
            self.universe,
            "cat_box_transfer",
            None
        )

        if transfer_system is None:
            return self._record({
                "name": (
                    "cat_exploration_pair_"
                    "creation_failed"
                ),
                "cat": cat.get("name"),
                "intention": (
                    "create_exploration_pair"
                ),
                "reason": (
                    "cat_box_transfer_unavailable"
                ),
                "executed": False
            })

        creation = (
            transfer_system
            .create_exploration_pair(
                cat=cat,
                destination_layer=(
                    destination_layer
                ),
                destination_position=(
                    destination_position
                )
            )
        )

        if not creation.get(
            "created",
            False
        ):
            return self._record({
                "name": (
                    "cat_exploration_pair_"
                    "creation_failed"
                ),
                "cat": cat.get("name"),
                "intention": (
                    "create_exploration_pair"
                ),
                "reason": creation.get(
                    "reason",
                    "pair_creation_failed"
                ),
                "creation_result": creation,
                "executed": False
            })

        source_box = creation.get(
            "source_box"
        )

        target_box = creation.get(
            "target_box"
        )

        if (
            source_box is None
            or target_box is None
        ):
            return self._record({
                "name": (
                    "cat_exploration_pair_"
                    "transfer_failed"
                ),
                "cat": cat.get("name"),
                "intention": (
                    "create_exploration_pair"
                ),
                "pair_id": creation.get(
                    "pair_id"
                ),
                "reason": (
                    "created_pair_boxes_missing"
                ),
                "creation_result": creation,
                "executed": False
            })

        transfer = (
            transfer_system
            .transfer_cat(
                cat=cat,
                source_box_id=source_box.id,
                target_box_id=target_box.id
            )
        )

        if not transfer.get(
            "transferred",
            False
        ):
            cat["state"] = (
                "exploration_pair_created_"
                "but_transfer_failed"
            )

            return self._record({
                "name": (
                    "cat_exploration_pair_"
                    "transfer_failed"
                ),
                "cat": cat.get("name"),
                "intention": (
                    "create_exploration_pair"
                ),
                "pair_id": creation[
                    "pair_id"
                ],
                "source_box_id": (
                    source_box.id
                ),
                "target_box_id": (
                    target_box.id
                ),
                "reason": transfer.get(
                    "reason",
                    "stable_pair_transfer_failed"
                ),
                "creation_result": creation,
                "transfer_result": transfer,
                "pair_preserved": True,
                "executed": False
            })

        exploration_route = None

        if (
            cat.get("current_layer")
            == "quantum_layer"
        ):
            exploration_route = (
                transfer_system
                .start_quantum_exploration_route(
                    cat=cat,
                    pair_id=creation[
                        "pair_id"
                    ]
                )
            )

        mind = cat.setdefault(
            "mind",
            {}
        )

        mind["previous_intention"] = deepcopy(
            intention
        )

        mind["current_intention"] = None

        event = {
            "name": (
                "cat_started_autonomous_"
                "exploration_through_new_pair"
            ),
            "cat": cat.get("name"),
            "intention": (
                "create_exploration_pair"
            ),
            "pair_id": creation[
                "pair_id"
            ],
            "source_box_id": (
                source_box.id
            ),
            "target_box_id": (
                target_box.id
            ),
            "source_layer": creation[
                "source_layer"
            ],
            "target_layer": creation[
                "target_layer"
            ],
            "energy_cost_j": creation[
                "energy_cost_j"
            ],
            "remaining_cat_energy": (
                creation[
                    "remaining_cat_energy"
                ]
            ),
            "creation": {
                "created": True,
                "stable": creation.get(
                    "stable",
                    True
                ),
                "available_to_other_cats": (
                    creation.get(
                        "available_to_other_cats",
                        True
                    )
                )
            },
            "transfer": {
                "transferred": True,
                "pair_remains_stable": (
                    transfer.get(
                        "pair_remains_stable",
                        False
                    )
                ),
                "target_box_consumed": (
                    transfer.get(
                        "target_box_consumed"
                    )
                ),
                "destination_layer": (
                    transfer.get(
                        "target_layer"
                    )
                ),
                "trail": transfer.get(
                    "trail"
                )
            },
            "exploration_route": (
                exploration_route
            ),
            "decision_source": "cat_mind",
            "executed": True
        }

        mind[
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _execute_rest(
        self,
        cat,
        intention
    ):
        previous_state = cat.get(
            "state"
        )

        cat["state"] = (
            "resting_by_own_choice"
        )

        cat.pop(
            "suggested_intent",
            None
        )

        cat.pop(
            "intent",
            None
        )

        cat.pop(
            "active_route_id",
            None
        )

        event = {
            "name": (
                "cat_intention_rest_started"
            ),
            "cat": cat.get("name"),
            "intention": "rest",
            "previous_state": previous_state,
            "state": cat["state"],
            "decision_source": "cat_mind",
            "executed": True
        }

        cat[
            "mind"
        ][
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _defer_intention(
        self,
        cat,
        intention
    ):
        intention_type = intention[
            "type"
        ]

        required_system = (
            self.DEFERRED_INTENTS[
                intention_type
            ]
        )

        cat["state"] = (
            "intention_waiting_for_body_system"
        )

        event = {
            "name": (
                "cat_intention_body_action_deferred"
            ),
            "cat": cat.get("name"),
            "intention": intention_type,
            "target": intention.get(
                "target"
            ),
            "required_system": required_system,
            "decision_preserved": True,
            "executed": False,
            "deferred": True
        }

        cat[
            "mind"
        ][
            "active_body_execution"
        ] = deepcopy(
            event
        )

        return self._record(
            event
        )

    def _record(
        self,
        event
    ):
        stored = deepcopy(
            event
        )

        self.history.append(
            stored
        )

        quantum_events = getattr(
            self.universe,
            "quantum_events",
            None
        )

        if quantum_events is not None:
            quantum_events.append(
                deepcopy(stored)
            )

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None
        )

        if emit_event is not None:
            emit_event(
                deepcopy(stored)
            )

        return event









