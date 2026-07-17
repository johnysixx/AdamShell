from universe.pre_cosmic_rules import (
    REALITY_PAYMENT_RATIO,
    WILL_GAIN_PER_ENERGY_SERVING,
)


IDEA_ENTITY_ENERGY_EXISTENCE_COST_PERCENT = REALITY_PAYMENT_RATIO * 100
GOD_ENERGY_CREATIVE_WILL_GAIN = 0.3
GOD_ENTROPY_EXISTENCE_GAIN_PERCENT = 1.0


class BarServiceRules:

    def apply_energy_drink(self, entity):
        entity_type = self._get(entity, "type")

        if entity_type == "god":
            creative_will = self._get(entity, "creative_will", 0.0)
            self._set(entity, "creative_will", creative_will + GOD_ENERGY_CREATIVE_WILL_GAIN)
            self._update_creation_capacity(entity)

            return {
                "name": "god_energy_drink_effect",
                "entity": self._get(entity, "name"),
                "existence_cost_pct": 0.0,
                "creative_will_gain": GOD_ENERGY_CREATIVE_WILL_GAIN
            }

        if entity_type == "idea_entity":
            existence_pct = self._get(entity, "existence_pct", 100.0)
            will = self._get(entity, "will", 0.0)

            new_existence = max(
                0.0,
                existence_pct - IDEA_ENTITY_ENERGY_EXISTENCE_COST_PERCENT
            )

            self._set(entity, "existence_pct", new_existence)
            self._set(entity, "will", will + WILL_GAIN_PER_ENERGY_SERVING)
            self._update_idea_capacity(entity)

            return {
                "name": "idea_entity_energy_drink_effect",
                "entity": self._get(entity, "name"),
                "existence_cost_pct": IDEA_ENTITY_ENERGY_EXISTENCE_COST_PERCENT,
                "will_gain": WILL_GAIN_PER_ENERGY_SERVING
            }

        return {
            "name": "energy_drink_not_available",
            "entity": self._get(entity, "name"),
            "entity_type": entity_type
        }

    def apply_entropy_drink(self, entity, entity_energy_gain_j=0.0):
        entity_type = self._get(entity, "type")

        if entity_type == "god":
            existence_pct = self._get(entity, "existence_pct", 100.0)

            new_existence = min(
                100.0,
                existence_pct + GOD_ENTROPY_EXISTENCE_GAIN_PERCENT
            )

            self._set(entity, "existence_pct", new_existence)
            self._update_creation_capacity(entity)

            return {
                "name": "god_entropy_drink_effect",
                "entity": self._get(entity, "name"),
                "existence_gain_pct": GOD_ENTROPY_EXISTENCE_GAIN_PERCENT,
                "payment_pct": 0.0
            }

        if entity_type == "idea_entity":
            energy_j = self._get(entity, "energy_j", 0.0)
            self._set(entity, "energy_j", energy_j + entity_energy_gain_j)
            self._update_idea_capacity(entity)

            return {
                "name": "idea_entity_entropy_drink_effect",
                "entity": self._get(entity, "name"),
                "entity_energy_gain_j": entity_energy_gain_j,
                "payment_pct": 0.0
            }

        return {
            "name": "entropy_drink_not_available",
            "entity": self._get(entity, "name"),
            "entity_type": entity_type
        }

    def _update_creation_capacity(self, entity):
        existence_pct = self._get(entity, "existence_pct", 100.0)
        creative_will = self._get(entity, "creative_will", 0.0)

        creation_capacity = creative_will * (existence_pct / 100.0)
        self._set(entity, "creation_capacity", creation_capacity)

    def _update_idea_capacity(self, entity):
        existence_pct = self._get(entity, "existence_pct", 100.0)
        will = self._get(entity, "will", 0.0)

        idea_capacity = will * (existence_pct / 100.0)
        self._set(entity, "idea_capacity", idea_capacity)

    def _get(self, entity, key, default=None):
        if isinstance(entity, dict):
            return entity.get(key, default)

        return getattr(entity, key, default)

    def _set(self, entity, key, value):
        if isinstance(entity, dict):
            entity[key] = value
            return

        setattr(entity, key, value)
