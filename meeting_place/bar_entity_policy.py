class BarEntityPolicy:

    AUTOMATIC_ACCESS = "automatic"
    POTENTIAL_ACCESS = "potential"
    NO_ACCESS = "none"

    PERSONAL_NAMED_GLASS = "personal_named"
    RESERVED_UNNAMED_GLASS = "reserved_unnamed"
    SHARED_GLASS = "shared"
    NO_GLASS = "none"

    STANDARD_SERVICE = "standard"
    CAT_UNTIL_ORDER_SERVICE = "cat_until_order"
    CAT_SERVICE = "cat"

    def resolve(self, profile, technical_name=None):
        if not isinstance(profile, dict):
            return {
                "entity_id": technical_name,
                "entity_class": "unclassified",
                "access_mode": self.NO_ACCESS,
                "glass_mode": self.SHARED_GLASS,
                "service_mode": self.STANDARD_SERVICE
            }

        entity_id = (
            profile.get("entity_id")
            or profile.get("world_key")
            or technical_name
            or profile.get("name")
        )

        entity_type = profile.get("type")

        entity_class = profile.get(
            "entity_class"
        )

        if entity_class is None:
            entity_class = self._infer_entity_class(
                profile,
                entity_type
            )

        if entity_class == "god":
            return {
                "entity_id": entity_id,
                "entity_class": entity_class,
                "access_mode": self.AUTOMATIC_ACCESS,
                "glass_mode": self.PERSONAL_NAMED_GLASS,
                "service_mode": self.STANDARD_SERVICE
            }

        if entity_class == "special_idea_entity":
            service_mode = self.STANDARD_SERVICE

            if entity_type == "cat":
                service_mode = (
                    self.CAT_UNTIL_ORDER_SERVICE
                )

            return {
                "entity_id": entity_id,
                "entity_class": entity_class,
                "access_mode": self.AUTOMATIC_ACCESS,
                "glass_mode": self.PERSONAL_NAMED_GLASS,
                "service_mode": service_mode
            }

        if entity_class == "common_idea_entity":
            return {
                "entity_id": entity_id,
                "entity_class": entity_class,
                "access_mode": self.POTENTIAL_ACCESS,
                "glass_mode": self.RESERVED_UNNAMED_GLASS,
                "service_mode": self.STANDARD_SERVICE
            }

        if entity_class == "physical_universe_entity":
            return {
                "entity_id": entity_id,
                "entity_class": entity_class,
                "access_mode": self.NO_ACCESS,
                "glass_mode": self.SHARED_GLASS,
                "service_mode": self.STANDARD_SERVICE
            }

        if entity_class == "cat" or entity_type == "cat":
            return {
                "entity_id": entity_id,
                "entity_class": "cat",
                "access_mode": self.NO_ACCESS,
                "glass_mode": self.NO_GLASS,
                "service_mode": self.CAT_SERVICE
            }

        return {
            "entity_id": entity_id,
            "entity_class": entity_class,
            "access_mode": self.NO_ACCESS,
            "glass_mode": self.SHARED_GLASS,
            "service_mode": self.STANDARD_SERVICE
        }

    def _infer_entity_class(
            self,
            profile,
            entity_type
    ):
        entity_name = profile.get("name")
        world_key = profile.get("world_key")
        alias = profile.get("alias")

        special_idea_names = {
            "serpent",
            "lilith",
            "pazuzu"
        }

        if entity_type == "god":
            return "god"

        if entity_type == "physical_universe_entity":
            return "physical_universe_entity"

        if entity_type == "cat":
            if (
                entity_name == "pazuzu"
                or alias
                == "classical_probe_debug_entity"
            ):
                return "special_idea_entity"

            return "cat"

        if entity_type == "idea_entity":
            if world_key == "pazuzu_masculine_principle":
                return "common_idea_entity"

            if entity_name in special_idea_names:
                return "special_idea_entity"

            return "common_idea_entity"

        return "unclassified"
