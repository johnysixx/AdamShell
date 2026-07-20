class QuantumDieBox:

    def __init__(self, quantum_die):
        self.name = "quantum_die_box"
        self.type = "quantum_container"

        self.edge_length = 1.0
        self.quantum_die = quantum_die

        self.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        self.state = "quantum_position_unresolved"

    def move_to(self, position):
        self.position = {
            "x": float(position["x"]),
            "y": float(position["y"]),
            "z": float(position["z"])
        }

        self.state = "position_resolved"

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "edge_length": self.edge_length,
            "position": self.position.copy(),
            "state": self.state,
            "contains": self.quantum_die.name
        }
