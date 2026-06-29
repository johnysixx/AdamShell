class Universe:

    def __init__(self, universe_id=None):
        self.id = universe_id or "root"
        self.conflict_history = []
        self.conflict_pressure = 0
        self.threshold = 3
        self.entities = []
        self.entity_memory = {}

        self.light = False
        self.space = False
        self.rules_modified = False

        self.chaos = True
        self.order = False

        # DAY 3
        self.deep = False

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

        entity =  {
            "name": name,
            "streght": streght,
            "age:": 0
        }
        self.entities.append(entity)
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

        for entity in self.entities:
            entity.tick()

    def add_entity(self, entity):
        self.entities.append(entity)
        print(f"New entity added: {entity.name}")