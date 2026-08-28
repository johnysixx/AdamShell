import random
import uuid
from core.entity.quantum_cat_route import QuantumCatRoute
from quantum.geometry_engine import QuantumGeometryEngine
from navigation import NavigationEngine

class QuantumUniverseSpace:

    def __init__(self, quantum_die_box):
        self.name = 'quantum_universe_space'
        self.type = 'quantum_space'
        self.quantum_die_box = quantum_die_box
        self.geometry_engine = QuantumGeometryEngine()
        self.navigation_engine = NavigationEngine()
        self.configuration_id = None
        self.configuration_seed = None
        self.reconfiguration_count = 0
        self.reconfiguration_chance = 0.15
        self.staircases = []
        self.cat_routes = []
        self.bar_front_door = {'name': 'bar_front_door', 'position': {'x': 0.0, 'y': 0.0, 'z': 0.0}}
        self.reconfigure(cause='initialization')

    def generate_space_sample(self, sample_key, count=8):
        if self.configuration_seed is None:
            raise RuntimeError('Quantum space has no configuration seed.')
        local_rng = random.Random(f'{self.configuration_seed}:{sample_key}')
        return [{'id': f'generated_staircase_{sample_key}_{index}', 'origin': {'x': local_rng.uniform(-10.0, 10.0), 'y': local_rng.uniform(-10.0, 10.0), 'z': local_rng.uniform(-10.0, 10.0)}, 'destination': {'x': local_rng.uniform(-10.0, 10.0), 'y': local_rng.uniform(-10.0, 10.0), 'z': local_rng.uniform(-10.0, 10.0)}, 'orientation': local_rng.choice(['up', 'down', 'left', 'right', 'inverted', 'impossible']), 'length': local_rng.uniform(1.0, 8.0)} for index in range(count)]

    def get_active_cat_routes(self):
        return [route for route in self.cat_routes if route.observation_active]

    def reconfigure(self, cause, rng=None):
        rng = rng or random
        active_routes = self.get_active_cat_routes()
        new_staircases = []
        target_count = rng.randint(8, 16)
        missing_count = target_count
        for _ in range(missing_count):
            staircase_id = f'staircase_{uuid.uuid4().hex[:8]}'
            new_staircases.append({'id': staircase_id, 'origin': {'x': rng.uniform(-10.0, 10.0), 'y': rng.uniform(-10.0, 10.0), 'z': rng.uniform(-10.0, 10.0)}, 'destination': {'x': rng.uniform(-10.0, 10.0), 'y': rng.uniform(-10.0, 10.0), 'z': rng.uniform(-10.0, 10.0)}, 'orientation': rng.choice(['up', 'down', 'left', 'right', 'inverted', 'impossible']), 'length': rng.uniform(1.0, 8.0)})
        self.staircases = new_staircases
        self.configuration_seed = rng.randint(0, 2 ** 63 - 1)
        self.configuration_id = f'quantum_configuration_{self.configuration_seed}'
        self.geometry_engine.configure(self.configuration_seed)
        self.reconfiguration_count += 1
        self.quantum_die_box.move_to({'x': 0.0, 'y': 0.0, 'z': 0.0})
        print(f'QUANTUM SPACE RECONFIGURED CAUSE={cause} CONFIG={self.configuration_id} ACTIVE_CAT_ROUTES={len(active_routes)}')

    def quantum_tick(self, rng=None):
        rng = rng or random
        if rng.random() >= self.reconfiguration_chance:
            return False
        self.reconfigure(cause='unobserved_quantum_tick', rng=rng)
        return True

    def collapse_reconfiguration(self, rng=None):
        self.reconfigure(cause='wave_function_collapse', rng=rng)

    def _get_cat_memory(self, cat):
        return getattr(cat, 'memory', None)

    def _remember_cat_route_event(self, cat, route, universe, event_type, details=None):
        memory = self._get_cat_memory(cat)
        if memory is None:
            return None
        route_details = {'route_id': route.route_id, 'destination': route.destination, 'start_position': dict(route.start_position), 'current_position': dict(route.current_position), 'current_step_index': route.current_step_index, 'next_position': route.next_position, 'route_state': route.state, 'has_arrived': route.has_arrived}
        route_details.update(details or {})
        return memory.remember(event_type=event_type, universe_tick=getattr(universe, 'universe_tick', None), location=dict(route.current_position), participants=[], details=route_details)

    def plan_direct_cat_route(self, cat_id, start_position, destination_position, destination, step_size=None):
        plan = self.navigation_engine.direct_route(start_position=start_position, destination_position=destination_position, step_size=step_size)
        route = self.create_cat_route(cat_id=cat_id, route_steps=plan['route_steps'], start_position=start_position, destination=destination)
        return {'name': 'cat_direct_route_planned', 'cat_id': cat_id, 'destination': destination, 'plan': plan, 'route': route}

    def plan_cat_route_to_nearest_huntable_cronenberg(self, cat, cronenbergs, start_position=None, step_size=None, max_size_ratio=1.2):
        cat_id = getattr(cat, 'name', None)
        cat_size = float(getattr(cat, 'size', 1.0))
        if start_position is None:
            start_position = getattr(cat, 'position', None)
        if start_position is None:
            return {'name': 'cat_hunt_route_not_planned', 'result': 'cat_has_no_position', 'cat_id': cat_id}
        huntable = [cronenberg for cronenberg in cronenbergs if getattr(cronenberg, 'active', True) and getattr(cronenberg, 'is_alive', False) and (getattr(cronenberg, 'position', None) is not None) and (float(cronenberg.size) / cat_size <= float(max_size_ratio))]
        nearest = self.navigation_engine.nearest_target(start_position, huntable)
        if nearest is None:
            return {'name': 'cat_hunt_route_not_planned', 'result': 'no_huntable_cronenberg', 'cat_id': cat_id}
        target = nearest['target']
        planned = self.plan_direct_cat_route(cat_id=cat_id, start_position=start_position, destination_position=nearest['position'], destination=target.id, step_size=step_size)
        planned['name'] = 'cat_route_to_nearest_huntable_cronenberg_planned'
        planned['target'] = target
        planned['target_id'] = target.id
        planned['target_distance'] = nearest['distance']
        return planned

    def plan_cat_route_to_bar(self, cat_id, start_position, step_size=None):
        return self.plan_direct_cat_route(cat_id=cat_id, start_position=start_position, destination_position=self.bar_front_door['position'], destination='bar_front_door', step_size=step_size)

    def create_cat_route(self, cat_id, route_steps, start_position, destination='bar_front_door'):
        route = QuantumCatRoute(cat_id=cat_id, route_steps=route_steps, start_position=start_position, destination=destination)
        self.cat_routes.append(route)
        return route

    def find_cat_route(self, cat_id):
        return next((route for route in self.cat_routes if route.cat_id == cat_id and route.observation_active), None)

    def advance_cat_route(self, cat, cronenbergs, encounter_system, universe, rng=None):
        cat_id = getattr(cat, 'name', None)
        route = self.find_cat_route(cat_id)
        if route is None:
            return {'result': 'no_active_route'}
        if not route.memory_started:
            self._remember_cat_route_event(cat=cat, route=route, universe=universe, event_type='route_started', details={'route_steps': [dict(step) for step in route.route_steps]})
            route.memory_started = True
        next_position = route.next_position
        if next_position is None:
            return {'result': 'already_arrived'}
        crossing_cronenbergs = [cronenberg for cronenberg in cronenbergs if getattr(cronenberg, 'is_alive', False) and route.position_matches(getattr(cronenberg, 'position', {}))]
        if crossing_cronenbergs:
            cronenberg = min(crossing_cronenbergs, key=lambda item: item.size)
            cronenberg_position = getattr(cronenberg, 'position', None)
            previous_detour_count = route.detour_count_for(cronenberg_position)
            if previous_detour_count > 0:

                def repeated_cat_route_paradox():
                    raise RuntimeError('Cat route paradox: repeated obstacle on shortest path.')
                quantum_error = universe.quantum_error_boundary.execute(operation=repeated_cat_route_paradox, source_component='quantum_cat_route', source_operation='repeated_detour_paradox')
                manifested_cronenberg = quantum_error.get('cronenberg')
                if manifested_cronenberg is not None:
                    link_metadata = {'cat': cat_id, 'position': dict(cronenberg_position), 'source_operation': 'repeated_detour_paradox'}
                    cronenberg.quantum_link_system.add_link(target_id=manifested_cronenberg.id, link_type='manifested_consequence', strength=1.0, created_tick=getattr(universe, 'universe_tick', None), metadata=link_metadata)
                    manifested_cronenberg.quantum_link_system.add_link(target_id=cronenberg.id, link_type='causal_paradox', strength=1.0, created_tick=getattr(universe, 'universe_tick', None), metadata=link_metadata)
                route.record_encounter({'result': 'cat_route_paradox', 'cat': cat_id, 'blocked_by': cronenberg.name, 'position': dict(cronenberg_position)})
                return {'result': 'cat_route_paradox_created_cronenberg', 'cat': cat_id, 'blocked_by': cronenberg.name, 'quantum_error': quantum_error}
            encounter = encounter_system.resolve(cat=cat, cronenberg=cronenberg, route=route, universe=universe, rng=rng)
            if encounter.get('result') == 'cat_avoids_cronenberg':
                self._remember_cat_route_event(cat=cat, route=route, universe=universe, event_type='route_detour', details={'blocked_by': cronenberg.name, 'blocked_position': dict(cronenberg_position), 'detour_position': dict(encounter['detour']), 'returns_to_original_route': True})
                return encounter
        previous_position = dict(route.current_position)
        position = route.advance()
        self._remember_cat_route_event(cat=cat, route=route, universe=universe, event_type='route_step', details={'previous_position': previous_position, 'position': dict(position) if position is not None else None})
        if route.has_arrived:
            self._remember_cat_route_event(cat=cat, route=route, universe=universe, event_type='route_arrived', details={'arrival_position': dict(route.current_position)})
        return {'result': 'route_advanced', 'position': position, 'destination': route.destination, 'arrived': route.has_arrived}

    @property
    def public_state(self):
        return {'name': self.name, 'type': self.type, 'configuration_id': self.configuration_id, 'configuration_seed': self.configuration_seed, 'reconfiguration_count': self.reconfiguration_count, 'staircase_count': len(self.staircases), 'active_cat_route_count': len(self.get_active_cat_routes()), 'active_cat_routes': [route.public_state for route in self.get_active_cat_routes()], 'quantum_die_box': self.quantum_die_box.public_state, 'bar_front_door': dict(self.bar_front_door), 'geometry_engine': self.geometry_engine.public_state}
