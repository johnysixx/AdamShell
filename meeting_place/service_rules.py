from universe.pre_cosmic_rules import REALITY_PAYMENT_RATIO, WILL_GAIN_PER_ENERGY_SERVING, captured_by_bar
from core.entity.existence_energy import existence_pct_to_energy_j
IDEA_ENTITY_ENERGY_EXISTENCE_COST_PERCENT = REALITY_PAYMENT_RATIO * 100
GOD_ENERGY_CREATIVE_WILL_GAIN = 0.3
GOD_ENTROPY_EXISTENCE_GAIN_PERCENT = 1.0

class BarServiceRules:

    def apply_basic_drink_payment(self, entity):
        entity_type = self._get(entity, 'type')
        entity_name = self._get(entity, 'name')
        if entity_type == 'god':
            return {'name': 'god_basic_drink_payment', 'entity': entity_name, 'payment_kind': 'god_rule', 'existence_paid_pct': 0.0, 'energy_paid_j': 0.0}
        if entity_type == 'idea_entity':
            energy_j = float(self._get(entity, 'energy_j', 0.0))
            energy_paid_j = energy_j * REALITY_PAYMENT_RATIO
            self._set(entity, 'energy_j', max(0.0, energy_j - energy_paid_j))
            return {'name': 'idea_entity_basic_drink_payment', 'entity': entity_name, 'payment_kind': 'energy', 'energy_paid_j': energy_paid_j, 'existence_paid_pct': 0.0}
        if entity_type == 'root_entity':
            existence_by_world = self._get(entity, 'existence_by_world', {})
            current = float(existence_by_world.get('root_universe', 0.0))
            existence_paid_pct = min(25.0, current)
            existence_by_world['root_universe'] = current - existence_paid_pct
            return {'name': 'root_entity_basic_drink_payment', 'entity': entity_name, 'payment_kind': 'root_existence', 'existence_paid_pct': existence_paid_pct, 'energy_paid_j': 0.0}
        if entity_type == 'physical_entity':
            existence_by_world = self._get(entity, 'existence_by_world', {})
            physical_before = float(existence_by_world.get('physical_universe', 0.0))
            existence_paid_pct = min(90.0, physical_before)
            existence_by_world['physical_universe'] = physical_before - existence_paid_pct
            idea_gain_pct = min(40.0, existence_paid_pct)
            idea_before = float(existence_by_world.get('idea_universe', 0.0))
            existence_by_world['idea_universe'] = min(100.0, idea_before + idea_gain_pct)
            converted_pct = max(0.0, existence_paid_pct - idea_gain_pct)
            generated_energy_j = existence_pct_to_energy_j(converted_pct)
            bar_energy_j = captured_by_bar(generated_energy_j)
            return {'name': 'physical_entity_basic_drink_payment', 'entity': entity_name, 'payment_kind': 'reality_exchange', 'existence_paid_pct': existence_paid_pct, 'idea_existence_gain_pct': idea_gain_pct, 'existence_converted_to_energy_pct': converted_pct, 'generated_energy_j': generated_energy_j, 'bar_energy_j': bar_energy_j}
        return {'name': 'basic_drink_payment_not_available', 'entity': entity_name, 'entity_type': entity_type, 'payment_kind': 'unsupported'}

    def apply_energy_drink(self, entity):
        entity_type = self._get(entity, 'type')
        if entity_type == 'god':
            creative_will = self._get(entity, 'creative_will', 0.0)
            self._set(entity, 'creative_will', creative_will + GOD_ENERGY_CREATIVE_WILL_GAIN)
            self._update_creation_capacity(entity)
            return {'name': 'god_energy_drink_effect', 'entity': self._get(entity, 'name'), 'existence_cost_pct': 0.0, 'creative_will_gain': GOD_ENERGY_CREATIVE_WILL_GAIN}
        if entity_type == 'idea_entity':
            existence_pct = self._get(entity, 'existence_pct', 100.0)
            will = self._get(entity, 'will', 0.0)
            new_existence = max(0.0, existence_pct - IDEA_ENTITY_ENERGY_EXISTENCE_COST_PERCENT)
            self._set(entity, 'existence_pct', new_existence)
            self._set(entity, 'will', will + WILL_GAIN_PER_ENERGY_SERVING)
            self._update_idea_capacity(entity)
            return {'name': 'idea_entity_energy_drink_effect', 'entity': self._get(entity, 'name'), 'existence_cost_pct': IDEA_ENTITY_ENERGY_EXISTENCE_COST_PERCENT, 'will_gain': WILL_GAIN_PER_ENERGY_SERVING}
        return {'name': 'energy_drink_not_available', 'entity': self._get(entity, 'name'), 'entity_type': entity_type}

    def apply_entropy_drink(self, entity, entity_energy_gain_j=0.0):
        entity_type = self._get(entity, 'type')
        entity_name = self._get(entity, 'name')
        if entity_type == 'god':
            energy_j = self._get(entity, 'energy_j', 0.0)
            self._set(entity, 'energy_j', energy_j + entity_energy_gain_j)
            existence_pct = self._get(entity, 'existence_pct', 100.0)
            new_existence = min(100.0, existence_pct + GOD_ENTROPY_EXISTENCE_GAIN_PERCENT)
            self._set(entity, 'existence_pct', new_existence)
            self._update_creation_capacity(entity)
            return {'name': 'god_entropy_drink_effect', 'entity': entity_name, 'existence_gain_pct': GOD_ENTROPY_EXISTENCE_GAIN_PERCENT, 'entity_energy_gain_j': entity_energy_gain_j, 'payment_pct': 0.0}
        if entity_type == 'idea_entity':
            energy_j = self._get(entity, 'energy_j', 0.0)
            self._set(entity, 'energy_j', energy_j + entity_energy_gain_j)
            self._update_idea_capacity(entity)
            return {'name': 'idea_entity_entropy_drink_effect', 'entity': entity_name, 'entity_energy_gain_j': entity_energy_gain_j, 'payment_pct': 0.0}
        return {'name': 'entropy_drink_not_available', 'entity': entity_name, 'entity_type': entity_type}

    def _update_creation_capacity(self, entity):
        existence_pct = self._get(entity, 'existence_pct', 100.0)
        creative_will = self._get(entity, 'creative_will', 0.0)
        creation_capacity = creative_will * (existence_pct / 100.0)
        self._set(entity, 'creation_capacity', creation_capacity)

    def _update_idea_capacity(self, entity):
        existence_pct = self._get(entity, 'existence_pct', 100.0)
        will = self._get(entity, 'will', 0.0)
        idea_capacity = will * (existence_pct / 100.0)
        self._set(entity, 'idea_capacity', idea_capacity)

    def _get(self, entity, key, default=None):
        return getattr(entity, key, default)

    def _set(self, entity, key, value):
        setattr(entity, key, value)
