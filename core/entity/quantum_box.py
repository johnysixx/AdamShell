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
    def public_state(self):
        return {
            "id": self.id,
            "type": "quantum_box",
            "position": self.position.copy(),
            "state": self.state,
            "content_state": "unresolved",
            "collapsed": self.collapse["collapsed"]
        }
