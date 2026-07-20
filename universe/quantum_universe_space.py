import random
import uuid

from core.entity.quantum_cat_route import QuantumCatRoute
from quantum.geometry_engine import QuantumGeometryEngine


class QuantumUniverseSpace:

    def __init__(self, quantum_die_box):
        self.name = "quantum_universe_space"
        self.type = "quantum_space"

        self.quantum_die_box = quantum_die_box
        self.geometry_engine = QuantumGeometryEngine()

        self.configuration_id = None
        self.configuration_seed = None
        self.reconfiguration_count = 0
        self.reconfiguration_chance = 0.15

        self.staircases = []
        self.cat_routes = []

        self.bar_front_door = {
            "name": "bar_front_door",
            "position": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        }

        self.reconfigure(cause="initialization")

    def generate_space_sample(
            self,
            sample_key,
            count=8
    ):
        if self.configuration_seed is None:
            raise RuntimeError(
                "Quantum space has no configuration seed."
            )

        local_rng = random.Random(
            f"{self.configuration_seed}:{sample_key}"
        )

        return [
            {
                "id": (
                    f"generated_staircase_"
                    f"{sample_key}_{index}"
                ),
                "origin": {
                    "x": local_rng.uniform(-10.0, 10.0),
                    "y": local_rng.uniform(-10.0, 10.0),
                    "z": local_rng.uniform(-10.0, 10.0)
                },
                "destination": {
                    "x": local_rng.uniform(-10.0, 10.0),
                    "y": local_rng.uniform(-10.0, 10.0),
                    "z": local_rng.uniform(-10.0, 10.0)
                },
                "orientation": local_rng.choice([
                    "up",
                    "down",
                    "left",
                    "right",
                    "inverted",
                    "impossible"
                ]),
                "length": local_rng.uniform(1.0, 8.0)
            }
            for index in range(count)
        ]

    def get_active_cat_routes(self):
        return [
            route
            for route in self.cat_routes
            if route.observation_active
        ]

    def reconfigure(self, cause, rng=None):
        rng = rng or random

        active_routes = self.get_active_cat_routes()

        new_staircases = []

        target_count = rng.randint(8, 16)
        missing_count = target_count

        for _ in range(missing_count):
            staircase_id = (
                f"staircase_{uuid.uuid4().hex[:8]}"
            )

            new_staircases.append({
                "id": staircase_id,
                "origin": {
                    "x": rng.uniform(-10.0, 10.0),
                    "y": rng.uniform(-10.0, 10.0),
                    "z": rng.uniform(-10.0, 10.0)
                },
                "destination": {
                    "x": rng.uniform(-10.0, 10.0),
                    "y": rng.uniform(-10.0, 10.0),
                    "z": rng.uniform(-10.0, 10.0)
                },
                "orientation": rng.choice([
                    "up",
                    "down",
                    "left",
                    "right",
                    "inverted",
                    "impossible"
                ]),
                "length": rng.uniform(1.0, 8.0)
            })

        self.staircases = new_staircases

        self.configuration_seed = rng.randint(
            0,
            2**63 - 1
        )

        self.configuration_id = (
            f"quantum_configuration_"
            f"{self.configuration_seed}"
        )

        self.geometry_engine.configure(
            self.configuration_seed
        )

        self.reconfiguration_count += 1

        self.quantum_die_box.move_to({
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        })

        print(
            f"QUANTUM SPACE RECONFIGURED "
            f"CAUSE={cause} "
            f"CONFIG={self.configuration_id} "
            f"ACTIVE_CAT_ROUTES={len(active_routes)}"
        )

    def quantum_tick(self, rng=None):
        rng = rng or random

        if rng.random() >= self.reconfiguration_chance:
            return False

        self.reconfigure(
            cause="unobserved_quantum_tick",
            rng=rng
        )

        return True

    def collapse_reconfiguration(self, rng=None):
        self.reconfigure(
            cause="wave_function_collapse",
            rng=rng
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "configuration_id": self.configuration_id,
            "configuration_seed": self.configuration_seed,
            "reconfiguration_count": self.reconfiguration_count,
            "staircase_count": len(self.staircases),
            "active_cat_route_count": len(
                self.get_active_cat_routes()
            ),
            "active_cat_routes": [
                route.public_state
                for route in self.get_active_cat_routes()
            ],
            "quantum_die_box": (
                self.quantum_die_box.public_state
            ),
            "bar_front_door": dict(
                self.bar_front_door
            ),
            "geometry_engine": (
                self.geometry_engine.public_state
            )
        }
