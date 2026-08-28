from core.entity.social_entity import _entity_attr_setdefault
from cats.duplicate_consumption_energy import DuplicateConsumptionEnergy

class KittenGrowth:
    MILK_SIZE_GAIN = 0.006
    MILK_STRENGTH_GAIN = 0.0015
    DEAD_CRONENBERG_PORTION = 0.08
    FATHER_CRONENBERG_PORTION = 0.12
    FIRST_KILL_PORTION = 0.18
    FAMILY_HUNT_PORTION = 0.22
    SIZE_GAIN_PER_MASS = 0.08
    STRENGTH_GAIN_PER_MASS = 0.12

    def __init__(self, universe):
        self.universe = universe
        self.history = []
        self.duplicate_energy = DuplicateConsumptionEnergy(universe)

    def ensure_state(self, kitten):
        growth = _entity_attr_setdefault(kitten, 'growth', {'milk_feedings': 0, 'milk_units_consumed': 0.0, 'cronenberg_portions_eaten': 0, 'cronenberg_mass_consumed': 0.0, 'size_gained': 0.0, 'strength_gained': 0.0, 'processed_sources': [], 'history': []})
        growth.setdefault('milk_feedings', 0)
        growth.setdefault('milk_units_consumed', 0.0)
        growth.setdefault('cronenberg_portions_eaten', 0)
        growth.setdefault('cronenberg_mass_consumed', 0.0)
        growth.setdefault('size_gained', 0.0)
        growth.setdefault('strength_gained', 0.0)
        growth.setdefault('processed_sources', [])
        growth.setdefault('history', [])
        return growth

    def feed_cat_milk(self, kitten, day, amount=1.0, source='mother'):
        growth = self.ensure_state(kitten)
        source_key = ('cat_milk', int(day))
        if source_key in growth['processed_sources']:
            return self._duplicate_event(kitten=kitten, source='cat_milk', day=day, amount=amount)
        amount = max(0.0, float(amount))
        size_gain = self.MILK_SIZE_GAIN * amount
        strength_gain = self.MILK_STRENGTH_GAIN * amount
        event = self._apply_growth(kitten=kitten, source='cat_milk', day=day, size_gain=size_gain, strength_gain=strength_gain, cronenberg_mass=0.0, metadata={'milk_amount': amount, 'provided_by': source})
        growth['milk_feedings'] += 1
        growth['milk_units_consumed'] += amount
        growth['processed_sources'].append(source_key)
        return event

    def feed_cronenberg_portion(self, kitten, day, mass, source):
        growth = self.ensure_state(kitten)
        source_key = (source, int(day))
        if source_key in growth['processed_sources']:
            return self._duplicate_event(kitten=kitten, source=source, day=day, amount=mass)
        mass = max(0.0, float(mass))
        size_gain = mass * self.SIZE_GAIN_PER_MASS
        strength_gain = mass * self.STRENGTH_GAIN_PER_MASS
        event = self._apply_growth(kitten=kitten, source=source, day=day, size_gain=size_gain, strength_gain=strength_gain, cronenberg_mass=mass, metadata={'portion_mass': mass})
        growth['cronenberg_portions_eaten'] += 1
        growth['cronenberg_mass_consumed'] += mass
        growth['processed_sources'].append(source_key)
        kitten.cronenbergs_eaten = int(getattr(kitten, 'cronenbergs_eaten', 0)) + 1
        kitten.cronenberg_mass_eaten = float(getattr(kitten, 'cronenberg_mass_eaten', 0.0)) + mass
        return event

    def feed_dead_delivery(self, kitten, day):
        return self.feed_cronenberg_portion(kitten=kitten, day=day, mass=self.DEAD_CRONENBERG_PORTION, source='mother_dead_cronenberg')

    def feed_father_delivery(self, kitten, day):
        return self.feed_cronenberg_portion(kitten=kitten, day=day, mass=self.FATHER_CRONENBERG_PORTION, source='father_dead_cronenberg')

    def feed_first_kill(self, kitten, day):
        return self.feed_cronenberg_portion(kitten=kitten, day=day, mass=self.FIRST_KILL_PORTION, source='first_training_kill')

    def feed_family_hunt(self, kitten, day):
        return self.feed_cronenberg_portion(kitten=kitten, day=day, mass=self.FAMILY_HUNT_PORTION, source='family_cronenberg_hunt')

    def _apply_growth(self, kitten, source, day, size_gain, strength_gain, cronenberg_mass, metadata):
        growth = self.ensure_state(kitten)
        previous_size = float(getattr(kitten, 'size', 1.0))
        previous_strength = float(getattr(kitten, 'strength', 1.0))
        new_size = previous_size + size_gain
        new_strength = previous_strength + strength_gain
        kitten.size = new_size
        kitten.strength = new_strength
        growth['size_gained'] += size_gain
        growth['strength_gained'] += strength_gain
        event = {'name': 'kitten_growth_applied', 'kitten': kitten.name, 'source': source, 'day': day, 'previous_size': previous_size, 'size_gain': size_gain, 'size': new_size, 'previous_strength': previous_strength, 'strength_gain': strength_gain, 'strength': new_strength, 'cronenberg_mass': cronenberg_mass, 'metadata': dict(metadata), 'grew': True}
        growth['history'].append(event)
        self._record(event)
        return event

    def _duplicate_event(self, kitten, source, day, amount=1.0):
        stored_energy = self.duplicate_energy.store(cat=kitten, source=source, day=day, amount=amount)
        event = {'name': 'kitten_growth_already_processed', 'kitten': kitten.name, 'source': source, 'day': day, 'amount_not_absorbed': float(amount), 'stored_energy': stored_energy, 'energy_conserved': True, 'grew': False}
        self._record(event)
        return event

    def _record(self, event):
        self.history.append(event)
        quantum_events = getattr(self.universe, 'quantum_events', None)
        if quantum_events is not None:
            quantum_events.append(event)
