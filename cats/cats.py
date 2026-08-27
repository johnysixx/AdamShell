import random

from universe.logger import UniverseLogger
from .memory import CatMemory
from .reproduction import CatReproduction
from .genotype import CatGenotype
from .cat_learning import CatLearning
from .cat import Cat
from .cat_personality import CatPersonality
from .cat_mind import CatMind
from .cat_intellect import CatIntellect
from .cat_intention_executor import (
    CatIntentionExecutor
)
from .cat_perception import (
    CatPerception
)
from universe.aroma_profile import (
    AromaProfile
)
from .cat_knowledge import (
    CatKnowledge
)
from .cat_need_system import (
    CatNeedSystem
)

class Cats:

    def __init__(self, universe):
        self.universe = universe

        self.universe.cats_layer = self

        self.cats = []
        self.events = []
        self.tick_count = 0

        self.intention_executor = (
            CatIntentionExecutor(
                self
            )
        )

        self.perception = CatPerception(
            self
        )

        self.allowed_colors = [
            "white",
            "black",
            "blue",
            "gray",
            "orange",
            "cream",
            "chocolate",
            "cinnamon",
            "lilac",
            "fawn",
            "tortoiseshell",
            "blue_tortoiseshell",
            "calico"
        ]

        self.allowed_patterns = [
            "solid",
            "tabby",
            "tuxedo",
            "bicolor",
            "tricolor",
            "pointed",
            "smoke",
            "shaded"
        ]

        self.allowed_eye_colors = [
            "blue",
            "green",
            "yellow",
            "gold",
            "amber",
            "orange",
            "copper",
            "hazel",
            "aqua",
            "odd_eyed"
        ]

        self.allowed_fur_lengths = [
            "short",
            "long"
        ]

        self.allowed_sexes = [
            "female",
            "male"
        ]

        self.default_idea_energy = 100

        self.access_rules = {
            "can_access_anywhere": True,
            "access_via": [
                "boxes",
                "cat_doors"
            ]
        }

        self.universe.world["cats"] = {
            "type": "species_layer",
            "state": "created",
            "allowed_colors": self.allowed_colors,
            "allowed_patterns": self.allowed_patterns,
            "allowed_eye_colors": self.allowed_eye_colors,
            "allowed_fur_lengths": self.allowed_fur_lengths,
            "allowed_sexes": self.allowed_sexes,
            "default_idea_energy": self.default_idea_energy,
            "access_rules": self.access_rules,
            "cats": self.cats
        }

        UniverseLogger.boot("CATS CREATED")
        UniverseLogger.boot("CATS ACCESS: anywhere via boxes and cat doors")

    def create_cat(
            self,
            name,
            color,
            fur_length,
            pattern="solid",
            eye_color="green",
            sex="female",
            origin="manual_creation"
    ):
        if color not in self.allowed_colors:
            UniverseLogger.event(f"CAT CREATION DENIED: invalid color {color}")
            return None

        if fur_length not in self.allowed_fur_lengths:
            UniverseLogger.event(f"CAT CREATION DENIED: invalid fur length {fur_length}")
            return None

        if pattern not in self.allowed_patterns:
            UniverseLogger.event(f"CAT CREATION DENIED: invalid pattern {pattern}")
            return None

        if eye_color not in self.allowed_eye_colors:
            UniverseLogger.event(f"CAT CREATION DENIED: invalid eye color {eye_color}")
            return None

        if sex not in self.allowed_sexes:
            UniverseLogger.event(f"CAT CREATION DENIED: invalid sex {sex}")
            return None

        cat = Cat(
            name=name,
            color=color,
            pattern=pattern,
            eye_color=eye_color,
            fur_length=fur_length,
            sex=sex,
            genotype=(
                CatGenotype.create_founder(
                    sex=sex
                )
            ),
            reproduction=(
                CatReproduction.create_state(
                    sex=sex,
                    neutered=False
                )
            ),
            origin=origin,
            idea_energy=(
                self.default_idea_energy
            ),
            memory=CatMemory(
                name
            ),
            access=self.access_rules,
            learning=(
                CatLearning.create_complete_state()
            ),
            personality=(
                CatPersonality.create_state()
            ),
            mind=(
                CatMind.create_state()
            ),
            intellect=(
                CatIntellect.create_state()
            ),
            aroma=(
                AromaProfile.create(
                    identity=f"cat:{name}",
                    components={
                        "cat": 1.0,
                        "fur": 0.80,
                        f"individual_cat:{name}": 2.0
                    },
                    intensity=1.0
                )
            )
        )

        self.cats.append(cat)
        self.universe.world["cats"]["cats"] = self.cats

        UniverseLogger.event(f"CAT CREATED: {name}")
        return cat

    def learn_raspberry_rum_aroma(
            self,
            cat,
            meeting_place
    ):
        raspberry_rum = getattr(
            meeting_place,
            "raspberry_rum",
            None
        )

        if not isinstance(
            raspberry_rum,
            dict
        ):
            return None

        return CatKnowledge.learn_aroma(
            cat=cat,
            identity="raspberry_rum",
            components=raspberry_rum[
                "aroma_profile"
            ],
            source=(
                "direct_raspberry_rum_experience"
            )
        )

    def learn_cat_aroma(
            self,
            observer,
            observed_cat
    ):
        aroma = AromaProfile.current(
            observed_cat.aroma
        )

        return CatKnowledge.learn_aroma(
            cat=observer,
            identity=observed_cat.aroma[
                "identity"
            ],
            components=aroma,
            source=(
                "direct_cat_contact"
            )
        )

    def learn_cronenberg_aroma(
            self,
            cat,
            cronenberg
    ):
        aroma = AromaProfile.current(
            cronenberg.aroma
        )

        return CatKnowledge.learn_aroma(
            cat=cat,
            identity="cronenberg",
            components=aroma,
            source=(
                "direct_cronenberg_encounter"
            )
        )

    def learn_aroma(
            self,
            cat,
            identity,
            components,
            source="direct_experience"
    ):
        return CatKnowledge.learn_aroma(
            cat=cat,
            identity=identity,
            components=components,
            source=source
        )

    def add_surface_aroma(
            self,
            cat,
            source,
            components,
            intensity=1.0,
            decay_rate=0.03
    ):
        return AromaProfile.add_surface(
            profile=cat.aroma,
            source=source,
            components=components,
            intensity=intensity,
            decay_rate=decay_rate
        )

    def current_aroma(
            self,
            cat
    ):
        return AromaProfile.current(
            cat.aroma
        )

    def decay_cat_aroma(
            self,
            cat,
            ticks=1
    ):
        return AromaProfile.decay(
            cat.aroma,
            ticks=ticks
        )

    def activate_for_cronenberg_overpopulation(
            self,
            cat,
            hunt_quota=10
    ):
        if not isinstance(
            cat,
            Cat
        ):
            return {
                "result": "invalid_cat",
                "activated": False
            }

        if cat.type != "cat":
            return {
                "result": "not_a_cat",
                "activated": False
            }

        if not self.can_travel(
            cat,
            via="boxes"
        ):
            return {
                "result": "box_travel_unavailable",
                "activated": False,
                "cat": cat.name
            }

        eaten = int(
            cat.cronenbergs_eaten
        )

        hunt_quota = int(hunt_quota)

        if eaten < hunt_quota:
            intent = "hunt_nearest_cronenberg"
        else:
            intent = "return_to_bar"

        cat.state = (
            "aware_of_cronenberg_overpopulation"
        )

        cat.suggested_intent = intent
        cat.hunt_quota = hunt_quota
        cat.overpopulation_response_available = True

        event = {
            "name": (
                "cat_activated_for_"
                "cronenberg_overpopulation"
            ),
            "cat": cat.name,
            "suggested_intent": intent,
            "cat_access_unchanged": True,
            "cronenbergs_eaten": eaten,
            "hunt_quota": hunt_quota,
            "activated": True
        }

        self.emit_event(event)

        return event

    def offer_navigation_for_suggested_intent(
            self,
            cat,
            cronenbergs=None,
            step_size=None
    ):
        if not isinstance(
            cat,
            Cat
        ):
            return {
                "name": "cat_navigation_not_offered",
                "result": "invalid_cat",
                "offered": False
            }

        if cat.type != "cat":
            return {
                "name": "cat_navigation_not_offered",
                "result": "not_a_cat",
                "offered": False
            }

        suggested_intent = (
            cat.suggested_intent
        )

        if suggested_intent is None:
            return {
                "name": "cat_navigation_not_offered",
                "result": "no_suggested_intent",
                "cat": cat.name,
                "offered": False
            }

        start_position = (
            cat.position
        )

        if start_position is None:
            return {
                "name": "cat_navigation_not_offered",
                "result": "cat_has_no_position",
                "cat": cat.name,
                "suggested_intent": suggested_intent,
                "offered": False
            }

        if not hasattr(
            self.universe,
            "quantum_space"
        ):
            self.universe.enable_quantum_layer()

        quantum_space = (
            self.universe.quantum_space
        )

        if suggested_intent == (
            "hunt_nearest_cronenberg"
        ):
            available_cronenbergs = (
                list(cronenbergs)
                if cronenbergs is not None
                else list(
                    self.universe.cronenbergs
                )
            )

            plan = (
                quantum_space
                .plan_cat_route_to_nearest_huntable_cronenberg(
                    cat=cat,
                    cronenbergs=(
                        available_cronenbergs
                    ),
                    start_position=(
                        start_position
                    ),
                    step_size=step_size
                )
            )

        elif suggested_intent == (
            "return_to_bar"
        ):
            plan = (
                quantum_space
                .plan_cat_route_to_bar(
                    cat_id=cat.name,
                    start_position=(
                        start_position
                    ),
                    step_size=step_size
                )
            )

        elif suggested_intent == (
            "follow_entity"
        ):
            target_id = (
                cat.navigation_target
            )

            recipient_registry = getattr(
                self.universe,
                "cat_recipient_registry",
                None
            )

            if recipient_registry is None:
                return {
                    "name": "cat_navigation_not_offered",
                    "result": "recipient_registry_missing",
                    "cat": cat.name,
                    "suggested_intent": suggested_intent,
                    "offered": False
                }

            recipient = recipient_registry.find(
                target_id
            )

            if recipient is None:
                return {
                    "name": "cat_navigation_not_offered",
                    "result": "recipient_not_found",
                    "cat": cat.name,
                    "navigation_target": target_id,
                    "offered": False
                }

            recipient_layer = recipient.get(
                "current_layer"
            )

            if recipient_layer != cat.current_layer:
                return {
                    "name": "cat_navigation_not_offered",
                    "result": "recipient_in_other_layer",
                    "cat": cat.name,
                    "navigation_target": target_id,
                    "recipient_layer": recipient_layer,
                    "cat_layer": cat.current_layer,
                    "offered": False
                }

            recipient_position = recipient.get(
                "position"
            )

            if recipient_position is None:
                return {
                    "name": "cat_navigation_not_offered",
                    "result": "recipient_has_no_position",
                    "cat": cat.name,
                    "navigation_target": target_id,
                    "offered": False
                }

            plan = (
                quantum_space
                .plan_direct_cat_route(
                    cat_id=cat.name,
                    start_position=start_position,
                    destination_position=(
                        recipient_position
                    ),
                    destination=(
                        f"recipient:{target_id}"
                    ),
                    step_size=step_size
                )
            )

        else:
            return {
                "name": "cat_navigation_not_offered",
                "result": "unsupported_suggested_intent",
                "cat": cat.name,
                "suggested_intent": suggested_intent,
                "offered": False
            }

        route = plan.get(
            "route"
        )

        if route is None:
            return {
                "name": "cat_navigation_not_offered",
                "result": plan.get(
                    "result",
                    "route_not_planned"
                ),
                "cat": cat.name,
                "suggested_intent": suggested_intent,
                "plan": plan,
                "offered": False
            }

        offer = {
            "name": "cat_navigation_offered",
            "cat": cat.name,
            "suggested_intent": (
                suggested_intent
            ),
            "route_id": route.route_id,
            "destination": (
                route.destination
            ),
            "route_step_count": len(
                route.route_steps
            ),
            "accepted": False,
            "offered": True
        }

        cat.navigation_offer = dict(
            offer
        )

        self.emit_event(
            offer
        )

        return {
            **offer,
            "plan": plan,
            "route": route
        }

    def accept_navigation_offer(
            self,
            cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            return {
                "name": "cat_navigation_offer_not_accepted",
                "result": "invalid_cat",
                "accepted": False
            }

        offer = (
            cat.navigation_offer
        )

        if offer is None:
            return {
                "name": "cat_navigation_offer_not_accepted",
                "result": "no_navigation_offer",
                "cat": cat.name,
                "accepted": False
            }

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None
        )

        if quantum_space is None:
            return {
                "name": "cat_navigation_offer_not_accepted",
                "result": "quantum_space_unavailable",
                "cat": cat.name,
                "accepted": False
            }

        route = quantum_space.find_cat_route(
            cat.name
        )

        if route is None:
            return {
                "name": "cat_navigation_offer_not_accepted",
                "result": "offered_route_not_found",
                "cat": cat.name,
                "accepted": False
            }

        offer["accepted"] = True

        cat.intent = offer[
            "suggested_intent"
        ]

        cat.navigation_offer = offer
        cat.active_route_id = (
            route.route_id
        )

        route.state = "ready"

        event = {
            "name": "cat_navigation_offer_accepted",
            "cat": cat.name,
            "intent": cat.intent,
            "route_id": route.route_id,
            "destination": route.destination,
            "accepted": True
        }

        self.emit_event(
            event
        )

        return {
            **event,
            "route": route
        }

    def decline_navigation_offer(
            self,
            cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            return {
                "name": "cat_navigation_offer_not_declined",
                "result": "invalid_cat",
                "declined": False
            }

        offer = (
            cat.navigation_offer
        )

        if offer is None:
            return {
                "name": "cat_navigation_offer_not_declined",
                "result": "no_navigation_offer",
                "cat": cat.name,
                "declined": False
            }

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None
        )

        route = (
            quantum_space.find_cat_route(
                cat.name
            )
            if quantum_space is not None
            else None
        )

        if route is not None:
            route.stop_observation()

        offer["accepted"] = False
        offer["declined"] = True

        cat.navigation_offer = offer

        if hasattr(
            cat,
            "intent"
        ):
            del cat.intent

        if hasattr(
            cat,
            "active_route_id"
        ):
            del cat.active_route_id

        event = {
            "name": "cat_navigation_offer_declined",
            "cat": cat.name,
            "route_id": offer.get(
                "route_id"
            ),
            "destination": offer.get(
                "destination"
            ),
            "declined": True
        }

        self.emit_event(
            event
        )

        return {
            **event,
            "route": route
        }

    def decide_navigation_offer(
            self,
            cat,
            rng=None,
            acceptance_chance=0.70
    ):
        if not isinstance(
            cat,
            Cat
        ):
            return {
                "name": (
                    "cat_navigation_decision_failed"
                ),
                "result": "invalid_cat",
                "decided": False
            }

        offer = (
            cat.navigation_offer
        )

        if offer is None:
            return {
                "name": (
                    "cat_navigation_decision_failed"
                ),
                "result": "no_navigation_offer",
                "cat": cat.name,
                "decided": False
            }

        acceptance_chance = float(
            acceptance_chance
        )

        if not 0.0 <= acceptance_chance <= 1.0:
            raise ValueError(
                "Cat navigation acceptance chance "
                "must be between 0 and 1."
            )

        rng = rng or random

        decision_roll = float(
            rng.random()
        )

        accepted = (
            decision_roll
            < acceptance_chance
        )

        decision = {
            "name": (
                "cat_navigation_offer_decided"
            ),
            "cat": cat.name,
            "route_id": offer.get(
                "route_id"
            ),
            "destination": offer.get(
                "destination"
            ),
            "suggested_intent": offer.get(
                "suggested_intent"
            ),
            "decision_roll": decision_roll,
            "acceptance_chance": (
                acceptance_chance
            ),
            "decision": (
                "accepted"
                if accepted
                else "declined"
            ),
            "decided": True
        }

        cat.last_navigation_decision = (
            dict(decision)
        )

        self.emit_event(
            decision
        )

        if accepted:
            result = (
                self.accept_navigation_offer(
                    cat
                )
            )
        else:
            result = (
                self.decline_navigation_offer(
                    cat
                )
            )

        return {
            **decision,
            "result_event": result,
            "route": result.get(
                "route"
            )
        }

    def observe_cat(
            self,
            cat,
            vision_radius=None
    ):
        return self.perception.observe(
            cat=cat,
            vision_radius=vision_radius
        )

    def think_and_act(
            self,
            cat,
            quantum_roll=None,
            vision_radius=None,
            cronenbergs=None,
            step_size=None
    ):
        from .cat_mind import CatMind

        observations = self.observe_cat(
            cat=cat,
            vision_radius=vision_radius
        )

        if not observations.get(
            "observed",
            False
        ):
            return {
                "name": (
                    "cat_thought_cycle_failed"
                ),
                "cat": getattr(
                    cat,
                    "name",
                    None
                ),
                "observation": observations,
                "completed": False
            }

        decision = CatMind.decide(
            cat=cat,
            observations=observations,
            quantum_roll=quantum_roll
        )

        if not decision.get(
            "selected",
            False
        ):
            return {
                "name": (
                    "cat_thought_cycle_failed"
                ),
                "cat": cat.name,
                "observations": observations,
                "decision": decision,
                "completed": False
            }

        execution = (
            self.execute_cat_intention(
                cat=cat,
                cronenbergs=cronenbergs,
                step_size=step_size
            )
        )

        event = {
            "name": "cat_thought_cycle_completed",
            "cat": cat.name,
            "observations": observations,
            "decision": decision,
            "execution": execution,
            "completed": True
        }

        self.emit_event(
            event
        )

        return event

    def advance_cat_quantum_exploration(
            self,
            cat,
            rng=None
    ):
        transfer_system = getattr(
            self.universe,
            "cat_box_transfer",
            None
        )

        if transfer_system is None:
            return {
                "name": (
                    "cat_quantum_exploration_"
                    "not_advanced"
                ),
                "cat": cat.name,
                "reason": (
                    "cat_box_transfer_unavailable"
                ),
                "advanced": False
            }

        return (
            transfer_system
            .advance_quantum_exploration(
                cat=cat,
                rng=rng
            )
        )

    def advance_cat_quantum_return(
            self,
            cat,
            rng=None
    ):
        transfer_system = getattr(
            self.universe,
            "cat_box_transfer",
            None
        )

        if transfer_system is None:
            return {
                "name": (
                    "cat_quantum_return_"
                    "not_advanced"
                ),
                "cat": cat.name,
                "reason": (
                    "cat_box_transfer_unavailable"
                ),
                "advanced": False
            }

        return (
            transfer_system
            .advance_quantum_return(
                cat=cat,
                rng=rng
            )
        )

    def execute_cat_intention(
            self,
            cat,
            cronenbergs=None,
            step_size=None
    ):
        return (
            self.intention_executor
            .execute_current_intention(
                cat=cat,
                cronenbergs=cronenbergs,
                step_size=step_size
            )
        )

    def can_travel(self, cat, via):
            if cat.type != "cat":
                return False

            if not self.access_rules.get("can_access_anywhere", False):
                return False

            allowed_routes = self.access_rules.get("access_via", [])

            return via in allowed_routes

    def emit_event(self, event):
        self.events.append(event)
        UniverseLogger.event(f"CATS EVENT: {event}")

    def tick(self):
        self._clear_events()
        self.tick_count += 1

        report = {
            "name": "cats_tick_completed",
            "tick": self.tick_count,
            "cats": [],
            "groups": [],
            "errors": [],
            "cronenbergs_created": []
        }

        UniverseLogger.event(
            f"CATS TICK {self.tick_count}"
        )

        # ----------------------------------------------------
        # INDIVIDUAL CATS
        # ----------------------------------------------------

        for cat in list(
            self.cats
        ):
            result = (
                self._run_cat_tick_operation(
                    cat=cat,
                    operation=(
                        self._tick_cat_autonomously
                    )
                )
            )

            report[
                "cats"
            ].append(
                result
            )

            if not result.get(
                "ok",
                True
            ):
                report[
                    "errors"
                ].append(
                    result
                )

                cronenberg_id = result.get(
                    "cronenberg_id"
                )

                if cronenberg_id is not None:
                    report[
                        "cronenbergs_created"
                    ].append(
                        cronenberg_id
                    )

        # ----------------------------------------------------
        # CAT GROUPS
        # ----------------------------------------------------

        group_results = (
            self._tick_groups()
        )

        report[
            "groups"
        ].extend(
            group_results
        )

        for result in group_results:
            if not result.get(
                "ok",
                True
            ):
                report[
                    "errors"
                ].append(
                    result
                )

                cronenberg_id = result.get(
                    "cronenberg_id"
                )

                if cronenberg_id is not None:
                    report[
                        "cronenbergs_created"
                    ].append(
                        cronenberg_id
                    )

        report[
            "ok"
        ] = not report[
            "errors"
        ]

        report[
            "error_count"
        ] = len(
            report[
                "errors"
            ]
        )

        self.emit_event({
            "name": "cats_tick_completed",
            "tick": self.tick_count,
            "cats_processed": len(
                report[
                    "cats"
                ]
            ),
            "groups_processed": len(
                report[
                    "groups"
                ]
            ),
            "error_count": report[
                "error_count"
            ],
            "cronenbergs_created": list(
                report[
                    "cronenbergs_created"
                ]
            )
        })

        return report

    def _tick_cat_autonomously(
        self,
        cat
    ):
        if not getattr(
            cat,
            "active",
            True
        ):
            return {
                "name": (
                    "cat_autonomous_tick_skipped"
                ),
                "cat": cat.name,
                "reason": "inactive",
                "completed": False
            }

        # ----------------------------------------------------
        # ACTIVE QUANTUM RETURN
        #
        # Kocka, ktera uz jde po quantum route,
        # nema ve stejnem ticku delat nove rozhodnuti.
        # ----------------------------------------------------

        quantum_return = getattr(
            cat,
            "quantum_return",
            None
        )

        if (
            isinstance(
                quantum_return,
                dict
            )
            and quantum_return.get(
                "active",
                False
            )
        ):
            result = (
                self.advance_cat_quantum_return(
                    cat
                )
            )

            return {
                "name": (
                    "cat_autonomous_tick_completed"
                ),
                "cat": cat.name,
                "mode": "quantum_return",
                "result": result,
                "completed": True
            }

        # ----------------------------------------------------
        # ACTIVE QUANTUM EXPLORATION
        # ----------------------------------------------------

        quantum_exploration = getattr(
            cat,
            "quantum_exploration",
            None
        )

        if (
            isinstance(
                quantum_exploration,
                dict
            )
            and quantum_exploration.get(
                "active",
                False
            )
        ):
            result = (
                self.advance_cat_quantum_exploration(
                    cat
                )
            )

            return {
                "name": (
                    "cat_autonomous_tick_completed"
                ),
                "cat": cat.name,
                "mode": (
                    "quantum_exploration"
                ),
                "result": result,
                "completed": True
            }

        # ----------------------------------------------------
        # NO PHYSICAL / QUANTUM POSITION
        #
        # Neni to chyba reality.
        # Kocka proste nema odkud pozorovat svet.
        # ----------------------------------------------------

        if getattr(
            cat,
            "position",
            None
        ) is None:
            return {
                "name": (
                    "cat_autonomous_tick_skipped"
                ),
                "cat": cat.name,
                "reason": "no_position",
                "completed": False
            }

        # Needs advance once per autonomous cat tick.
        needs_event = CatNeedSystem.advance(
            cat
        )

        # ----------------------------------------------------
        # PERCEPTION -> MIND -> INTENTION -> ACTION
        #
        # Socialni interakce pak muze prirozene
        # vzniknout z vykonaneho intention,
        # napr. approach_cat -> meet().
        # ----------------------------------------------------

        thought = self.think_and_act(
            cat=cat,
            cronenbergs=getattr(
                self.universe,
                "cronenbergs",
                []
            )
        )

        decision = thought.get(
            "decision",
            {}
        )

        intention_type = (
            decision.get(
                "intention"
            )
            or decision.get(
                "type"
            )
        )

        if intention_type is None:
            current = (
                cat.mind.get(
                    "current_intention"
                )
                or {}
            )

            intention_type = (
                current.get(
                    "type"
                )
            )

        needs_after_action = (
            CatNeedSystem.apply_action(
                cat,
                intention_type
            )
        )

        return {
            "name": (
                "cat_autonomous_tick_completed"
            ),
            "cat": cat.name,
            "mode": "thought_cycle",
            "needs": needs_event,
            "needs_after_action": (
                needs_after_action
            ),
            "thought": thought,
            "completed": bool(
                thought.get(
                    "completed",
                    False
                )
            )
        }

    def _tick_groups(self):
        group_system = getattr(
            self,
            "group_system",
            None
        )

        if group_system is None:
            return []

        from .cat_group_lifecycle_system import (
            CatGroupLifecycleSystem
        )

        lifecycle = getattr(
            self,
            "group_lifecycle_system",
            None
        )

        if (
            lifecycle is None
            or lifecycle.group_system
            is not group_system
        ):
            lifecycle = (
                CatGroupLifecycleSystem(
                    group_system
                )
            )

            self.group_lifecycle_system = (
                lifecycle
            )

        results = []

        for group_id in list(
            group_system.groups
        ):
            result = (
                self._run_group_tick_operation(
                    group_id=group_id,
                    operation=lifecycle.advance
                )
            )

            results.append(
                result
            )

        return results

    def _run_cat_tick_operation(
        self,
        cat,
        operation
    ):
        try:
            value = operation(
                cat
            )

            return {
                "cat": cat.name,
                "ok": True,
                "result": value
            }

        except Exception as error:
            return self._cat_tick_error(
                error=error,
                source_component=(
                    f"cat:{cat.name}"
                ),
                source_operation=(
                    "autonomous_tick"
                ),
                cat_name=cat.name
            )

    def _run_group_tick_operation(
        self,
        group_id,
        operation
    ):
        try:
            value = operation(
                group_id,
                self.cats
            )

            return {
                "group_id": group_id,
                "ok": True,
                "result": value
            }

        except Exception as error:
            return self._cat_tick_error(
                error=error,
                source_component=(
                    f"cat_group:{group_id}"
                ),
                source_operation=(
                    "lifecycle_advance"
                ),
                group_id=group_id
            )

    def _cat_tick_error(
        self,
        error,
        source_component,
        source_operation,
        **context
    ):
        UniverseLogger.event(
            "CATS TICK ERROR: "
            f"SOURCE={source_component}."
            f"{source_operation} "
            f"ERROR={type(error).__name__}: "
            f"{error}"
        )

        cronenberg = None

        create_cronenberg = getattr(
            self.universe,
            "create_cronenberg_from_quantum_error",
            None
        )

        if callable(
            create_cronenberg
        ):
            cronenberg = create_cronenberg(
                error=error,
                source_component=(
                    source_component
                ),
                source_operation=(
                    source_operation
                )
            )

        return {
            **context,
            "ok": False,
            "source_component": (
                source_component
            ),
            "source_operation": (
                source_operation
            ),
            "error_type": type(
                error
            ).__name__,
            "error_message": str(
                error
            ),
            "cronenberg_id": getattr(
                cronenberg,
                "id",
                None
            )
        }

    def _clear_events(self):
        self.events = []


