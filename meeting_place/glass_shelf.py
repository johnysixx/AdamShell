class GlassShelf:

    def __init__(self):
        self.name = "glass_shelf"
        self.location = "behind_bar"

        self.personal_glasses = {}
        self.reserved_glasses = []
        self.shared_glasses = []

        print("GLASS SHELF CREATED BEHIND BAR")

    def register_policy_decision(self, decision):
        glass_mode = decision.get("glass_mode")
        entity_id = decision.get("entity_id")

        if glass_mode == "none":
            return None

        if glass_mode == "personal_named":
            return self._create_personal_glass(
                entity_id
            )

        if glass_mode == "reserved_unnamed":
            return self._create_reserved_glass(
                entity_id
            )

        if glass_mode == "shared":
            return self._create_shared_glass(
                entity_id
            )

        return None

    def _create_personal_glass(self, entity_id):
        if entity_id in self.personal_glasses:
            return self.personal_glasses[entity_id]

        glass = {
            "name": f"{entity_id}_glass",
            "type": "personal_bar_glass",
            "owner": entity_id,
            "state": "clean",
            "dirt": 0.0,
            "location": self.name
        }

        self.personal_glasses[entity_id] = glass

        print(
            f"PERSONAL GLASS CREATED: "
            f"{glass['name']}"
        )

        return glass

    def _create_reserved_glass(self, entity_id):
        for glass in self.reserved_glasses:
            if glass.get("reserved_for") == entity_id:
                return glass

        reservation_number = (
            len(self.reserved_glasses) + 1
        )

        glass = {
            "name": None,
            "type": "reserved_bar_glass",
            "owner": None,
            "reserved_for": entity_id,
            "reservation_number": reservation_number,
            "state": "clean",
            "dirt": 0.0,
            "location": self.name
        }

        self.reserved_glasses.append(glass)

        print(
            f"UNNAMED RESERVED GLASS CREATED: "
            f"reservation_{reservation_number}"
        )

        return glass

    def _create_shared_glass(self, entity_id):
        glass_number = len(self.shared_glasses) + 1

        glass = {
            "name": f"shared_glass_{glass_number}",
            "type": "shared_bar_glass",
            "owner": None,
            "created_for_entity": entity_id,
            "state": "clean",
            "dirt": 0.0,
            "location": self.name
        }

        self.shared_glasses.append(glass)

        print(
            f"SHARED GLASS CREATED: "
            f"{glass['name']}"
        )

        return glass
