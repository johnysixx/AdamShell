from core.entity.components import SpatialVector3


class QuantumDieBox:

    def __init__(self, quantum_die):
        self.name = "quantum_die_box"
        self.type = "quantum_container"

        self.edge_length = 1.0
        self.quantum_die = quantum_die

        self._position = SpatialVector3.zero()

        self.state = "quantum_position_unresolved"

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        if not isinstance(position, SpatialVector3):
            raise TypeError(
                "Quantum die box position must be a SpatialVector3 object."
            )
        self._position = position

    def move_to(self, position):
        self.position = position
        self.state = "position_resolved"
        return self.position

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "edge_length": self.edge_length,
            "position": self.position.to_dict(),
            "state": self.state,
            "contains": self.quantum_die.name
        }
