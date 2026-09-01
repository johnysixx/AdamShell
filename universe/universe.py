from core.entity.social_entity import _entity_attr_setdefault
from lifecycle import LifeCycleSystem
from cats.cat_lifecycle import CatLifeCycleHandler
import uuid
from typing import Self
from core.entity.factory import EntityFactory
from cats import Cats
from core.entity.profile_resolver import EntityProfileResolver
from core.entity.quantum_die import QuantumDie
from core.entity.quantum_die_box import QuantumDieBox
from universe.quantum_universe_space import QuantumUniverseSpace
from universe.big_bang import BigBang
from core.entity.quantum_box import QuantumBox
from universe.universe_statistics import UniverseStatistics
from universe.cronenberg_population_statistics import CronenbergPopulationStatistics
from universe.logger import UniverseLogger
from core.entity.cronenberg import Cronenberg
from quantum.error_boundary import QuantumErrorBoundary
from quantum.event_bus import QuantumEventBus
from quantum.d20_registry import D20Registry
from quantum.quantum_die_resolver import QuantumDieResolver
from quantum.cronenberg_pair_encounter import CronenbergPairEncounter
from quantum.cronenberg_pair_encounter_resolver import CronenbergPairEncounterResolver
from universe.law_registry import LawRegistry
from quantum.death_ripple import QuantumDeathRipple
from cats.cronenberg_encounter import CatCronenbergEncounter
from quantum.cat_box_transfer import CatQuantumBoxTransfer
from cats.cat_door_registry import CatDoorRegistry
from universe.cat_recipient_registry import CatRecipientRegistry
from universe.aroma_residue import AromaResidue

class Universe:

    def __init__(self, universe_id=None):
        self.id = universe_id or 'root'
        self.entropy = 0
        self.pressure = 0
        self.universe_tick = 0
        self.universe_history = []
        self.energy_pool = 100
        self.last_pressure_cost = 0.0
        self.last_energy_gain = 0.0
        self.last_energy_delta = 0.0
        self.last_classical_entropy_delta = 0.0
        self.classical_entropy_total = 0.0
        self.max_entities = 50
        self.conflict_history = []
        self.conflict_pressure = 0
        self.threshold = 3
        self.entities = []
        self.entity_memory = {}
        self.physics_model = 'symbolic_classical'
        self.physics_layers = {'classical': True, 'quantum': False}
        self.quantum_die_resolver = QuantumDieResolver(self)
        self.cronenberg_pair_encounter = CronenbergPairEncounter()
        self.cronenberg_pair_encounter_resolver = CronenbergPairEncounterResolver(self)
        self.active_cronenberg_pair_encounters = set()
        self.quantum_die = QuantumDie(resolver=self.quantum_die_resolver)
        self.quantum_boxes = []
        self.quantum_events = []
        self.cronenbergs = []
        self.cronenberg_count = 0
        self.quantum_event_bus = QuantumEventBus()
        self.d20_registry = D20Registry()
        self.law_registry = LawRegistry()
        self.d20_registry.register(self.quantum_die)
        self.quantum_death_ripple = QuantumDeathRipple(self.d20_registry)
        self.cat_cronenberg_encounter = CatCronenbergEncounter()
        self.cat_box_transfer = CatQuantumBoxTransfer(self)
        self.cat_door_registry = CatDoorRegistry()
        self.cat_recipient_registry = CatRecipientRegistry()
        self.quantum_event_bus.subscribe('cronenberg_hunted', self.quantum_death_ripple.on_cronenberg_hunted)
        self.statistics = UniverseStatistics()
        self.cronenberg_population_statistics = CronenbergPopulationStatistics(self)
        self.quantum_state = {'enabled': False, 'superposition': False, 'observer': None, 'collapsed': False, 'tick_count': 0, 'collapse_count': 0, 'last_collapse_tick': None, 'uncertainty': 0.0, 'fluctuation': 0.0, 'entropy_delta': 0.0, 'entropy_total': 0.0}
        self.physics = {'light': False, 'space': False, 'time': False, 'gravity': False}
        self.world = {}
        self.big_bang = None
        self.big_bang_started = False
        self.physical_universe_started = False
        self.universe_exists = False
        self.state = 'pre_universe'
        self.factory = EntityFactory()
        self.quantum_error_boundary = QuantumErrorBoundary(cronenberg_factory=self.create_cronenberg_from_quantum_error)
        self.life_cycle_system = LifeCycleSystem(self)
        self.cat_life_cycle_handler = CatLifeCycleHandler(self)
        self.life_cycle_system.register(self.cat_life_cycle_handler)
        UniverseLogger.boot(f'Root reality prepared: {self.id}')
        UniverseLogger.boot('Physical universe has not started yet.')

    @property
    def snapshot(self):
        geometry_state = None
        if hasattr(self, 'quantum_space'):
            geometry_state = self.quantum_space.geometry_engine.public_state
        quantum_layer_map = {'tick': self.universe_tick, 'boxes': [box.public_state for box in self.quantum_boxes if getattr(box, 'current_layer', None) == 'quantum_layer'], 'space': self.quantum_space.public_state if hasattr(self, 'quantum_space') else {}}
        return {'universe_id': self.id, 'tick': self.universe_tick, 'energy': self.energy_pool, 'pressure': self.pressure, 'entropy': self.entropy, 'statistics': self.statistics.public_state, 'geometry': geometry_state, 'quantum_layer_map': quantum_layer_map}

    def start_big_bang(self):
        if self.big_bang_started:
            UniverseLogger.event('BIG BANG ALREADY STARTED')
            return self.world.get('big_bang')
        self.big_bang = BigBang(self)
        self.big_bang.explode()
        self.big_bang_started = True
        self.physical_universe_started = True
        self.universe_exists = True
        self.state = 'physical_universe'
        UniverseLogger.boot('PHYSICAL UNIVERSE STARTED')
        UniverseLogger.boot('THE UNIVERSE EXISTS')
        return self.world.get('big_bang')

    def hear(self, word):
        if word.name == 'LetThereBeLight':
            self.light = True
            UniverseLogger.event('Light is created.')
        elif word.name == 'LetThereBeSpace':
            self.space = True
            self.chaos = False
            self.order = True
            UniverseLogger.event('Space is separated from chaos.')
        elif word.name == 'LetThereBeDeep':
            self.deep = True
            UniverseLogger.event('The Deep emerges from void.')
        elif word.name == 'RewriteRule':
            self.rules_modified = True
            UniverseLogger.event('Reality rules are evolving...')

    def register_conflicts(self, conflicts):
        if not conflicts:
            return
        self.conflict_history.extend(conflicts)
        self.conflict_pressure += len(conflicts)
        self.check_threshold()
        self.spawn_entities_from_conflicts(conflicts)
        UniverseLogger.event(f'Ă˘ĹˇÂ\xa0 Conflict pressure increased: {self.conflict_pressure}')

    def check_threshold(self):
        if self.conflict_pressure >= self.threshold:
            UniverseLogger.event('Threshold reached reality shift triggered')
            self.trigger_reality_shift()

    def trigger_reality_shift(self):
        self.conflict_pressure = 0
        self.chaos = True
        self.create_entity('TheresholdEvent', streght=3)
        UniverseLogger.event('Reality Shifted new layer formed')

    def create_entity(self, name, streght=1, profile=None):
        entity = self.factory.create(name, self)
        if profile is None:
            profile = EntityProfileResolver.find_profile(world=self.world, technical_name=name)
        entity.profile = profile
        self.add_entity(entity)
        UniverseLogger.event(f'new entity created: {name}')
        return entity

    def spawn_entities_from_conflicts(self, conflicts):
        if not conflicts:
            return
        for c in conflicts:
            key = c['key']
            if key == 'light' and self.conflict_pressure > 1:
                self.create_entity('LightEcho', streght=1)
            if key == 'space' and self.conflict_pressure > 1:
                self.create_entity('VoidRipple', streght=1)
            if key == 'deep' and self.conflict_pressure > 1:
                self.create_entity('AbyssSeed', streght=1)

    def tick(self):
        return self.tick_universe()

    def add_entity(self, entity):
        entity.universe = self
        self.entities.append(entity)
        UniverseLogger.event(f'New entity added: {entity.name}')
        entity_type = getattr(entity, 'type', None)
        world_entity = self.world.get(entity.name)
        if entity_type is None and isinstance(world_entity, dict):
            entity_type = world_entity.get('type')
        meeting_place = getattr(self, 'meeting_place', None)
        if meeting_place is None:
            return
        if entity_type == 'cat':
            meeting_place.glass_shelf.appear_shared_glass(kind='beer_mug')
        elif entity_type == 'cronenberg':
            meeting_place.glass_shelf.appear_shared_glass(kind='shot_glass')
        profile = getattr(entity, 'profile', None)
        decision = meeting_place.bar_entity_policy.resolve(profile=profile, technical_name=entity.name)
        entity.bar_policy = decision
        meeting_place.glass_shelf.register_policy_decision(decision)

    def update_physics(self):
        self.last_classical_entropy_delta = len(self.entities) * 0.01
        self.classical_entropy_total += self.last_classical_entropy_delta
        self.entropy += self.last_classical_entropy_delta
        if self.quantum_state['enabled']:
            self.entropy += self.quantum_state['entropy_delta']
        self.pressure = self.entropy / (len(self.entities) + 1)
        if 'spacetime' in self.world:
            self.pressure += self.world['spacetime']['curvature']
        self.energy_pool += len(self.entities) * 0.02
        self.last_energy_gain = 0.05
        self.energy_pool += self.last_energy_gain
        self.last_pressure_cost = self.pressure * 0.1
        self.energy_pool -= self.last_pressure_cost
        self.last_energy_delta = self.last_energy_gain - self.last_pressure_cost

    def enable_physics(self, law):
        if law == 'time':
            self.physics['time'] = {'tick': 0, 'flow': 1.0, 'state': 'linear', 'pressure': 0.0}
            UniverseLogger.event('Physics enabled: time')
            return
        if law == 'gravity':
            self.physics['gravity'] = {'enabled': True, 'strength': 1.0, 'curvature_effect': 0.01}
            UniverseLogger.event('Physics enabled: gravity')
            return
        self.physics[law] = True
        UniverseLogger.event(f'Physics enabled: {law}')

    def enable_quantum_layer(self):
        self.physics_layers['quantum'] = True
        self.quantum_state['enabled'] = True
        self.physics_model = 'symbolic_quantum'
        if not hasattr(self, 'quantum_die_box'):
            self.quantum_die_box = QuantumDieBox(self.quantum_die)
        if not hasattr(self, 'quantum_space'):
            self.quantum_space = QuantumUniverseSpace(self.quantum_die_box)
        UniverseLogger.event('Quantum layers enabled')

    def boot_physics(self):
        self.enable_physics('light')
        self.enable_physics('time')
        self.enable_physics('gravity')
        self.enable_physics('space')
        self.enable_physics('energy')
        self.bind_spacetime()
        UniverseLogger.event('Physics booted')
        UniverseLogger.event(f'Physics model: {self.physics_model}')
        UniverseLogger.event(f"Physics layers: classical={self.physics_layers['classical']} quantum={self.physics_layers['quantum']} ")
        UniverseLogger.event(f"Quantum state: enabled={self.quantum_state['enabled']} superposition={self.quantum_state['superposition']} collapsed={self.quantum_state['collapsed']}")

    def tick_time(self):
        if 'time' in self.physics:
            t = self.physics['time']
            t['tick'] += 1
            t['pressure'] += 0.1 * t['flow']
            self.energy_pool -= t['pressure'] * 0.1
            UniverseLogger.event(f"TIME={t['tick']}  PRESSURE={t['pressure']:.2f}  ENERGY={self.energy_pool:.2f}")

    def get_time(self):
        return self.physics['time']['tick']

    def get_energy(self):
        return self.energy_pool

    def bind_spacetime(self):
        self.world['spacetime'] = {'linked': True, 'curvature': 0.0, 'time_axis': {'tick': 0, 'flow': 1.0, 'state': 'global'}, 'space_axis': {'dimensions': 3, 'state': 'global', 'expanded': True}}
        UniverseLogger.event('time and space are bound into spacetime')

    def tick_spacetime(self):
        if 'spacetime' not in self.world:
            UniverseLogger.event('No spacetime bound yet')
            return
        spacetime = self.world['spacetime']
        spacetime['time_axis']['tick'] += 1
        gravity = self.physics['gravity']
        curvature_delta = 0.0
        if gravity and gravity['enabled']:
            curvature_delta = gravity['curvature_effect'] * gravity['strength']
            spacetime['curvature'] += curvature_delta
            UniverseLogger.event(f"SPACETIME TICK={spacetime['time_axis']['tick']} DELTA={curvature_delta:.2f} CURVATURE={spacetime['curvature']:.2f}")

    def open_quantum_box(self, box_id, observer=None, rng=None):
        return self.quantum_error_boundary.execute(operation=lambda: self._open_quantum_box_unprotected(box_id=box_id, observer=observer, rng=rng), source_component='quantum_box', source_operation='open_quantum_box')

    def _open_quantum_box_unprotected(self, box_id, observer=None, rng=None):
        box = next((quantum_box for quantum_box in self.quantum_boxes if quantum_box.id == box_id), None)
        if box is None:
            UniverseLogger.event(f'QUANTUM BOX NOT FOUND: {box_id}')
            return None
        result = box.collapse_state(cause='opened', observer=observer, tick=self.quantum_state['tick_count'], rng=rng)
        self.statistics.record_quantum_collapse()
        if result == 'cat':
            manifestation = self.manifest_cat(name=f'cat_from_{box.id}', source='quantum_box_opened', position=box.position)
            event = manifestation['event']
            event['collapse_cause'] = 'opened'
            event['box_id'] = box.id
            event['observer'] = observer
            UniverseLogger.event(f'CAT JUMPS OUT OF QUANTUM BOX: {box.id}')
        else:
            event = {'name': 'empty_quantum_box_opened', 'collapse_cause': 'opened', 'box_id': box.id, 'position': box.position.copy(), 'observer': observer, 'tick': self.quantum_state['tick_count']}
            UniverseLogger.event(f'QUANTUM BOX WAS EMPTY: {box.id}')
        self.quantum_boxes.remove(box)
        self.statistics.record_quantum_box_disappeared()
        UniverseLogger.event(f'QUANTUM BOX DISAPPEARED: {box.id}')
        return event

    def manifest_cat(self, name, source, position=None, color='black', fur_length='short', pattern='solid', eye_color='green', sex='female'):
        cats = getattr(self, 'cats_layer', None)
        if cats is None:
            cats = Cats(self)
            self.cats_layer = cats
        cat = cats.create_cat(name=name, color=color, fur_length=fur_length, pattern=pattern, eye_color=eye_color, sex=sex, origin=source)
        if cat is None:
            return None
        if position is not None:
            cat.position = dict(position)
        if source in {'quantum_box_opened', 'quantum_box_spontaneous_collapse'}:
            self._prepare_quantum_box_cat(cat=cat, source=source)
        entity = self.create_entity(name=name, profile=cat)
        entity.cat_data = cat
        event = {'name': 'cat_manifested', 'cat': name, 'source': source, 'position': dict(position) if position is not None else None, 'tick': self.quantum_state['tick_count']}
        self.quantum_events.append(event)
        self.statistics.record_cat_created()
        UniverseLogger.event(f'CAT MANIFESTED: {name} FROM={source}')
        return {'cat': cat, 'entity': entity, 'event': event}

    def _prepare_quantum_box_cat(self, cat, source):
        learning = cat.learning
        cat.age_days = 98
        cat.developmental_stage = 'juvenile'
        cat.quantum_box_origin = {'manifested_from_box': True, 'source': source, 'born_in_quantum_layer': True}
        traits = _entity_attr_setdefault(cat, 'special_traits', [])
        for trait in ('quantum_box_cat', 'juvenile_quantum_cat', 'sees_direct_path_to_bar'):
            if trait not in traits:
                traits.append(trait)
        meow = learning['meow_knowledge']
        meow.update({'learned': True, 'understood': True, 'can_speak': True, 'teacher': None, 'source': 'quantum_box_cat_wisdom', 'learned_on_day': 0})
        learning['adult_meowing_learned'] = True
        learning['human_communication_learned'] = True
        for skill in learning['skills'].values():
            skill.update({'learned': True, 'progress': 1.0, 'teacher': None, 'learned_on_day': 0})
        learning['complete'] = True
        learning['teaching_required'] = False
        feline_wisdom = _entity_attr_setdefault(cat, 'feline_wisdom', {'awareness': {}, 'abilities': {}, 'history': []})
        feline_wisdom['abilities'].pop('teach_other_cats', None)
        feline_wisdom['abilities'].pop('teach_teaching', None)
        cat.state = 'juvenile_cat_from_quantum_box'
        return cat

    def create_quantum_box(self, rng=None, layer='quantum_layer'):
        box = QuantumBox(rng=rng)
        box.current_layer = layer
        self.quantum_boxes.append(box)
        self.statistics.record_quantum_box_created()
        UniverseLogger.event(f"QUANTUM BOX CREATED: {box.id} AT x={box.position['x']:.3f} y={box.position['y']:.3f} z={box.position['z']:.3f}")
        return box

    def should_collapse_quantum_box(self, box, rng=None):
        import random
        rng = rng or random
        base_chance = 0.01
        age_factor = box.age_ticks * 0.001
        collapse_chance = min(base_chance + age_factor, 0.25)
        return rng.random() < collapse_chance

    def create_cronenberg_from_quantum_error(self, error, source_component, source_operation):
        cronenberg = Cronenberg(error=error, source_component=source_component, source_operation=source_operation, quantum_tick=self.quantum_state['tick_count'])
        self.cronenbergs.append(cronenberg)
        self.cronenberg_count += 1
        self.add_entity(cronenberg)
        event = {'name': 'cronenberg_manifested', 'type': 'quantum_error_manifestation', 'cronenberg_id': cronenberg.id, 'source_component': source_component, 'source_operation': source_operation, 'error_type': type(error).__name__, 'error_message': str(error), 'quantum_tick': self.quantum_state['tick_count']}
        self.quantum_events.append(event)
        UniverseLogger.event(f'CRONENBERG MANIFESTED: {cronenberg.id} FROM={source_component}.{source_operation} ERROR={type(error).__name__}')
        return cronenberg

    def tick_quantum_unprotected(self):
        if not self.quantum_state['enabled']:
            return
        self.quantum_state['tick_count'] += 1
        self.quantum_state['collapsed'] = False
        self.quantum_state['superposition'] = True
        self.quantum_state['observer'] = 'quantum_tick'
        self.quantum_state['fluctuation'] += 0.01
        self.quantum_state['uncertainty'] = self.quantum_state['fluctuation'] * 0.5
        self.quantum_state['entropy_delta'] = self.quantum_state['uncertainty'] * 0.1
        self.quantum_state['entropy_total'] += self.quantum_state['entropy_delta']
        self.quantum_state['superposition'] = False
        self.quantum_state['collapsed'] = True
        self.quantum_state['collapse_count'] += 1
        self.quantum_state['last_collapse_tick'] = self.quantum_state['tick_count']
        for box in list(self.quantum_boxes):
            box.age_ticks += 1
            if not self.should_collapse_quantum_box(box):
                continue
            result = box.collapse_state(cause='spontaneous', observer=None, tick=self.quantum_state['tick_count'])
            self.statistics.record_quantum_collapse()
            if result == 'cat':
                manifestation = self.manifest_cat(name=f'cat_from_{box.id}', source='quantum_box_spontaneous_collapse', position=box.position)
                event = manifestation['event']
                event['collapse_cause'] = 'spontaneous'
                event['box_id'] = box.id
                event['observer'] = None
                UniverseLogger.event(f'CAT MANIFESTS FROM SPONTANEOUS QUANTUM COLLAPSE: {box.id}')
            else:
                UniverseLogger.event(f'SPONTANEOUSLY COLLAPSED BOX WAS EMPTY: {box.id}')
            self.quantum_boxes.remove(box)
            self.statistics.record_quantum_box_disappeared()
            UniverseLogger.event(f'QUANTUM BOX DISAPPEARED: {box.id}')
        UniverseLogger.event(f"QUANTUM TICK FLUCTUATION={self.quantum_state['fluctuation']:.2f} UNCERTAINTY={self.quantum_state['uncertainty']:.3f} QENTROPY={self.quantum_state['entropy_delta']:.4f} ")

    def tick_quantum(self):
        if not self.quantum_state['enabled']:
            return None
        return self.quantum_error_boundary.execute(operation=self.tick_quantum_unprotected, source_component='universe', source_operation='tick_quantum')

    def record_universe_state(self):
        curvature = 0.0
        if 'spacetime' in self.world:
            curvature = self.world['spacetime']['curvature']
        snapshot = {'tick': self.universe_tick, 'energy': self.energy_pool, 'gain': self.last_energy_gain, 'cost': self.last_pressure_cost, 'delta': self.last_energy_delta, 'classical_entropy_delta': self.last_classical_entropy_delta, 'classical_entropy_total': self.classical_entropy_total, 'entropy': self.entropy, 'pressure': self.pressure, 'curvature': curvature, 'physics_model': self.physics_model, 'quantum_enabled': self.quantum_state['enabled'], 'quantum_fluctuation': self.quantum_state['fluctuation'], 'quantum_uncertainty': self.quantum_state['uncertainty'], 'quantum_entropy_delta': self.quantum_state['entropy_delta'], 'quantum_entropy_total': self.quantum_state['entropy_total']}
        self.universe_history.append(snapshot)

    def resolve_quantum_pair_consumption(self, first, second):
        if not first._is_quantum_counterpart_of(second):
            raise ValueError('Cronenbergs are not quantum counterparts.')
        if not first.active or not second.active:
            raise ValueError('Quantum pair consumption requires two active Cronenbergs.')
        pair_id = first.quantum_state.pair_id
        combined_size = float(first.size) + float(second.size)
        combined_energy = max(0.0, float(first.energy)) + max(0.0, float(second.energy))
        retained_energy = combined_energy * 0.4
        released_energy = combined_energy * 0.35
        dark_energy = combined_energy * 0.25
        recombined_size = combined_size * 0.5
        recombined = Cronenberg(error=RuntimeError('Quantum counterpart consumption caused recombination.'), source_component='cronenberg_quantum_pair_consumption', source_operation='consume', quantum_tick=self.quantum_state['tick_count'])
        recombined.state = 'born_from_quantum_pair_consumption'
        recombined.location = first.location
        recombined.current_layer = getattr(first, 'current_layer', None)
        recombined.size = recombined_size
        recombined.juice_value = recombined_size
        recombined.energy = retained_energy
        recombined.age = max(first.age, second.age)
        recombined.quantum_state.reset(spin=0.0)
        recombined.recombined_from = [first.id, second.id]
        recombined.origin.mark_recombined(
            source_ids=recombined.recombined_from,
            former_pair_id=pair_id,
            consumption_location=first.location,
            released_energy=released_energy,
            dark_energy_created=dark_energy,
        )
        first.active = False
        second.active = False
        first.state = 'destroyed_by_quantum_pair_consumption'
        second.state = 'destroyed_by_quantum_pair_consumption'
        first.location = 'quantum_consumption_history'
        second.location = 'quantum_consumption_history'
        first.recombined_into = recombined.id
        second.recombined_into = recombined.id
        first.quantum_state.disentangle()
        second.quantum_state.disentangle()
        self.energy_pool += released_energy
        if not hasattr(self, 'dark_energy'):
            self.dark_energy = 0.0
        self.dark_energy += dark_energy
        self.cronenbergs.append(recombined)
        self.cronenberg_count += 1
        self.add_entity(recombined)
        event = {'name': 'cronenberg_quantum_pair_consumed', 'pair_id': pair_id, 'participants': [first.id, second.id], 'recombined_id': recombined.id, 'combined_size': combined_size, 'recombined_size': recombined_size, 'combined_energy': combined_energy, 'retained_energy': retained_energy, 'released_energy': released_energy, 'dark_energy_created': dark_energy, 'tick': self.quantum_state['tick_count']}
        self.quantum_events.append(event)
        UniverseLogger.event(f'CRONENBERG QUANTUM PAIR CONSUMED: {first.id} <-> {second.id} -> {recombined.id}')
        return {'result': 'quantum_pair_consumption_recombined', 'first': first, 'second': second, 'recombined': recombined, 'event': event}

    def merge_cronenberg_quantum_pair(self, first, second, source='cronenberg_quantum_pair_encounter'):
        if first is second:
            raise ValueError('Quantum merge requires two different Cronenbergs.')
        if first not in self.cronenbergs:
            raise ValueError('First Cronenberg is not registered.')
        if second not in self.cronenbergs:
            raise ValueError('Second Cronenberg is not registered.')
        first_pair_id = first.quantum_state.pair_id
        second_pair_id = second.quantum_state.pair_id
        if first_pair_id is None or first_pair_id != second_pair_id:
            raise ValueError('Cronenbergs do not belong to the same quantum pair.')
        if first.quantum_state.counterpart_id != second.id or second.quantum_state.counterpart_id != first.id:
            raise ValueError('Cronenbergs are not mutual quantum counterparts.')
        if not first.active or not second.active:
            raise ValueError('Only active Cronenbergs can merge.')
        merged = Cronenberg(error=RuntimeError('Cronenberg quantum pair merged.'), source_component='cronenberg_quantum_pair_merge', source_operation=source, quantum_tick=self.quantum_state['tick_count'])
        merged.state = 'born_from_quantum_merge'
        merged.location = first.location
        merged.current_layer = getattr(first, 'current_layer', None)
        merged.size = float(first.size) + float(second.size)
        merged.energy = float(first.energy) + float(second.energy)
        merged.juice_value = merged.size
        merged.age = max(first.age, second.age)
        merged.quantum_state.reset(spin=0.0)
        merged.merged_from = [first.id, second.id]
        merged.origin.mark_merged(
            source_ids=merged.merged_from,
            former_pair_id=first_pair_id,
            merge_location=first.location,
        )
        first.active = False
        second.active = False
        first.state = 'quantum_merged'
        second.state = 'quantum_merged'
        first.merged_into = merged.id
        second.merged_into = merged.id
        first.location = 'merged_history'
        second.location = 'merged_history'
        first.quantum_state.disentangle()
        second.quantum_state.disentangle()
        self.cronenbergs.append(merged)
        self.cronenberg_count += 1
        self.add_entity(merged)
        event = {'name': 'cronenberg_quantum_pair_merged', 'pair_id': first_pair_id, 'parents': [first.id, second.id], 'merged_id': merged.id, 'merged_size': merged.size, 'merged_energy': merged.energy, 'merged_spin': merged.quantum_state.spin, 'source': source, 'tick': self.quantum_state['tick_count']}
        self.quantum_events.append(event)
        UniverseLogger.event(f'CRONENBERG QUANTUM PAIR MERGED: {first.id} + {second.id} -> {merged.id}')
        return {'result': 'quantum_pair_merged', 'first': first, 'second': second, 'merged': merged, 'event': event}

    def create_cronenberg_quantum_counterpart(self, original, source='serpent_d20_hidden_roll'):
        if original not in self.cronenbergs:
            raise ValueError('Original Cronenberg is not registered in this universe.')
        if not getattr(original, 'is_alive', False):
            raise ValueError('Quantum counterpart requires a living Cronenberg.')
        existing_counterpart_id = original.quantum_state.counterpart_id
        if existing_counterpart_id is not None:
            existing = next((cronenberg for cronenberg in self.cronenbergs if cronenberg.id == existing_counterpart_id), None)
            if existing is not None:
                return {'result': 'counterpart_already_exists', 'original': original, 'counterpart': existing, 'pair_id': original.quantum_state.pair_id}
        pair_id = f'cronenberg_pair_{uuid.uuid4().hex[:8]}'
        counterpart = Cronenberg(error=RuntimeError('Cronenberg quantum counterpart manifestation.'), source_component='cronenberg_quantum_counterpart', source_operation=source, quantum_tick=self.quantum_state['tick_count'])
        counterpart.size = original.size
        counterpart.juice_value = original.juice_value
        counterpart.energy = original.energy
        counterpart.age = original.age
        counterpart.state = 'born_as_quantum_counterpart'
        counterpart.location = 'quantum_layer'
        counterpart.quantum_state.pair_with(
            pair_id=pair_id,
            counterpart_id=original.id,
            spin=-float(original.quantum_state.spin),
        )
        original.quantum_state.pair_with(
            pair_id=pair_id,
            counterpart_id=counterpart.id,
        )
        metadata = {'pair_id': pair_id, 'created_by': source, 'spin_relation': 'opposite'}
        original.quantum_link_system.add_link(target_id=counterpart.id, link_type='quantum_counterpart', strength=1.0, created_tick=self.quantum_state['tick_count'], metadata=metadata)
        counterpart.quantum_link_system.add_link(target_id=original.id, link_type='quantum_counterpart', strength=1.0, created_tick=self.quantum_state['tick_count'], metadata=metadata)
        counterpart.origin.mark_counterpart(
            counterpart_of=original.id,
            pair_id=pair_id,
        )
        self.cronenbergs.append(counterpart)
        self.cronenberg_count += 1
        self.add_entity(counterpart)
        event = {'name': 'cronenberg_quantum_counterpart_created', 'original_id': original.id, 'counterpart_id': counterpart.id, 'pair_id': pair_id, 'original_spin': original.quantum_state.spin, 'counterpart_spin': counterpart.quantum_state.spin, 'source': source, 'tick': self.quantum_state['tick_count']}
        self.quantum_events.append(event)
        UniverseLogger.event(f'CRONENBERG QUANTUM COUNTERPART CREATED: {original.id} <-> {counterpart.id}')
        return {'result': 'counterpart_created', 'original': original, 'counterpart': counterpart, 'pair_id': pair_id, 'event': event}

    def trigger_quantum_error(self, error, source_component, source_operation):
        if not isinstance(error, Exception):
            raise TypeError('Quantum error must be an Exception.')

        def broken_quantum_operation():
            raise error
        return self.quantum_error_boundary.execute(operation=broken_quantum_operation, source_component=source_component, source_operation=source_operation)

    def trigger_test_quantum_error(self):
        return self.trigger_quantum_error(error=RuntimeError('Test quantum geometry failure.'), source_component='quantum_geometry_engine', source_operation='test_failure')

    def detect_cronenberg_pair_encounters(self):
        active_cronenbergs = [cronenberg for cronenberg in self.cronenbergs if getattr(cronenberg, 'active', True) and cronenberg.is_alive and (cronenberg.quantum_state.pair_id is not None)]
        current_encounters = set()
        detected_events = []
        processed_pair_ids = set()
        cronenbergs_by_id = {cronenberg.id: cronenberg for cronenberg in active_cronenbergs}
        for first in active_cronenbergs:
            counterpart_id = first.quantum_state.counterpart_id
            second = cronenbergs_by_id.get(counterpart_id)
            if second is None:
                continue
            pair_id = first.quantum_state.pair_id
            if pair_id in processed_pair_ids:
                continue
            processed_pair_ids.add(pair_id)
            encounter_key = (pair_id, first.location)
            if first.location != second.location:
                continue
            current_encounters.add(encounter_key)
            if encounter_key in self.active_cronenberg_pair_encounters:
                continue
            event = self.cronenberg_pair_encounter.detect(first, second, universe_tick=self.universe_tick)
            if not event.get('encountered', False):
                continue
            resolution = self.cronenberg_pair_encounter_resolver.resolve(first=first, second=second, encounter_event=event)
            event['resolution'] = resolution
            self.quantum_events.append(event)
            detected_events.append(event)
            UniverseLogger.event(f'CRONENBERG QUANTUM PAIR ENCOUNTERED: {pair_id} AT={first.location}')
        self.active_cronenberg_pair_encounters = current_encounters
        return detected_events

    def tick_entities(self):
        results = []
        for entity in list(self.entities):
            if not getattr(entity, 'active', True):
                continue
            tick = getattr(entity, 'tick', None)
            if not callable(tick):
                continue
            entity_name = getattr(entity, 'name', entity.__class__.__name__)
            result = self._run_tick_operation(phase='entities', operation=tick, source_component=f'entity:{entity_name}', source_operation='tick', args=(self,))
            results.append(result)
        encounters = self._run_tick_operation(phase='entities', operation=self.detect_cronenberg_pair_encounters, source_component='universe', source_operation='detect_cronenberg_pair_encounters')
        results.append(encounters)
        return results

    def _tick_aroma_residues(self):
        for box in getattr(self, 'quantum_boxes', []):
            AromaResidue.decay(box, ticks=1)
        cats_world = self.world.get('cats', {})
        if isinstance(cats_world, dict):
            cats = cats_world.get('cats', [])
        else:
            cats = []
        for cat in cats:
            AromaResidue.decay(cat, ticks=1)

    def _run_tick_operation(self, phase, operation, source_component, source_operation, args=None, kwargs=None):
        args = tuple(args or ())
        kwargs = dict(kwargs or {})
        try:
            value = operation(*args, **kwargs)
            return {'phase': phase, 'source_component': source_component, 'source_operation': source_operation, 'ok': True, 'result': value}
        except Exception as error:
            UniverseLogger.event(f'UNIVERSE TICK ERROR: PHASE={phase} SOURCE={source_component}.{source_operation} ERROR={type(error).__name__}: {error}')
            cronenberg = self.create_cronenberg_from_quantum_error(error=error, source_component=source_component, source_operation=source_operation)
            return {'phase': phase, 'source_component': source_component, 'source_operation': source_operation, 'ok': False, 'error_type': type(error).__name__, 'error_message': str(error), 'cronenberg_id': getattr(cronenberg, 'id', None)}

    def _run_optional_tick(self, phase, target, source_component):
        if target is None:
            return {'phase': phase, 'source_component': source_component, 'source_operation': 'tick', 'ok': True, 'skipped': True, 'reason': 'component_not_present'}
        tick = getattr(target, 'tick', None)
        if not callable(tick):
            return {'phase': phase, 'source_component': source_component, 'source_operation': 'tick', 'ok': True, 'skipped': True, 'reason': 'component_has_no_tick'}
        return self._run_tick_operation(phase=phase, operation=tick, source_component=source_component, source_operation='tick')

    def tick_universe(self):
        self.universe_tick += 1
        report = {'tick': self.universe_tick, 'phases': [], 'errors': [], 'cronenbergs_created': []}

        def record(result):
            report['phases'].append(result)
            if not result.get('ok', True):
                report['errors'].append(result)
                cronenberg_id = result.get('cronenberg_id')
                if cronenberg_id is not None:
                    report['cronenbergs_created'].append(cronenberg_id)
            return result
        record(self._run_optional_tick(phase='layers', target=getattr(self, 'layers', None), source_component='layers'))
        record(self._run_optional_tick(phase='idea_universe', target=getattr(self, 'idea_universe', None), source_component='idea_universe'))
        record(self._run_tick_operation(phase='aroma', operation=self._tick_aroma_residues, source_component='universe', source_operation='tick_aroma_residues'))
        record(self._run_tick_operation(phase='spacetime', operation=self.tick_spacetime, source_component='universe', source_operation='tick_spacetime'))
        record(self._run_tick_operation(phase='quantum', operation=self.tick_quantum, source_component='universe', source_operation='tick_quantum'))
        record(self._run_tick_operation(phase='physics', operation=self.update_physics, source_component='universe', source_operation='update_physics'))
        record(self._run_tick_operation(phase='biology', operation=self.life_cycle_system.tick_day, source_component='life_cycle_system', source_operation='tick_day'))
        entity_results = self.tick_entities()
        for entity_result in entity_results:
            record(entity_result)
        record(self._run_optional_tick(phase='cats', target=getattr(self, 'cats_layer', None), source_component='cats'))
        record(self._run_optional_tick(phase='meeting_place', target=getattr(self, 'meeting_place', None), source_component='meeting_place'))
        record(self._run_tick_operation(phase='statistics', operation=self.cronenberg_population_statistics.record_snapshot, source_component='cronenberg_population_statistics', source_operation='record_snapshot'))
        history_result = record(self._run_tick_operation(phase='history', operation=self.record_universe_state, source_component='universe', source_operation='record_universe_state'))
        if history_result.get('ok') and self.universe_history:
            last_snapshot = self.universe_history[-1]
            UniverseLogger.event(f"UNIVERSE TICK={self.universe_tick} HISTORY={len(self.universe_history)} MODEL={last_snapshot.get('physics_model', 'unknown')} QUANTUM={last_snapshot.get('quantum_enabled', False)} QFLUCT={last_snapshot.get('quantum_fluctuation', 0.0):.2f} QUNCERT={last_snapshot.get('quantum_uncertainty', 0.0):.3f} QENTROPY={last_snapshot.get('quantum_entropy_delta', 0.0):.4f} QTOTAL={last_snapshot.get('quantum_entropy_total', 0.0):.4f} CENTROPY={last_snapshot.get('classical_entropy_delta', 0.0):.4f} CTOTAL={last_snapshot.get('classical_entropy_total', 0.0):.4f} ENERGY={self.energy_pool:.4f} GAIN={self.last_energy_gain:.4f} COST={self.last_pressure_cost:.4f} DELTA={self.last_energy_delta:.4f} ENTROPY={self.entropy:.4f} PRESSURE={self.pressure:.4f} CURVATURE={last_snapshot.get('curvature', 0.0):.2f}")
        report['ok'] = not report['errors']
        report['error_count'] = len(report['errors'])
        report['cronenberg_count'] = self.cronenberg_count
        UniverseLogger.event(f"UNIVERSE TICK COMPLETE: TICK={self.universe_tick} ERRORS={report['error_count']} CRONENBERGS={len(report['cronenbergs_created'])}")
        return report
