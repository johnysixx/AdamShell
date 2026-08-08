from copy import deepcopy

from cats.cat_knowledge import (
    CatKnowledge
)


class CatIntentionExecutor:

    NAVIGATION_INTENTS = {
        "visit_bar": "return_to_bar",
        "hunt_cronenberg": (
            "hunt_nearest_cronenberg"
        )
    }

    DEFERRED_INTENTS = {
        "explore_box": (
            "box_exploration_body_system"
        ),
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

        # Kočka už se rozhodla ve své mysli.
        # Executor její vůli znovu nehází.
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