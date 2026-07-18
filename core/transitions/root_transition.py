class RootTransition:

    def __init__(
            self,
            existence_cost_pct=25.0,
            energy_cost_j=1000.0
    ):
        self.existence_cost_pct = existence_cost_pct
        self.energy_cost_j = energy_cost_j


    def can_create(self, entity):
        is_allowed_entity = (
            entity.get("name") == "serpent"
        )

        has_enough_existence = (
            entity.get("existence_pct", 0.0) >= 100.0
        )

        has_enough_energy = (
            entity.get("energy_j", 0.0) >= self.energy_cost_j
        )

        return (
            is_allowed_entity
            and has_enough_existence
            and has_enough_energy
        )


    def create(self, entity):
        if not self.can_create(entity):
            return False

        entity["existence_pct"] -= self.existence_cost_pct
        entity["energy_j"] -= self.energy_cost_j

        entity["root_transition"] = {
            "target": "root_universe",
            "state": "created",
            "creator": entity.get("name"),
            "existence_cost_pct": self.existence_cost_pct,
            "energy_cost_j": self.energy_cost_j,
            "can_enter": False
        }

        return True

    def can_enter(self, entity):
        transition = entity.get("root_transition")

        if transition is None:
            return False

        transition_exists = (
                transition.get("state") == "created"
        )

        existence_restored = (
                entity.get("existence_pct", 0.0)
                >= 100.0
        )

        return transition_exists and existence_restored

    def update_entry_status(self, entity):
        transition = entity.get("root_transition")

        if transition is None:
            return False

        transition["can_enter"] = self.can_enter(entity)

        return transition["can_enter"]

    def enter(self, entity):
        if not self.can_enter(entity):
            return False

        transition = entity["root_transition"]

        transition["can_enter"] = True
        transition["state"] = "used"

        entity["current_layer"] = "root_universe"
        entity["root_presence"] = True

        return True
