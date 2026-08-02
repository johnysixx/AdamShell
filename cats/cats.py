import random

from universe.logger import UniverseLogger
from .memory import CatMemory

class Cats:

    def __init__(self, universe):
        self.universe = universe
        self.cats = []
        self.events = []
        self.tick_count = 0

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

        cat = {
            "name": name,
            "type": "cat",
            "state": "created",
            "color": color,
            "pattern": pattern,
            "eye_color": eye_color,
            "fur_length": fur_length,
            "sex": sex,
            "origin": origin,
            "idea_energy": self.default_idea_energy,
            "size": 1.0,
            "strength": 1.0,
            "cronenbergs_eaten": 0,
            "cronenberg_mass_eaten": 0.0,
            "memory": CatMemory(name),
            "access": self.access_rules,
            "special_traits": []
        }

        self.cats.append(cat)
        self.universe.world["cats"]["cats"] = self.cats

        UniverseLogger.event(f"CAT CREATED: {name}")
        return cat

    def activate_for_cronenberg_overpopulation(
            self,
            cat,
            hunt_quota=10
    ):
        if not isinstance(cat, dict):
            return {
                "result": "invalid_cat",
                "activated": False
            }

        if cat.get("type") != "cat":
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
                "cat": cat.get("name")
            }

        eaten = int(
            cat.get(
                "cronenbergs_eaten",
                0
            )
        )

        hunt_quota = int(hunt_quota)

        if eaten < hunt_quota:
            intent = "hunt_nearest_cronenberg"
        else:
            intent = "return_to_bar"

        cat["state"] = (
            "aware_of_cronenberg_overpopulation"
        )

        cat["suggested_intent"] = intent
        cat["hunt_quota"] = hunt_quota
        cat["overpopulation_response_available"] = True

        event = {
            "name": (
                "cat_activated_for_"
                "cronenberg_overpopulation"
            ),
            "cat": cat.get("name"),
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
        if not isinstance(cat, dict):
            return {
                "name": "cat_navigation_not_offered",
                "result": "invalid_cat",
                "offered": False
            }

        if cat.get("type") != "cat":
            return {
                "name": "cat_navigation_not_offered",
                "result": "not_a_cat",
                "offered": False
            }

        suggested_intent = cat.get(
            "suggested_intent"
        )

        if suggested_intent is None:
            return {
                "name": "cat_navigation_not_offered",
                "result": "no_suggested_intent",
                "cat": cat.get("name"),
                "offered": False
            }

        start_position = cat.get(
            "position"
        )

        if start_position is None:
            return {
                "name": "cat_navigation_not_offered",
                "result": "cat_has_no_position",
                "cat": cat.get("name"),
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
                    cat_id=cat.get("name"),
                    start_position=(
                        start_position
                    ),
                    step_size=step_size
                )
            )

        else:
            return {
                "name": "cat_navigation_not_offered",
                "result": "unsupported_suggested_intent",
                "cat": cat.get("name"),
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
                "cat": cat.get("name"),
                "suggested_intent": suggested_intent,
                "plan": plan,
                "offered": False
            }

        offer = {
            "name": "cat_navigation_offered",
            "cat": cat.get("name"),
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

        cat["navigation_offer"] = dict(
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
        if not isinstance(cat, dict):
            return {
                "name": "cat_navigation_offer_not_accepted",
                "result": "invalid_cat",
                "accepted": False
            }

        offer = cat.get(
            "navigation_offer"
        )

        if offer is None:
            return {
                "name": "cat_navigation_offer_not_accepted",
                "result": "no_navigation_offer",
                "cat": cat.get("name"),
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
                "cat": cat.get("name"),
                "accepted": False
            }

        route = quantum_space.find_cat_route(
            cat.get("name")
        )

        if route is None:
            return {
                "name": "cat_navigation_offer_not_accepted",
                "result": "offered_route_not_found",
                "cat": cat.get("name"),
                "accepted": False
            }

        offer["accepted"] = True

        cat["intent"] = offer[
            "suggested_intent"
        ]

        cat["navigation_offer"] = offer
        cat["active_route_id"] = (
            route.route_id
        )

        route.state = "ready"

        event = {
            "name": "cat_navigation_offer_accepted",
            "cat": cat.get("name"),
            "intent": cat["intent"],
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
        if not isinstance(cat, dict):
            return {
                "name": "cat_navigation_offer_not_declined",
                "result": "invalid_cat",
                "declined": False
            }

        offer = cat.get(
            "navigation_offer"
        )

        if offer is None:
            return {
                "name": "cat_navigation_offer_not_declined",
                "result": "no_navigation_offer",
                "cat": cat.get("name"),
                "declined": False
            }

        quantum_space = getattr(
            self.universe,
            "quantum_space",
            None
        )

        route = (
            quantum_space.find_cat_route(
                cat.get("name")
            )
            if quantum_space is not None
            else None
        )

        if route is not None:
            route.stop_observation()

        offer["accepted"] = False
        offer["declined"] = True

        cat["navigation_offer"] = offer

        cat.pop(
            "intent",
            None
        )

        cat.pop(
            "active_route_id",
            None
        )

        event = {
            "name": "cat_navigation_offer_declined",
            "cat": cat.get("name"),
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
        if not isinstance(cat, dict):
            return {
                "name": (
                    "cat_navigation_decision_failed"
                ),
                "result": "invalid_cat",
                "decided": False
            }

        offer = cat.get(
            "navigation_offer"
        )

        if offer is None:
            return {
                "name": (
                    "cat_navigation_decision_failed"
                ),
                "result": "no_navigation_offer",
                "cat": cat.get("name"),
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
            "cat": cat.get("name"),
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

        cat["last_navigation_decision"] = (
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

    def can_travel(self, cat, via):
            if cat.get("type") != "cat":
                return False

            if not self.access_rules.get("can_access_anywhere", False):
                return False

            allowed_routes = self.access_rules.get("access_via", [])

            return via in allowed_routes

    def emit_event(self, event):
        self.events.append(event)
        UniverseLogger.event(f"CATS EVENT: {event}")

    def tick(self):
        self.tick_count += 1
        UniverseLogger.event(f"CATS TICK {self.tick_count}")
        self._clear_events()

    def _clear_events(self):
        self.events = []


