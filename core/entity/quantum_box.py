import random
import uuid


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

        self.content["resolved"] = rng.choice([
            "empty",
            "cat"
        ])

        self.state = "collapsed"

        self.collapse["collapsed"] = True
        self.collapse["cause"] = cause
        self.collapse["observer"] = observer
        self.collapse["tick"] = tick

        print(
            f"QUANTUM BOX COLLAPSED: {self.id} "
            f"CAUSE={cause} "
            f"RESULT={self.content['resolved']}"
        )

        return self.content["resolved"]

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
