class QuantumCatRoute:

    def __init__(
            self,
            cat_id,
            route_steps,
            start_position,
            destination="bar_front_door"
    ):
        self.cat_id = cat_id
        self.destination = destination

        self.route_steps = list(route_steps)

        self.start_position = dict(start_position)

        self.state = "observed"
        self.observation_active = True

    def stop_observation(self):
        self.observation_active = False
        self.state = "released"

    @property
    def public_state(self):
        return {
            "type": "quantum_cat_route",
            "cat_id": self.cat_id,
            "destination": self.destination,
            "route_steps": list(self.route_steps),
            "state": self.state,
            "observation_active": self.observation_active
        }
