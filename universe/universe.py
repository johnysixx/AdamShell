from typing import Self

from core.entity.factory import EntityFactory
from universe.big_bang import BigBang

class Universe:

    def __init__(self, universe_id=None):
        self.id = universe_id or "root"
        self.entropy = 0
        self.pressure = 0
        self.universe_tick =0
        self.universe_history = []
        self.energy_pool = 100
        self.last_pressure_cost =0.0
        self.last_energy_gain =0.0
        self.last_energy_delta = 0.0
        self.last_classical_entropy_delta = 0.0
        self.classical_entropy_total = 0.0
        self.max_entities = 50

        self.conflict_history = []
        self.conflict_pressure = 0
        self.threshold = 3
        self.entities = []
        self.entity_memory = {}


        self.physics_model = "symbolic_classical"

        self.physics_layers ={
            "classical": True,
            "quantum": False,
        }

        self.quantum_state = {
            "enabled": False,
            "superposition": False,
            "observer": None,
            "collapsed": False,
            "uncertainty": 0.0,
            "fluctuation": 0.0,
            "entropy_delta": 0.0,
            "entropy_total": 0.0,
        }

        self.physics= {
            "light" : False,
            "space" : False,
            "time" : False,
            "gravity" : False,
        }
        self.world = {}

        self.big_bang = BigBang(self)
        self.big_bang.explode()

        self.factory = EntityFactory()

        # universe is now state-less (entity driven)

        print(f"Universe created: {self.id}")
        print("The universe exists.")

    def hear(self, word):

        if word.name == "LetThereBeLight":
            self.light = True
            print("Light is created.")

        elif word.name == "LetThereBeSpace":
            self.space = True
            self.chaos = False
            self.order = True
            print("Space is separated from chaos.")

        # DAY 3 emergence
        elif word.name == "LetThereBeDeep":
            self.deep = True
            print("The Deep emerges from void.")

        elif word.name == "RewriteRule":
            self.rules_modified = True
            print("Reality rules are evolving...")

    def register_conflicts(self, conflicts):

        if not conflicts:
         return

        self.conflict_history.extend(conflicts)

    # ⚖️ slabý tlak místo okamžité změny
        self.conflict_pressure += len(conflicts)
        self.check_threshold()
        self.spawn_entities_from_conflicts(conflicts)

        print(f"⚠ Conflict pressure increased: {self.conflict_pressure}")

    def check_threshold(self):

        if self.conflict_pressure >= self.threshold:
            print("Threshold reached reality shift triggered")
            self.trigger_reality_shift()

    def trigger_reality_shift(self):
        self.conflict_pressure = 0
        self.chaos = True

        self.create_entity("TheresholdEvent", streght=3)


        print("Reality Shifted new layer formed")

    def create_entity(self, name, streght=1):

        entity = self.factory.create(name, self,)

        self.add_entity(entity)

        print("new entity created: ",  {name})

        return entity







    def spawn_entities_from_conflicts(self, conflicts):

        if not conflicts:
            return

        for c in conflicts:

            key = c["key"]

            if key == "light" and self.conflict_pressure > 1:
                self.create_entity("LightEcho", streght=1)

            if key == "space" and self.conflict_pressure > 1:
                self.create_entity("VoidRipple", streght=1)

            if key == "deep" and self.conflict_pressure > 1:
                self.create_entity("AbyssSeed", streght=1)

    def tick(self):

        if hasattr(self, "layers"):
            self.layers.tick()

    def add_entity(self, entity):
        self.entities.append(entity)
        print(f"New entity added: {entity.name}")

    def update_physics(self):

        self.last_classical_entropy_delta= len(self.entities) * 0.01
        self.classical_entropy_total += self.last_classical_entropy_delta
        self.entropy += self.last_classical_entropy_delta

        if self.quantum_state["enabled"]:
            self.entropy += self.quantum_state["entropy_delta"]


        self.pressure = self.entropy / (len(self.entities) + 1)

        if "spacetime" in self.world:
            self.pressure += self.world["spacetime"]["curvature"]


        self.energy_pool += len(self.entities) * 0.02

        self.last_energy_gain = 0.05
        self.energy_pool += self.last_energy_gain


        self.last_pressure_cost = self.pressure * 0.1
        self.energy_pool -= self.last_pressure_cost

        self.last_energy_delta = self.last_energy_gain - self.last_pressure_cost

    def enable_physics(self, law):

            if law == "time":
                self.physics["time"] = {
                    "tick": 0,
                    "flow": 1.0,
                    "state": "linear",
                    "pressure": 0.0
                }
                print("Physics enabled: time")
                return
            if law == "gravity":
                self.physics["gravity"] =  {
                    "enabled": True,
                    "strength": 1.0,
                    "curvature_effect": 0.01
                }
                print("Physics enabled: gravity")
                return

            self.physics[law] = True
            print(f"Physics enabled: {law}" )

    def enable_quantum_layer(self):

        self.physics_layers["quantum"] = True
        self.quantum_state["enabled"] = True
        self.physics_model = "symbolic_quantum"

        print("Quantum layers enabled")

    def boot_physics(self):

            self.enable_physics("light")
            self.enable_physics("time")
            self.enable_physics("gravity")
            self.enable_physics("space")
            self.enable_physics("energy")

            self.bind_spacetime()

            print("Physics booted")
            print(f"Physics model: {self.physics_model}")

            print(
                f"Physics layers: "
                f"classical={self.physics_layers['classical']} "
                f"quantum={self.physics_layers['quantum']} "
            )
            print(
                f"Quantum state: "
                f"enabled={self.quantum_state['enabled']} "
                f"superposition={self.quantum_state['superposition']} "
                f"collapsed={self.quantum_state['collapsed']}"
            )


    def tick_time(self):

        print(("DEBUG time: ", self.physics["time"]))

        if "time" in self.physics:
            t = self.physics["time"]

            t["tick"] += 1
            t["pressure"] += 0.1 * t["flow"]

            self.energy_pool -= t["pressure"] * 0.1

            print(
                f"TIME={t['tick']}  PRESSURE={t['pressure']:.2f}  ENERGY={self.energy_pool:.2f}"
            )

    def get_time(self):
        return self.physics["time"]["tick"]

    def get_energy(self):
        return self.energy_pool

    def bind_spacetime(self):
        self.world["spacetime"] = {
            "linked": True,
            "curvature": 0.0,

            "time_axis": {
                "tick": 0,
                "flow": 1.0,
                "state": "global"
            },

            "space_axis": {
                "dimensions": 3,
                "state": "global",
                "expanded": True
            }
        }
        print("time and space are bound into spacetime")

    def tick_spacetime(self):

        if "spacetime" not in self.world:
            print("No spacetime bound yet")
            return


        spacetime = self.world["spacetime"]

        spacetime["time_axis"]["tick"] += 1

        gravity = self.physics["gravity"]
        curvature_delta = 0.0

        if gravity and gravity["enabled"]:
                curvature_delta = gravity["curvature_effect"] * gravity["strength"]
                spacetime["curvature"] += curvature_delta

                print(
                 f"SPACETIME TICK={spacetime['time_axis']['tick']} "
                 f"DELTA={curvature_delta:.2f} "
                 f"CURVATURE={spacetime['curvature']:.2f}"
                 )

    def tick_quantum(self):

        if not self.quantum_state["enabled"]:
            return

        self.quantum_state["fluctuation"] += 0.01
        self.quantum_state["uncertainty"] = self.quantum_state["fluctuation"] * 0.5
        self.quantum_state["entropy_delta"] = self.quantum_state["uncertainty"] * 0.1
        self.quantum_state["entropy_total"] += self.quantum_state["entropy_delta"]

        print(
            f"QUANTUM TICK "
            f"FLUCTUATION={self.quantum_state['fluctuation']:.2f} "
            f"UNCERTAINTY={self.quantum_state['uncertainty']:.3f} "
            f"QENTROPY={self.quantum_state['entropy_delta']:.4f} "
        )

    def record_universe_state(self):

        curvature = 0.0

        if "spacetime" in self.world:
            curvature = self.world["spacetime"]["curvature"]

        snapshot = {
            "tick": self.universe_tick,
            "energy": self.energy_pool,
            "gain": self.last_energy_gain,
            "cost": self.last_pressure_cost,
            "delta": self.last_energy_delta,
            "classical_entropy_delta": self.last_classical_entropy_delta,
            "classical_entropy_total": self.classical_entropy_total,
            "entropy": self.entropy,
            "pressure": self.pressure,
            "curvature": curvature,
            "physics_model": self.physics_model,
            "quantum_enabled": self.quantum_state["enabled"],
            "quantum_fluctuation": self.quantum_state["fluctuation"],
            "quantum_uncertainty": self.quantum_state["uncertainty"],
            "quantum_entropy_delta": self.quantum_state["entropy_delta"],
            "quantum_entropy_total": self.quantum_state["entropy_total"],
        }

        self.universe_history.append(snapshot)





    def tick_universe(self):
        self.universe_tick += 1

        self.tick_spacetime()
        self.tick_quantum()
        self.update_physics()
        self.record_universe_state()

        last_snapshot = self.universe_history[-1]

        print(
            f"UNIVERSE TICK={self.universe_tick} "
            f"HISTORY={len(self.universe_history)} "
            f"MODEL={last_snapshot.get('physics_model', 'unknown')} "
            f"QUANTUM={last_snapshot.get('quantum_enabled', False)} "
            f"QFLUCT={last_snapshot.get('quantum_fluctuation', 0.0):.2f} "
            f"QUNCERT={last_snapshot.get('quantum_uncertainty', 0.0):.3f} "
            f"QENTROPY={last_snapshot.get('quantum_entropy_delta', 0.0):.4f} "
            f"QTOTAL={last_snapshot.get('quantum_entropy_total', 0.0):.4f} "
            f"CENTROPY={last_snapshot.get('classical_entropy_delta', 0.0):.4f} "
            f"CTOTAL={last_snapshot.get('classical_entropy_total', 0.0):.4f} "
            f"ENERGY={self.energy_pool:.4f} "
            f"GAIN={self.last_energy_gain:.4f} "
            f"COST={self.last_pressure_cost:.4f} "
            f"DELTA={self.last_energy_delta:.4f} "
            f"ENTROPY={self.entropy:.4f} "
            f"PRESSURE={self.pressure:.4f} "
            f"CURVATURE={last_snapshot['curvature']:.2f}"
        )


        print("universe tick complete")