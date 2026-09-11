from idea_universe.primordial_waters_state import (
    PrimordialWatersState,
)


class PrimordialWaters:

    def __init__(self):
        self.name = "primordial_waters"
        self.type = "primordial_waters"

        self.primordial_waters_state = (
            PrimordialWatersState()
        )
        self.state = self.primordial_waters_state

    @property
    def waters(self):
        return self.primordial_waters_state.waters

    @waters.setter
    def waters(self, value):
        self.primordial_waters_state.waters = value

    @property
    def deep(self):
        return self.primordial_waters_state.deep

    @deep.setter
    def deep(self, value):
        self.primordial_waters_state.deep = value

    @property
    def chaos(self):
        return self.primordial_waters_state.chaos

    @chaos.setter
    def chaos(self, value):
        self.primordial_waters_state.chaos = value

    @property
    def ordered(self):
        return self.primordial_waters_state.ordered

    @ordered.setter
    def ordered(self, value):
        self.primordial_waters_state.ordered = value

    @property
    def light(self):
        return self.primordial_waters_state.light

    @light.setter
    def light(self, value):
        self.primordial_waters_state.light = value

    @property
    def order_started(self):
        return self.primordial_waters_state.order_started

    @order_started.setter
    def order_started(self, value):
        self.primordial_waters_state.order_started = value

    @property
    def space(self):
        return self.primordial_waters_state.space

    @space.setter
    def space(self, value):
        self.primordial_waters_state.space = value

    @property
    def can_expand(self):
        return self.primordial_waters_state.can_expand

    @can_expand.setter
    def can_expand(self, value):
        self.primordial_waters_state.can_expand = value

    @property
    def seas(self):
        return self.primordial_waters_state.seas

    @seas.setter
    def seas(self, value):
        self.primordial_waters_state.seas = value

    @property
    def dry_land(self):
        return self.primordial_waters_state.dry_land

    @dry_land.setter
    def dry_land(self, value):
        self.primordial_waters_state.dry_land = value

    @property
    def vegetation(self):
        return self.primordial_waters_state.vegetation

    @vegetation.setter
    def vegetation(self, value):
        self.primordial_waters_state.vegetation = value

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            **self.primordial_waters_state.to_dict(),
        }
