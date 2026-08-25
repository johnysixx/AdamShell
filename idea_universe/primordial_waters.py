class PrimordialWaters:

    def __init__(self):
        self.name = "primordial_waters"
        self.type = "primordial_waters"

        self.waters = False
        self.deep = False
        self.chaos = False
        self.ordered = False

        self.light = False
        self.order_started = False

        self.space = False
        self.can_expand = False

        self.seas = False
        self.dry_land = False
        self.vegetation = False

        self.state = {
            "name": self.name,
            "type": self.type,
            "waters": self.waters,
            "deep": self.deep,
            "chaos": self.chaos,
            "ordered": self.ordered,
            "light": self.light,
            "order_started": self.order_started,
            "space": self.space,
            "can_expand": self.can_expand,
            "seas": self.seas,
            "dry_land": self.dry_land,
            "vegetation": self.vegetation
        }
