import random
import uuid

from core.actualization.possibility import Possibility
from core.actualization.potential import Potential


class QuantumBox:

    def __init__(self, rng=None):
        rng = rng or random

        self.id = f"quantum_box_{uuid.uuid4().hex[:8]}"

        self.position = {
            "x": rng.uniform(-1.0, 1.0),
            "y": rng.uniform(-1.0, 1.0),
            "z": rng.uniform(-1.0, 1.0)
        }

        self.state = "superposition"
        self.age_ticks = 0

        # Mal? krabice 1?.
        self.box_class = "1x"

        # Vrstva, ve kter? krabice fyzicky existuje.
        self.current_layer = "quantum_layer"

        # Kvantov? dvoj?e v jin? vrstv?.
        self.quantum_counterpart = {
            "box_id": None,
            "layer": None,
            "paired": False
        }

        # P?enos u? existuj?c? ko?ky.
        self.cat_transfer = {
            "active": False,
            "state": "inactive",
            "cat_name": None,
            "source_box_id": None,
            "target_box_id": None,
            "source_layer": None,
            "target_layer": None,
            "started_tick": None
        }

        # Energie samotn? krabice.
        self.energy = {
            "available": True,
            "consumed": False,
            "purpose": None
        }

        self.content = {
            "possibilities": [
                "empty",
                "cat"
            ],
            "resolved": None
        }

        self.collapse = {
            "collapsed": False,
            "cause": None,
            "observer": None,
            "tick": None
        }

    def pair_with(
            self,
            counterpart
    ):
        if counterpart is self:
            raise ValueError(
                "Quantum box cannot pair with itself."
            )

        if self.box_class != "1x":
            raise ValueError(
                "Only 1x boxes are supported."
            )

        if counterpart.box_class != "1x":
            raise ValueError(
                "Only 1x boxes are supported."
            )

        self.quantum_counterpart.update({
            "box_id": counterpart.id,
            "layer": counterpart.current_layer,
            "paired": True
        })

        counterpart.quantum_counterpart.update({
            "box_id": self.id,
            "layer": self.current_layer,
            "paired": True
        })

        return {
            "name": "quantum_boxes_paired",
            "box_a": self.id,
            "box_b": counterpart.id,
            "layer_a": self.current_layer,
            "layer_b": counterpart.current_layer,
            "paired": True
        }

    def clear_counterpart(self):
        previous = self.quantum_counterpart.copy()

        self.quantum_counterpart.update({
            "box_id": None,
            "layer": None,
            "paired": False
        })

        return previous

    def begin_cat_transfer(
            self,
            cat,
            target_box,
            tick=None
    ):
        if not self.quantum_counterpart["paired"]:
            raise RuntimeError(
                "Source quantum box has no counterpart."
            )

        if (
            self.quantum_counterpart["box_id"]
            != target_box.id
        ):
            raise RuntimeError(
                "Target box is not the paired counterpart."
            )

        if not target_box.energy["available"]:
            raise RuntimeError(
                "Target box has no available energy."
            )

        transfer = {
            "active": True,
            "state": "cat_transfer_superposition",
            "cat_name": cat.get("name"),
            "source_box_id": self.id,
            "target_box_id": target_box.id,
            "source_layer": self.current_layer,
            "target_layer": target_box.current_layer,
            "started_tick": tick
        }

        self.cat_transfer.update(
            transfer
        )

        target_box.cat_transfer.update(
            transfer
        )

        self.state = "cat_transfer_superposition"
        target_box.state = (
            "cat_transfer_superposition"
        )

        return transfer.copy()

    def is_in_cat_transfer_superposition(
            self
    ):
        return bool(
            self.cat_transfer.get(
                "active",
                False
            )
            and self.cat_transfer.get(
                "state"
            )
            == "cat_transfer_superposition"
        )

    def is_visible_to(
            self,
            observer
    ):
        if not self.is_in_cat_transfer_superposition():
            return True

        if isinstance(
            observer,
            dict
        ):
            return observer.get(
                "type"
            ) == "cat"

        return getattr(
            observer,
            "type",
            None
        ) == "cat"

    def cat_observation_state(
            self,
            observer
    ):
        if not self.is_visible_to(
            observer
        ):
            return {
                "visible": False,
                "recognized_as_quantum_box": False,
                "occupied": None
            }

        occupied = (
            self.is_in_cat_transfer_superposition()
        )

        return {
            "visible": True,
            "recognized_as_quantum_box": True,
            "occupied": occupied,
            "occupancy_state": (
                "cat_transfer_occupied"
                if occupied
                else "unoccupied"
            ),
            "occupant_identity_visible": False
        }

    def consume_for_cat_transfer(self):
        self.energy.update({
            "available": False,
            "consumed": True,
            "purpose": "cat_layer_transfer"
        })

        self.state = "consumed"

        return self.energy.copy()

    @property
    def possibilities(self):
        return tuple(self.content["possibilities"])

    def generate_potentials(self, cycle_id):
        if self.collapse["collapsed"]:
            return []

        probability = 1.0 / len(self.possibilities)

        return [
            Potential(
                possibility=Possibility(
                    name=possibility_name,
                    probability=probability,
                    action=lambda result=possibility_name: (
                        self.resolve_state(
                            result=result,
                            cause="actualization",
                            observer="reality",
                            tick=cycle_id
                        )
                    )
                ),
                cycle_id=cycle_id,
                source=self.id,
                context={
                    "type": "quantum_box_collapse",
                    "quantum_box_id": self.id,
                    "result": possibility_name,
                    "exclusive_group": self.id
                }
            )
            for possibility_name in self.possibilities
        ]

    def resolve_state(
            self,
            result,
            cause,
            observer=None,
            tick=None
    ):
        if self.collapse["collapsed"]:
            return self.content["resolved"]

        if result not in self.possibilities:
            raise ValueError(
                f"Unknown quantum box result: {result}"
            )

        self.content["resolved"] = result
        self.state = "collapsed"

        self.collapse["collapsed"] = True
        self.collapse["cause"] = cause
        self.collapse["observer"] = observer
        self.collapse["tick"] = tick

        print(
            f"QUANTUM BOX COLLAPSED: {self.id} "
            f"CAUSE={cause} "
            f"RESULT={result}"
        )

        return {
            "type": "quantum_box_collapsed",
            "quantum_box_id": self.id,
            "result": result,
            "cause": cause,
            "observer": observer,
            "tick": tick
        }

    def collapse_state(
            self,
            cause,
            observer=None,
            tick=None,
            rng=None
    ):
        if self.collapse["collapsed"]:
            return self.content["resolved"]

        rng = rng or random

        result = rng.choice(
            self.possibilities
        )

        event = self.resolve_state(
            result=result,
            cause=cause,
            observer=observer,
            tick=tick
        )

        return event["result"]

    @property
    def public_state(self):
        return {
            "id": self.id,
            "type": "quantum_box",
            "position": self.position.copy(),
            "state": self.state,
            "content_state": (
                "unresolved"
                if not self.collapse["collapsed"]
                else self.content["resolved"]
            ),
            "collapsed": self.collapse["collapsed"],
            "box_class": self.box_class,
            "current_layer": self.current_layer,
            "quantum_counterpart": (
                self.quantum_counterpart.copy()
            ),
            "cat_transfer": (
                self.cat_transfer.copy()
            ),
            "energy": self.energy.copy()
        }
