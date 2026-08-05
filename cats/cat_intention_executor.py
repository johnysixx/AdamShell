from copy import deepcopy


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