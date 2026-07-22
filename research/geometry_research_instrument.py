class GeometryResearchInstrument:

    def __init__(self):
        self.name = "geometry_research_instrument"
        self.type = "research_instrument"

        self.measurements = []

    def measure(self, observable_geometry_state):
        measurement = {
            "geometry_version": (
                observable_geometry_state.get(
                    "geometry_version"
                )
            ),
            "stable_connection_count": (
                observable_geometry_state.get(
                    "stable_connection_count"
                )
            )
        }

        self.measurements.append(
            measurement
        )

        return measurement

    @property
    def last_measurement(self):
        if not self.measurements:
            return None

        return self.measurements[-1]

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "measurement_count": len(
                self.measurements
            ),
            "last_measurement": (
                self.last_measurement
            )
        }
