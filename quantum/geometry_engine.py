class QuantumGeometryEngine:

    def __init__(self):
        self.name = "quantum_geometry_engine"
        self.type = "geometry_engine"

        self.configuration_seed = None
        self.geometry_version = 0

        self.stable_connections = []

    def configure(self, configuration_seed):
        self.configuration_seed = configuration_seed
        self.geometry_version += 1

        print(
            f"QUANTUM GEOMETRY CONFIGURED "
            f"SEED={self.configuration_seed} "
            f"VERSION={self.geometry_version}"
        )

    def terminal_display(self):
        return (
            f"GEOMETRY VERSION: {self.geometry_version} | "
            f"SEED: {self.configuration_seed}"
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "configuration_seed": self.configuration_seed,
            "geometry_version": self.geometry_version,
            "stable_connection_count": len(
                self.stable_connections
            )
        }
