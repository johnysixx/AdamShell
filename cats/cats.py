class Cats:

    def __init__(self, universe):
        self.universe = universe
        self.cats = []
        self.events = []
        self.tick_count = 0

        self.allowed_colors = [
            "white",
            "black",
            "blue",
            "gray",
            "orange",
            "cream",
            "chocolate",
            "cinnamon",
            "lilac",
            "fawn",
            "tortoiseshell",
            "blue_tortoiseshell",
            "calico"
        ]

        self.allowed_patterns = [
            "solid",
            "tabby",
            "tuxedo",
            "bicolor",
            "tricolor",
            "pointed",
            "smoke",
            "shaded"
        ]

        self.allowed_eye_colors = [
            "blue",
            "green",
            "yellow",
            "gold",
            "amber",
            "orange",
            "copper",
            "hazel",
            "aqua",
            "odd_eyed"
        ]

        self.allowed_fur_lengths = [
            "short",
            "long"
        ]

        self.allowed_sexes = [
            "female",
            "male"
        ]

        self.default_idea_energy = 100

        self.access_rules = {
            "can_access_anywhere": True,
            "access_via": [
                "boxes",
                "cat_doors"
            ]
        }

        self.universe.world["cats"] = {
            "type": "species_layer",
            "state": "created",
            "allowed_colors": self.allowed_colors,
            "allowed_patterns": self.allowed_patterns,
            "allowed_eye_colors": self.allowed_eye_colors,
            "allowed_fur_lengths": self.allowed_fur_lengths,
            "allowed_sexes": self.allowed_sexes,
            "default_idea_energy": self.default_idea_energy,
            "access_rules": self.access_rules,
            "cats": self.cats
        }

        print("CATS CREATED")
        print("CATS ACCESS: anywhere via boxes and cat doors")

    def create_cat(
            self,
            name,
            color,
            fur_length,
            pattern="solid",
            eye_color="green",
            sex="female",
            origin="manual_creation"
    ):
        if color not in self.allowed_colors:
            print(f"CAT CREATION DENIED: invalid color {color}")
            return None

        if fur_length not in self.allowed_fur_lengths:
            print(f"CAT CREATION DENIED: invalid fur length {fur_length}")
            return None

        if pattern not in self.allowed_patterns:
            print(f"CAT CREATION DENIED: invalid pattern {pattern}")
            return None

        if eye_color not in self.allowed_eye_colors:
            print(f"CAT CREATION DENIED: invalid eye color {eye_color}")
            return None

        if sex not in self.allowed_sexes:
            print(f"CAT CREATION DENIED: invalid sex {sex}")
            return None

        cat = {
            "name": name,
            "type": "cat",
            "state": "created",
            "color": color,
            "pattern": pattern,
            "eye_color": eye_color,
            "fur_length": fur_length,
            "sex": sex,
            "origin": origin,
            "idea_energy": self.default_idea_energy,
            "access": self.access_rules,
            "special_traits": []
        }

        self.cats.append(cat)
        self.universe.world["cats"]["cats"] = self.cats

        print(f"CAT CREATED: {name}")
        return cat

    def can_travel(self, cat, via):
            if cat.get("type") != "cat":
                return False

            if not self.access_rules.get("can_access_anywhere", False):
                return False

            allowed_routes = self.access_rules.get("access_via", [])

            return via in allowed_routes

    def emit_event(self, event):
        self.events.append(event)
        print(f"CATS EVENT: {event}")

    def tick(self):
        self.tick_count += 1
        print(f"CATS TICK {self.tick_count}")
        self._clear_events()

    def _clear_events(self):
        self.events = []

