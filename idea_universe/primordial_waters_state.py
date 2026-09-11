from dataclasses import dataclass


@dataclass(slots=True)
class PrimordialWatersState:

    waters: bool = False
    deep: bool = False
    chaos: bool = False
    ordered: bool = False
    light: bool = False
    order_started: bool = False
    space: bool = False
    can_expand: bool = False
    seas: bool = False
    dry_land: bool = False
    vegetation: bool = False

    def to_dict(self):
        return {
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
            "vegetation": self.vegetation,
        }
