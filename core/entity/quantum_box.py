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
            "content_state": "unresolved",
            "collapsed": self.collapse["collapsed"]
        }
