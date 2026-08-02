import random

from universe.logger import UniverseLogger

from .bartender import Bartender
from .terminals import BarTerminals
from .bar_counter import BarCounter
from .bouncer import Bouncer
from .dice_vial import DiceVial
from .dice_box import DiceBox
from .fridge import BarFridge
from .reservoirs import BarEnergyReservoir, BarEntropyReservoir
from .service_rules import BarServiceRules
from .back_room import BackRoom
from .glass_shelf import GlassShelf
from .bar_entity_policy import BarEntityPolicy
from .bar_geometry_terminal import BarGeometryTerminal
from .back_room_black_box import BackRoomBlackBox
from .lemonade_reservoir import LemonadeReservoir
from .lemonade_signs import LemonadeSigns

class MeetingPlace:

    def __init__(self, universe):
        self.universe = universe
        self.universe.meeting_place = self

        self.entities = []
        self.events = []

        self.cronenberg_area = {
            "state": "lemon_courtyard",
            "location": "behind_bar",
            "tree": True,
            "tree_type": "lemon_tree",
            "lemons_visible": True,
            "bench": True
        }

        self.cronenberg_lemonade_total = 0.0
        self.cronenberg_processing_count = 0
        self.cronenberg_processing_history = []
        self.tick_count = 0
        self.bar_counter = BarCounter()
        self.glass_shelf = GlassShelf()
        self.bar_entity_policy = BarEntityPolicy()

        self.dice_vial = DiceVial()
        self.universe.d20_registry.register(
            self.dice_vial
        )
        self.dice_box = DiceBox()
        self.fridge = BarFridge()
        self.energy_reservoir = BarEnergyReservoir()
        self.entropy_reservoir = BarEntropyReservoir()
        self.lemonade_reservoir = LemonadeReservoir()
        self.lemonade_signs = LemonadeSigns()
        self.terminals = BarTerminals()
        self.geometry_terminal = BarGeometryTerminal()
        self.bouncer = Bouncer()
        self.service_rules = BarServiceRules()
        self.back_room = BackRoom(
            self.universe.universe_registry
        )

        self.back_room_black_box = (
            BackRoomBlackBox()
        )

        self.total_entropy_served_today = 0
        self.total_entropy_served_ever = 0
        self.entropy_terminal = {
            "name": "entropy_terminal",
            "type": "bar_terminal",
            "total_entropy_served_today": self.total_entropy_served_today,
            "total_entropy_served_ever": self.total_entropy_served_ever
        }
        self.bartender = Bartender(
            self.bar_counter.hidden_story_book
        )

        self.access = {
            "from": [
                "eden",
                "library",
                "quantum_layer"
            ],
            "exit_to": [
                "library",
                "quantum_layer"
            ],
            "root_universe": False
        }

        self.permissions = {
            "god": "enter",
            "serpent": "enter",
            "pazuzu": "enter",
            "classical_probe_debug_entity": "enter"
        }

        self.state = {
            "type": "meeting_layer",
            "state": "initialized",
            "access": self.access,
            "permissions": self.permissions,
            "entities": self.entities,
            "bar_counter": self.bar_counter.name,
            "hidden_story_book": self.bar_counter.hidden_story_book.name,
            "bar_cloth": self.bar_counter.bar_cloth,
            "milk_bowl": self.bar_counter.milk_bowl,
            "dice_vial": self.dice_vial.public_state,
            "dice_box": self.dice_box.public_state,
            "fridge": self.fridge.public_state,
            "energy_reservoir": self.energy_reservoir.public_state,
            "entropy_reservoir": self.entropy_reservoir.public_state,
            "geometry_terminal": self.geometry_terminal.public_state,
            "back_room": self.back_room.public_state,
            "back_room_black_box": (
                self.back_room_black_box.public_state
            ),
            "terminals": self.terminals.terminals,
            "bouncer": self.bouncer.name,
            "service_rules": "bar_service_rules",
            "entropy_terminal": self.entropy_terminal,
            "bartender": self.bartender.name
        }

        self.universe.world["meeting_place"] = self.state

        UniverseLogger.boot("MEETING PLACE INITIALIZED")

    def can_enter(self, entity_name):
        return self.permissions.get(entity_name) == "enter"

    def observe_lemon_courtyard(self, observer_role):
        staff_roles = {
            "bartender",
            "bouncer",
            "bar_staff"
        }

        pen = getattr(self, "cronenberg_pen", None)

        public_view = {
            "name": "lemon_courtyard",
            "location": "behind_bar",
            "tree": True,
            "tree_type": "lemon_tree",
            "lemons_visible": True,
            "bench": True,
            "assumed_lemonade_source": "lemons_from_tree",
            "cronenberg_pen_visible": False
        }

        if observer_role not in staff_roles:
            return public_view

        staff_view = dict(public_view)
        staff_view["cronenberg_pen_visible"] = pen is not None
        staff_view["cronenberg_pen"] = (
            pen.get_status()
            if pen is not None
            else None
        )
        staff_view["actual_lemonade_source"] = (
            "cronenberg_processing"
        )

        return staff_view

    def create_cronenberg_pen_area(self):
        self.cronenberg_area = {
            "state": "lemon_courtyard_with_hidden_pen",
            "location": "behind_bar",
            "tree": True,
            "bench": True
        }

        UniverseLogger.event(
            "A HIDDEN CRONENBERG PEN IS CREATED BEHIND THE LEMON COURTYARD"
        )

    def restore_cronenberg_clearing(self):
        if hasattr(self, "cronenberg_pen"):
            del self.cronenberg_pen

        self.cronenberg_area = {
            "state": "lemon_courtyard",
            "location": "behind_bar",
            "tree": True,
            "tree_type": "lemon_tree",
            "lemons_visible": True,
            "bench": True
        }

        UniverseLogger.event(
            "HIDDEN CRONENBERG PEN DISAPPEARS; LEMON COURTYARD REMAINS UNCHANGED"
        )

    def add_entity(self, entity):
        entity_name = self._get_entity_name(entity)

        if self._is_cat(entity):
            self.bar_counter.red_button.clear_alarm()

        if not self.bouncer.can_enter(entity):
            UniverseLogger.event(f"MEETING PLACE ENTRY DENIED BY BOUNCER: {entity_name}")

            entity_type = (
                entity.get("type")
                if isinstance(entity, dict)
                else getattr(entity, "type", None)
            )

            if entity_type == "cronenberg":
                if not hasattr(self, "cronenberg_pen"):
                    from .cronenberg_pen import CronenbergPen
                    self.cronenberg_pen = CronenbergPen(self.universe)
                    self.create_cronenberg_pen_area()

                self.cronenberg_pen.add_cronenberg(entity)
                return

            react = getattr(entity, "react", None)
            if callable(react):
                react(
                    universe=self.universe,
                    event="entry_denied",
                    source="bouncer"
                )

            return

        self.bartender.prepare_for_guest()

        self.entities.append(entity)
        if isinstance(entity, dict):
            entity["current_layer"] = "meeting_place"
        else:
            entity.current_layer = "meeting_place"
            entity.location = "meeting_place"
        self.universe.world["meeting_place"]["entities"] = self.entities

        UniverseLogger.event(f"MEETING PLACE: entity joined {entity_name}")
        self.emit_event(f"{entity_name} arrived at the bar")
        if self._is_cat(entity):
            self.universe.statistics.record_cat_arrived()
            self.geometry_terminal.cat_arrived(entity_name)

            if self.bartender.knows_guest(entity_name):
                self.bartender.guest_arrives(entity_name)
            else:
                self.handle_cat_after_entry(entity)
                self.bartender.remember_guest(entity_name)
        else:
            self.bartender.guest_arrives(entity_name)

    def emit_event(self, event):
        self.events.append(event)

        self.back_room_black_box.record(
            event=event,
            source="meeting_place",
            tick=self.tick_count
        )

        self.bartender.observe_event(event)
        self.show_bar_story_count()

        UniverseLogger.event(f"MEETING PLACE EVENT: {event}")

    def guest_asks_about_dice_vial(self, guest_name):
        self.emit_event(f"{guest_name} asked about the dice vial")
        self.bartender.answer_about_dice_vial(guest_name)

    def handle_cat_created(self, cat_id):
        self.geometry_terminal.cat_detected(cat_id)
        self.bar_counter.red_button.activate_alarm()

    def handle_cat_after_entry(self, cat):
        self.serve_cat_milk(cat)

    def serve_cat_milk(self, cat):
        cat_name = self._get_entity_name(cat)

        milk = self.fridge.get_item("milk")
        milk_bowl = self.bar_counter.milk_bowl

        if milk is None:
            self.emit_event(f"{cat_name} could not be served milk because milk was missing")
            return

        self.bartender.serve_without_order(
            cat_name,
            milk,
            milk_bowl
        )
        self.emit_event(f"{cat_name} drinks milk at the bar")

    def welcome_cat_d20(
        self,
        name="cat_d20"
    ):
        existing = next(
            (
                cat
                for cat in getattr(
                    getattr(
                        self.universe,
                        "cats_layer",
                        None
                    ),
                    "cats",
                    []
                )
                if cat.get("name") == name
            ),
            None
        )

        if existing is not None:
            return {
                "name": "cat_d20_already_present",
                "cat": existing,
                "box": getattr(
                    self,
                    "cat_d20_box",
                    None
                ),
                "created": False
            }

        manifestation = (
            self.universe.manifest_cat(
                name=name,
                source="cat_d20_arrival",
                position={
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                },
                color="black",
                fur_length="short",
                pattern="solid",
                eye_color="gold",
                sex="female"
            )
        )

        cat = manifestation["cat"]

        if not hasattr(
            self,
            "cat_d20_secret_history"
        ):
            self.cat_d20_secret_history = []

        cat["special_traits"].extend([
            "d20_cat",
            "born_as_cat_d20",
            "secret_probability_sense"
        ])

        cat["state"] = "arrived_at_bar"
        cat["current_layer"] = (
            "meeting_place"
        )

        cat["cat_d20"] = {
            "is_cat": True,
            "is_die": False,
            "sides": 20,
            "roll_method": (
                "turns_herself_in_box"
            ),
            "can_be_thrown": False,
            "visibility": (
                "appears_to_be_a_small_cat"
            )
        }

        self.add_entity(
            cat
        )

        cat_box = (
            self.place_cat_d20_box(
                cat
            )
        )

        event = {
            "name": "cat_d20_welcomed_at_bar",
            "cat": cat["name"],
            "milk_served": (
                self.bar_counter
                .milk_bowl
                .get("contains")
                == "milk"
            ),
            "box": cat_box["name"],
            "box_location": (
                cat_box["location"]
            ),
            "cat_entered_box": True,
            "tick": getattr(
                self.universe,
                "universe_tick",
                0
            )
        }

        self.emit_event(
            event
        )

        UniverseLogger.event(
            "CAT D20 ARRIVED AS A CAT, "
            "DRANK MILK, AND ENTERED "
            "HER OWN BOX ON THE BAR"
        )

        return {
            "name": (
                "cat_d20_arrival_completed"
            ),
            "cat": cat,
            "entity": manifestation[
                "entity"
            ],
            "box": cat_box,
            "event": event,
            "created": True
        }

    def turn_cat_d20_in_box(
        self,
        rng=None
    ):
        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        if cats_layer is None:
            return {
                "name": "cat_d20_turn_failed",
                "result": "cats_layer_missing",
                "turned": False
            }

        cat = next(
            (
                candidate
                for candidate in cats_layer.cats
                if "d20_cat" in candidate.get(
                    "special_traits",
                    []
                )
            ),
            None
        )

        if cat is None:
            return {
                "name": "cat_d20_turn_failed",
                "result": "cat_d20_missing",
                "turned": False
            }

        box = getattr(
            self,
            "cat_d20_box",
            None
        )

        if box is None:
            return {
                "name": "cat_d20_turn_failed",
                "result": "cat_d20_box_missing",
                "cat": cat["name"],
                "turned": False
            }

        if box.get(
            "occupied_by"
        ) != cat["name"]:
            return {
                "name": "cat_d20_turn_failed",
                "result": "cat_d20_not_in_box",
                "cat": cat["name"],
                "turned": False
            }

        rng = rng or random

        value = int(
            rng.randint(
                1,
                20
            )
        )

        cat_d20_state = cat[
            "cat_d20"
        ]

        previous_value = (
            cat_d20_state.get(
                "current_value"
            )
        )

        turn_count = int(
            cat_d20_state.get(
                "turn_count",
                0
            )
        ) + 1

        turn_event = {
            "name": "cat_d20_turned_in_box",
            "cat": cat["name"],
            "box": box["name"],
            "previous_value": (
                previous_value
            ),
            "value": value,
            "turn_number": turn_count,
            "turned_by": "herself",
            "was_thrown": False,
            "visibility": "secret_cat_event",
            "tick": getattr(
                self.universe,
                "universe_tick",
                0
            ),
            "turned": True
        }

        cat_d20_state[
            "current_value"
        ] = value

        cat_d20_state[
            "turn_count"
        ] = turn_count

        cat_d20_state.setdefault(
            "turn_history",
            []
        ).append(
            dict(turn_event)
        )

        cat[
            "state"
        ] = "turned_in_cat_d20_box"

        box[
            "last_cat_d20_value"
        ] = value

        box[
            "turn_count"
        ] = turn_count

        if not hasattr(
            self,
            "cat_d20_secret_history"
        ):
            self.cat_d20_secret_history = []

        self.cat_d20_secret_history.append(
            dict(turn_event)
        )

        self.universe.quantum_events.append(
            dict(turn_event)
        )

        UniverseLogger.event(
            "CAT D20 SECRET ROTATION RECORDED"
        )

        interpretation = (
            self.interpret_cat_d20_value(
                value
            )
        )

        turn_event["interpretation"] = (
            interpretation
        )

        return turn_event

    def cat_d20_prepare_pazuzu_profile(
        self
    ):
        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        if cats_layer is None:
            return {
                "name": (
                    "cat_d20_pazuzu_profile_failed"
                ),
                "result": "cats_layer_missing",
                "prepared": False
            }

        cat_d20 = next(
            (
                cat
                for cat in cats_layer.cats
                if "d20_cat" in cat.get(
                    "special_traits",
                    []
                )
            ),
            None
        )

        if cat_d20 is None:
            return {
                "name": (
                    "cat_d20_pazuzu_profile_failed"
                ),
                "result": "cat_d20_missing",
                "prepared": False
            }

        base_profile = {
            "color": "black",
            "fur_length": "short",
            "pattern": "solid",
            "eye_color": "green",
            "sex": "female"
        }

        if not hasattr(
            self,
            "cat_d20_canonical_profile_counts"
        ):
            self.cat_d20_canonical_profile_counts = {}

        profile_key = (
            base_profile["color"],
            base_profile["fur_length"],
            base_profile["pattern"],
            base_profile["eye_color"],
            base_profile["sex"]
        )

        occurrence = (
            self.cat_d20_canonical_profile_counts.get(
                profile_key,
                0
            )
            + 1
        )

        self.cat_d20_canonical_profile_counts[
            profile_key
        ] = occurrence

        if occurrence == 1:
            target_name = "pazuzu"
            profile = dict(
                base_profile
            )
            all_dice_rotation_requested = False

        elif occurrence == 2:
            target_name = "gib"
            profile = dict(
                base_profile
            )
            profile[
                "fur_length"
            ] = "long"
            all_dice_rotation_requested = True

        else:
            target_name = None
            profile = dict(
                base_profile
            )
            all_dice_rotation_requested = False

        event = {
            "name": (
                "cat_d20_prepared_"
                "canonical_pazuzu_profile"
            ),
            "cat": cat_d20["name"],
            "profile": dict(
                profile
            ),
            "base_profile": dict(
                base_profile
            ),
            "profile_occurrence": occurrence,
            "target_name": target_name,
            "all_dice_rotation_requested": (
                all_dice_rotation_requested
            ),
            "mode": "canonical_turn",
            "random": False,
            "prepared": (
                target_name is not None
            ),
            "visibility": "secret_cat_event",
            "tick": getattr(
                self.universe,
                "universe_tick",
                0
            )
        }

        cat_d20["cat_d20"][
            "canonical_target"
        ] = target_name

        cat_d20["cat_d20"][
            "canonical_profile"
        ] = dict(
            profile
        )

        if not hasattr(
            self,
            "cat_d20_secret_history"
        ):
            self.cat_d20_secret_history = []

        self.cat_d20_secret_history.append(
            dict(event)
        )

        self.universe.quantum_events.append(
            dict(event)
        )

        UniverseLogger.event(
            "CAT D20 CANONICAL ROTATION "
            "FOR PAZUZU RECORDED"
        )

        return event

    def manifest_gib_from_cat_d20(
        self,
        prepared_event
    ):
        if not isinstance(
            prepared_event,
            dict
        ):
            return {
                "name": "gib_manifestation_failed",
                "result": "invalid_prepared_event",
                "created": False
            }

        if prepared_event.get(
            "target_name"
        ) != "gib":
            return {
                "name": "gib_manifestation_failed",
                "result": "prepared_target_is_not_gib",
                "created": False
            }

        if prepared_event.get(
            "profile_occurrence"
        ) != 2:
            return {
                "name": "gib_manifestation_failed",
                "result": "invalid_profile_occurrence",
                "created": False
            }

        profile = dict(
            prepared_event.get(
                "profile",
                {}
            )
        )

        required_fields = {
            "color",
            "fur_length",
            "pattern",
            "eye_color",
            "sex"
        }

        if not required_fields.issubset(
            profile
        ):
            return {
                "name": "gib_manifestation_failed",
                "result": "incomplete_gib_profile",
                "created": False
            }

        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        existing = next(
            (
                cat
                for cat in (
                    cats_layer.cats
                    if cats_layer is not None
                    else []
                )
                if cat.get("name") == "gib"
            ),
            None
        )

        if existing is not None:
            return {
                "name": "gib_already_exists",
                "cat": existing,
                "created": False
            }

        manifestation = (
            self.universe.manifest_cat(
                name="gib",
                source=(
                    "cat_d20_second_"
                    "canonical_profile"
                ),
                color=profile["color"],
                fur_length=profile[
                    "fur_length"
                ],
                pattern=profile["pattern"],
                eye_color=profile[
                    "eye_color"
                ],
                sex=profile["sex"]
            )
        )

        if manifestation is None:
            return {
                "name": "gib_manifestation_failed",
                "result": "manifest_cat_failed",
                "created": False
            }

        gib = manifestation["cat"]

        gib["special_traits"].extend([
            "gib",
            "pazuzu_profile_echo",
            "second_canonical_cat"
        ])

        gib["canonical_origin"] = {
            "base_profile": dict(
                prepared_event[
                    "base_profile"
                ]
            ),
            "mutation": {
                "fur_length": {
                    "from": "short",
                    "to": "long"
                }
            },
            "profile_occurrence": 2,
            "created_by": "cat_d20"
        }

        event = {
            "name": "gib_manifested",
            "cat": gib["name"],
            "profile": dict(
                profile
            ),
            "profile_occurrence": 2,
            "all_dice_rotation_requested": (
                prepared_event.get(
                    "all_dice_rotation_requested",
                    False
                )
            ),
            "created": True,
            "visibility": "secret_cat_event",
            "tick": getattr(
                self.universe,
                "universe_tick",
                0
            )
        }

        if not hasattr(
            self,
            "cat_d20_secret_history"
        ):
            self.cat_d20_secret_history = []

        self.cat_d20_secret_history.append(
            dict(event)
        )

        self.universe.quantum_events.append(
            dict(event)
        )

        UniverseLogger.event(
            "GIB MANIFESTED FROM THE SECOND "
            "CANONICAL CAT D20 PROFILE"
        )

        return {
            **event,
            "cat": gib,
            "entity": manifestation[
                "entity"
            ]
        }

    def trigger_pazuzu_birth_dice_resonance(
        self,
        rng=None
    ):
        existing_event = getattr(
            self,
            "pazuzu_birth_dice_resonance_event",
            None
        )

        if existing_event is not None:
            return {
                **existing_event,
                "already_triggered": True
            }

        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        cat_d20 = next(
            (
                cat
                for cat in (
                    cats_layer.cats
                    if cats_layer is not None
                    else []
                )
                if "d20_cat" in cat.get(
                    "special_traits",
                    []
                )
            ),
            None
        )

        if cat_d20 is None:
            return {
                "name": (
                    "pazuzu_birth_dice_"
                    "resonance_failed"
                ),
                "result": "cat_d20_missing",
                "triggered": False
            }

        quantum_d20_result = (
            self.universe
            .quantum_die
            .roll(
                rng=rng
            )
        )

        cat_d20_result = (
            self.turn_cat_d20_in_box(
                rng=rng
            )
        )

        dice_vial_result = (
            self.dice_vial.roll(
                rng=rng
            )
        )

        dice_box_result = (
            self.dice_box
            .rotate_random_die(
                rng=rng
            )
        )

        event = {
            "name": (
                "pazuzu_birth_dice_resonance"
            ),
            "quantum_d20": (
                quantum_d20_result
            ),
            "cat_d20": (
                cat_d20_result
            ),
            "dice_vial": (
                dice_vial_result
            ),
            "dice_box": (
                dice_box_result
            ),
            "triggered": True,
            "visibility": (
                "secret_multiverse_event"
            ),
            "tick": getattr(
                self.universe,
                "universe_tick",
                0
            )
        }

        if not hasattr(
            self,
            "cat_d20_secret_history"
        ):
            self.cat_d20_secret_history = []

        self.cat_d20_secret_history.append(
            dict(event)
        )

        self.universe.quantum_events.append(
            dict(event)
        )

        self.pazuzu_birth_dice_resonance_event = (
            dict(event)
        )

        UniverseLogger.event(
            "PAZUZU BIRTH DICE RESONANCE "
            "RECORDED"
        )

        return event

    def interpret_cat_d20_value(
        self,
        value
    ):
        value = int(value)

        if value < 1 or value > 20:
            raise ValueError(
                "CatD20 value must be between 1 and 20."
            )

        if value <= 14:
            meaning = "accept_navigation_offer"
        elif value <= 18:
            meaning = "decline_navigation_offer"
        elif value == 19:
            meaning = "cat_does_something_else"
        else:
            meaning = "cat_d20_surge"

        return {
            "name": "cat_d20_value_interpreted",
            "value": value,
            "meaning": meaning
        }

    def place_cat_d20_box(
        self,
        cat
    ):
        if not isinstance(cat, dict):
            raise TypeError(
                "Cat D20 box requires a cat."
            )

        if "d20_cat" not in cat.get(
            "special_traits",
            []
        ):
            raise ValueError(
                "This box is reserved for Cat D20."
            )

        existing_box = getattr(
            self,
            "cat_d20_box",
            None
        )

        if existing_box is not None:
            existing_box[
                "occupied_by"
            ] = cat["name"]

            cat["cat_d20_box"] = (
                existing_box
            )

            return existing_box

        self.cat_d20_box = {
            "name": "cat_d20_box",
            "type": "cat_box",
            "location": "on_bar_counter",
            "state": "occupied",
            "material": "wood",
            "size": "kitten_sized",
            "purpose": (
                "safe_place_for_cat_d20_"
                "to_sleep_and_turn"
            ),
            "occupied_by": cat["name"],
            "access": {
                "cats": True,
                "bartender": (
                    "may_place_and_clean"
                ),
                "guests": (
                    "look_but_do_not_touch"
                )
            },
            "throwable": False
        }

        cat["cat_d20_box"] = (
            self.cat_d20_box
        )

        cat["state"] = (
            "resting_in_cat_d20_box"
        )

        self.universe.world[
            "meeting_place"
        ]["cat_d20_box"] = (
            self.cat_d20_box
        )

        UniverseLogger.event(
            "BARTENDER PLACES A SMALL WOODEN "
            "BOX ON THE BAR FOR CAT D20"
        )

        UniverseLogger.event(
            "CAT D20 ENTERS HER BOX"
        )

        return self.cat_d20_box

    def sync_entropy_terminal_to_world(self):
        self.entropy_terminal["total_entropy_served_today"] = (
            self.total_entropy_served_today
        )
        self.entropy_terminal["total_entropy_served_ever"] = (
            self.total_entropy_served_ever
        )

        self.universe.world["meeting_place"]["entropy_terminal"] = (
            self.entropy_terminal
        )

    def sync_reservoirs_to_world(self):
        self.universe.world["meeting_place"]["energy_reservoir"] = (
            self.energy_reservoir.public_state
        )
        self.universe.world["meeting_place"]["entropy_reservoir"] = (
            self.entropy_reservoir.public_state
        )

    def add_bar_energy(self, source, amount_j):
        event = self.energy_reservoir.add_energy(source, amount_j)
        self.sync_reservoirs_to_world()
        self.emit_event(f"bar energy increased from {source}")
        return event

    def add_bar_entropy(self, source, amount_units):
        event = self.entropy_reservoir.add_entropy(source, amount_units)
        self.sync_reservoirs_to_world()
        self.emit_event(f"bar entropy increased from {source}")
        return event

    def serve_lemonade(self, entity, location=None):
        entity_name = self._get_entity_name(entity)

        if location is None:
            location = getattr(
                entity,
                "location",
                "outside_bar"
            )

        event = self.lemonade_reservoir.serve(
            drinker_name=entity_name,
            location=location
        )

        if event is None:
            return None

        self.dice_vial.roll()

        self.lemonade_signs.sync_with_reservoir(
            self.lemonade_reservoir
        )

        self.emit_event(
            f"{entity_name} drinks free lemonade at {location}"
        )

        return {
            "lemonade_event": event
        }

    def serve_energy(self, entity):
        from universe.pre_cosmic_rules import ENERGY_SERVING_J

        entity_name = self._get_entity_name(entity)
        entity_type = self._get_entity_type(entity)

        if entity_type not in ["god", "idea_entity"]:
            self.emit_event(f"{entity_name} could not be served energy")
            return None

        try:
            reservoir_event = self.energy_reservoir.spend_energy(
                f"energy_serving_for_{entity_name}",
                ENERGY_SERVING_J
            )
        except ValueError:
            self.sync_reservoirs_to_world()
            self.emit_event(f"{entity_name} could not be served energy because bar energy was missing")
            return None

        service_effect = self.service_rules.apply_energy_drink(entity)

        self.sync_reservoirs_to_world()
        self.emit_event(f"{entity_name} drinks energy at the bar")
        self.emit_event(f"{entity_name} energy drink effect applied")

        return {
            "reservoir_event": reservoir_event,
            "service_effect": service_effect
        }

    def quantum_entropy_tick(self, rng=None):
        event = self.entropy_reservoir.quantum_tick(rng)
        self.sync_reservoirs_to_world()
        self.emit_event("quantum entropy tick was stored in the bar")
        return event

    def serve_entropy(self, entity):
        entity_name = self._get_entity_name(entity)
        entity_type = self._get_entity_type(entity)

        if entity_type not in ["god", "idea_entity"]:
            self.emit_event(f"{entity_name} could not be served entropy")
            return None

        event = self.entropy_reservoir.serve_entropy(
            self.energy_reservoir,
            entity_name
        )

        self.sync_reservoirs_to_world()

        if event is None:
            self.emit_event(f"{entity_name} could not be served entropy")
            return None

        self.total_entropy_served_today += 1
        self.total_entropy_served_ever += 1
        self.sync_entropy_terminal_to_world()

        if self.total_entropy_served_ever % 10 == 0:
            secret_event = self.dice_vial.roll()

            if secret_event["quantum_tick_requested"]:
                self.quantum_entropy_tick()

            if secret_event["box_created"]:
                self.universe.create_quantum_box()



        effect = self.service_rules.apply_entropy_drink(
            entity,
            event.get("entity_energy_gain_j", 0.0)
        )

        self.emit_event(f"{entity_name} drinks entropy at the bar")
        self.emit_event(f"{entity_name} entropy drink effect applied")

        return {
            "reservoir_event": event,
            "service_effect": effect
        }

    def tick(self):
        self.tick_count += 1
        UniverseLogger.event(f"MEETING PLACE TICK {self.tick_count}")
        self.bartender.idle_work()

        cronenberg_pen = getattr(self, "cronenberg_pen", None)
        if cronenberg_pen is not None:
            cronenberg_pen.tick()
        self._clear_events()

    def show_library_book_count(self, library):
        return self.terminals.show_book_count(library)

    def show_book_search_terminal(self):
        return self.terminals.show_book_search_placeholder()

    def show_random_library_excerpt(self, library):
        return self.terminals.show_random_excerpt(library)

    def show_bar_story_count(self):
        return self.terminals.show_bar_story_count(
            self.bar_counter
        )


    def show_cronenberg_pen_terminal(self):
        return self.back_room.cronenberg_pen_terminal.display(self)

    def _clear_events(self):
        self.events = []

    def ask_bartender_about_dice_box(self, entity=None):
        return self.dice_box.answer_about_contents()

    def ask_bartender_about_d20(self, entity=None):
        return self.dice_box.answer_about_d20()

    def _get_entity_name(self, entity):
        if isinstance(entity, dict):
            return entity.get("name")

        return getattr(entity, "name", None)

    def _get_entity_type(self, entity):
        if isinstance(entity, dict):
            return entity.get("type")

        return getattr(entity, "type", None)

    def _is_cat(self, entity):
        if isinstance(entity, dict):
            return entity.get("type", None) == "cat"

        return getattr(entity, "type", None) == "cat"

    def process_interactions(self):
        if len(self.entities) < 2:
            return

        energy_entities = [
            entity for entity in self.entities
            if hasattr(entity, "energy")
        ]

        if len(energy_entities) < 2:
            return

        sorted_entities = sorted(
            energy_entities,
            key=lambda entity: entity.energy,
            reverse=True
        )

        a = sorted_entities[0]
        b = sorted_entities[-1]

        transfer = 0.5

        a.energy -= transfer
        b.energy += transfer

        self.emit_event(f"{a.name} -> {b.name} energy transfer {transfer}")
