import uuid

class QuantumCatRoute:

    def __init__(
        self,
        cat_id,
        route_steps,
        start_position,
        destination="bar_front_door"
    ):
        self.route_id = (
            f"cat_route_"
            f"{uuid.uuid4().hex[:8]}"
        )

        self.cat_id = cat_id
        self.destination = destination

        self.route_steps = [
            dict(step)
            for step in route_steps
        ]

        self.start_position = dict(
            start_position
        )

        self.current_step_index = 0
        self.current_position = dict(
            self.start_position
        )

        self.detours = []
        self.encounters = []

        self.memory_started = False

        self.state = "observed"
        self.observation_active = True

    @property
    def next_position(self):
        if (
            self.current_step_index
            >= len(self.route_steps)
        ):
            return None

        return dict(
            self.route_steps[
                self.current_step_index
            ]
        )

    @property
    def has_arrived(self):
        return self.next_position is None

    def position_matches(
        self,
        position,
        tolerance=0.001
    ):
        next_position = self.next_position

        if next_position is None:
            return False

        return all(
            abs(
                float(next_position[axis])
                - float(position[axis])
            ) <= tolerance
            for axis in ("x", "y", "z")
        )

    def advance(self):
        next_position = self.next_position

        if next_position is None:
            self.state = "arrived"
            self.stop_observation()
            return None

        self.current_position = dict(
            next_position
        )

        self.current_step_index += 1



        if self.has_arrived:
            self.state = "arrived"
            self.stop_observation()
        else:
            self.state = "travelling"

        return dict(
            self.current_position
        )

    def detour_count_for(self, blocked_position):
        if blocked_position is None:
            return 0

        blocked_position = dict(
            blocked_position
        )

        return sum(
            1
            for detour in self.detours
            if detour.get(
                "blocked_position"
            ) == blocked_position
        )

    def make_minimal_detour(
        self,
        blocked_position,
        clearance=0.25
    ):
        blocked_position = dict(
            blocked_position
        )

        detour_position = {
            "x": float(
                blocked_position["x"]
            ),
            "y": float(
                blocked_position["y"]
            ) + float(clearance),
            "z": float(
                blocked_position["z"]
            )
        }

        self.detours.append({
            "blocked_position": (
                blocked_position
            ),
            "detour_position": (
                dict(detour_position)
            ),
            "returns_to_original_route": True,
            "destination": self.destination
        })

        self.current_position = dict(
            detour_position
        )

        self.state = "avoiding_obstacle"

        return dict(
            detour_position
        )

    def record_encounter(
        self,
        encounter
    ):
        self.encounters.append(
            dict(encounter)
        )

        return encounter

    def stop_observation(self):
        self.observation_active = False
        self.state = "released"

    @property
    def public_state(self):
        return {
            "type": "quantum_cat_route",
            "route_id": self.route_id,
            "cat_id": self.cat_id,
            "destination": self.destination,
            "route_steps": list(
                self.route_steps
            ),
            "start_position": dict(
                self.start_position
            ),
            "current_position": dict(
                self.current_position
            ),
            "current_step_index": (
                self.current_step_index
            ),
            "next_position": (
                self.next_position
            ),
            "has_arrived": self.has_arrived,
            "detours": list(
                self.detours
            ),
            "encounters": list(
                self.encounters
            ),
            "state": self.state,
            "observation_active": (
                self.observation_active
            )
        }
