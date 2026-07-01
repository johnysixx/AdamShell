from typing import Self

from core.entity.factory import EntityFactory

class Universe:

    def __init__(self, universe_id=None):
        self.id = universe_id or "root"
        self.entrophy = 0
        self.pressure = 0
        self.energy_pool = 100
        self.max_entities = 50
        self.conflict_history = []
        self.conflict_pressure = 0
        self.threshold = 3
        self.entities = []
        self.entity_memory = {}

        self.physics= {
            "light" : False,
            "space" : False,
            "time" : False,
            "gravity" : False,
        }
        self.world = {}

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

        self.entrophy += len(self.entities) * 0.01

        self.pressure = self.entrophy / (len(self.entities) + 1)

        self.energy_pool += len(self.entities) * 0.02

        self.energy_pool += 0.05

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

            self.physics[law] = True
            print(f"Physics enabled: {law}" )
    def boot_physics(self):

            self.enable_physics("light")
            self.enable_physics("time")
            self.enable_physics("gravity")
            self.enable_physics("space")
            self.enable_physics("energy")

            self.bind_spacetime()

            print("Physics booted")

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
        spacetime = self.world["spacetime"]

        spacetime["time_axis"]["time_axis"] += 1

        if self.physics["gravity"]:
            spacetime["curvature"] += 0.01

            print(
                f"SPACETIME TICK={spacetime['time_axis']['tick']} "
                f"CURVATURE={spacetime['curvature']:.2f}"
            )