from typing import Self

from core.entity.factory import EntityFactory
from core.entity.profile_resolver import EntityProfileResolver
from core.entity.quantum_die import QuantumDie
from core.entity.quantum_die_box import QuantumDieBox
from universe.quantum_universe_space import QuantumUniverseSpace
from universe.big_bang import BigBang
from core.entity.quantum_box import QuantumBox
from universe.universe_statistics import UniverseStatistics

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

        self.quantum_die = QuantumDie()
        self.quantum_boxes = []
        self.quantum_events = []
        self.statistics = UniverseStatistics()

        self.quantum_state = {
            "enabled": False,
            "superposition": False,
            "observer": None,
            "collapsed": False,
            "tick_count": 0,
            "collapse_count": 0,
            "last_collapse_tick": None,
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

        self.big_bang = None
        self.big_bang_started = False
        self.physical_universe_started = False
        self.universe_exists = False
        self.state = "pre_universe"

        self.factory = EntityFactory()

        # universe is now state-less (entity driven)

        print(f"Root reality prepared: {self.id}")
        print("Physical universe has not started yet.")

    @property
    def snapshot(self):
        geometry_state = None

        if hasattr(self, "quantum_space"):
            geometry_state = (
                self.quantum_space
                .geometry_engine
                .public_state
            )

        return {
            "universe_id": self.id,
            "tick": self.universe_tick,
            "energy": self.energy_pool,
            "pressure": self.pressure,
            "entropy": self.entropy,
            "statistics": self.statistics.public_state,
            "geometry": geometry_state
        }

    def start_big_bang(self):
        if self.big_bang_started:
            print("BIG BANG ALREADY STARTED")
            return self.world.get("big_bang")

        self.big_bang = BigBang(self)
        self.big_bang.explode()

        self.big_bang_started = True
        self.physical_universe_started = True
        self.universe_exists = True
        self.state = "physical_universe"

        print("PHYSICAL UNIVERSE STARTED")
        print("THE UNIVERSE EXISTS")

        return self.world.get("big_bang")

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

    def create_entity(
            self,
            name,
            streght=1,
            profile=None
    ):

        entity = self.factory.create(
            name,
            self
        )

        if profile is None:
            profile = EntityProfileResolver.find_profile(
                world=self.world,
                technical_name=name
            )

        entity.profile = profile

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

        print(
            f"New entity added: {entity.name}"
        )

        meeting_place = getattr(
            self,
            "meeting_place",
            None
        )

        if meeting_place is None:
            return

        profile = getattr(
            entity,
            "profile",
            None
        )

        decision = (
            meeting_place
            .bar_entity_policy
            .resolve(
                profile=profile,
                technical_name=entity.name
            )
        )

        entity.bar_policy = decision

        meeting_place.glass_shelf.register_policy_decision(
            decision
        )

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

        if not hasattr(self, "quantum_die_box"):
            self.quantum_die_box = QuantumDieBox(
                self.quantum_die
            )

        if not hasattr(self, "quantum_space"):
            self.quantum_space = QuantumUniverseSpace(
                self.quantum_die_box
            )

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

    def open_quantum_box(
            self,
            box_id,
            observer=None,
            rng=None
    ):
        box = next(
            (
                quantum_box
                for quantum_box in self.quantum_boxes
                if quantum_box.id == box_id
            ),
            None
        )

        if box is None:
            print(f"QUANTUM BOX NOT FOUND: {box_id}")
            return None

        result = box.collapse_state(
            cause="opened",
            observer=observer,
            tick=self.quantum_state["tick_count"],
            rng=rng
        )

        self.statistics.record_quantum_collapse()


        if result == "cat":
            event = {
                "name": "cat_manifestation_requested",
                "source": "cat_distribution_system",
                "collapse_cause": "opened",
                "box_id": box.id,
                "position": box.position.copy(),
                "observer": observer,
                "tick": self.quantum_state["tick_count"]
            }

            self.statistics.record_cat_created()

            self.quantum_events.append(event)

            print(
                f"CAT JUMPS OUT OF QUANTUM BOX: {box.id}"
            )

        else:
            event = {
                "name": "empty_quantum_box_opened",
                "collapse_cause": "opened",
                "box_id": box.id,
                "position": box.position.copy(),
                "observer": observer,
                "tick": self.quantum_state["tick_count"]
            }

            print(f"QUANTUM BOX WAS EMPTY: {box.id}")

        self.quantum_boxes.remove(box)
        self.statistics.record_quantum_box_disappeared()

        print(f"QUANTUM BOX DISAPPEARED: {box.id}")

        return event

    def create_quantum_box(self, rng=None):
        box = QuantumBox(rng=rng)
        self.quantum_boxes.append(box)
        self.statistics.record_quantum_box_created()

        print(
            f"QUANTUM BOX CREATED: {box.id} "
            f"AT x={box.position['x']:.3f} "
            f"y={box.position['y']:.3f} "
            f"z={box.position['z']:.3f}"
        )

        return box

    def should_collapse_quantum_box(self, box, rng=None):
        import random

        rng = rng or random

        base_chance = 0.01
        age_factor = box.age_ticks * 0.001

        collapse_chance = min(
            base_chance + age_factor,
            0.25
        )

        return rng.random() < collapse_chance

    def tick_quantum(self):

        if not self.quantum_state["enabled"]:
            return

        self.quantum_state["tick_count"] += 1

        self.quantum_state["collapsed"] = False
        self.quantum_state["superposition"] = True
        self.quantum_state["observer"] = "quantum_tick"

        self.quantum_state["fluctuation"] += 0.01
        self.quantum_state["uncertainty"] = self.quantum_state["fluctuation"] * 0.5
        self.quantum_state["entropy_delta"] = self.quantum_state["uncertainty"] * 0.1
        self.quantum_state["entropy_total"] += self.quantum_state["entropy_delta"]

        self.quantum_state["superposition"] = False
        self.quantum_state["collapsed"] = True
        self.quantum_state["collapse_count"] += 1
        self.quantum_state["last_collapse_tick"] = (
            self.quantum_state["tick_count"]
        )

        for box in list(self.quantum_boxes):
            box.age_ticks += 1

            if not self.should_collapse_quantum_box(box):
                continue

            result = box.collapse_state(
                cause="spontaneous",
                observer=None,
                tick=self.quantum_state["tick_count"]
            )

            self.statistics.record_quantum_collapse()


            if result == "cat":
                event = {
                    "name": "cat_manifestation_requested",
                    "source": "cat_distribution_system",
                    "collapse_cause": "spontaneous",
                    "box_id": box.id,
                    "position": box.position.copy(),
                    "observer": None,
                    "tick": self.quantum_state["tick_count"]
                }

                self.statistics.record_cat_created()

                self.quantum_events.append(event)

                print(
                    f"CAT MANIFESTS FROM SPONTANEOUS "
                    f"QUANTUM COLLAPSE: {box.id}"
                )
            else:
                print(
                    f"SPONTANEOUSLY COLLAPSED BOX WAS EMPTY: "
                    f"{box.id}"
                )

            self.quantum_boxes.remove(box)
            self.statistics.record_quantum_box_disappeared()

            print(
                f"QUANTUM BOX DISAPPEARED: {box.id}"
            )

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
