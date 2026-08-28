from copy import deepcopy
import math
from universe.aroma_profile import AromaProfile
from cats.cat_knowledge import CatKnowledge

class CatOlfaction:
    DEFAULT_RADIUS = 14.0

    @classmethod
    def sniff(cls, cat, universe, radius=None):
        radius = float(radius if radius is not None else cls.DEFAULT_RADIUS)
        cat_position = cls._position(getattr(cat, 'position', None))
        detected = []
        seen_ids = set()
        for entity in getattr(universe, 'entities', []):
            if entity is cat:
                continue
            observation = cls._sniff_entity(cat=cat, entity=entity, cat_position=cat_position, radius=radius)
            if observation is None:
                continue
            entity_id = observation['entity_id']
            if entity_id in seen_ids:
                continue
            seen_ids.add(entity_id)
            detected.append(observation)
        for entity in getattr(universe, 'cronenbergs', []):
            observation = cls._sniff_entity(cat=cat, entity=entity, cat_position=cat_position, radius=radius)
            if observation is None:
                continue
            entity_id = observation['entity_id']
            if entity_id in seen_ids:
                continue
            seen_ids.add(entity_id)
            detected.append(observation)
        cat_layer = getattr(cat, 'current_layer', None)
        for quantum_box in getattr(universe, 'quantum_boxes', []):
            box_layer = getattr(quantum_box, 'current_layer', None)
            if cat_layer is not None and box_layer is not None and (box_layer != cat_layer):
                continue
            observation = cls._sniff_entity(cat=cat, entity=quantum_box, cat_position=cat_position, radius=radius)
            if observation is None:
                continue
            entity_id = observation['entity_id']
            if entity_id in seen_ids:
                continue
            seen_ids.add(entity_id)
            detected.append(observation)
        ambient = cls._sniff_ambient(cat=cat, universe=universe)
        detected.sort(key=lambda item: item['perceived_intensity'], reverse=True)
        ozone_detected = any((float(item['components'].get('ozone', 0.0)) > 0.15 for item in detected))
        return {'cat': cat.name, 'radius': radius, 'detected_aromas': detected, 'ambient_aroma': ambient, 'ozone_detected': ozone_detected, 'detected_count': len(detected), 'sniffed': True}

    @classmethod
    def _sniff_entity(cls, cat, entity, cat_position, radius):
        profile = cls._get(entity, 'aroma')
        if not isinstance(profile, dict):
            return None
        position = cls._position(cls._get(entity, 'position'))
        distance = cls._distance(cat_position, position)
        if distance > radius:
            return None
        components = AromaProfile.current(profile)
        if not components:
            return None
        distance_factor = 1.0 / (1.0 + distance)
        perceived = {name: float(value) * distance_factor for name, value in components.items()}
        recognition = CatKnowledge.recognize_aroma(cat, components)
        identity = profile.get('identity')
        return {'entity_id': cls._entity_id(entity), 'actual_identity': identity, 'position': deepcopy(position), 'distance': distance, 'components': perceived, 'raw_components': components, 'perceived_intensity': sum(perceived.values()), 'recognition': recognition}

    @classmethod
    def _sniff_ambient(cls, cat, universe):
        if getattr(cat, 'current_layer', None) != 'meeting_place':
            return None
        meeting_place = getattr(universe, 'meeting_place', None)
        if meeting_place is None:
            return None
        ambient = getattr(meeting_place, 'ambient_aroma', None)
        if not isinstance(ambient, dict):
            return None
        profile = dict(ambient.get('profile', {}))
        recognition = CatKnowledge.recognize_aroma(cat, profile)
        return {'source': ambient.get('dominant_source'), 'components': profile, 'recognition': recognition}

    @staticmethod
    def _get(entity, key):
        return getattr(entity, key, None)

    @classmethod
    def _entity_id(cls, entity):
        return cls._get(entity, 'name') or cls._get(entity, 'id') or f'entity_{id(entity)}'

    @staticmethod
    def _position(position):
        if not isinstance(position, dict):
            return {'x': 0.0, 'y': 0.0, 'z': 0.0}
        return {'x': float(position.get('x', 0.0)), 'y': float(position.get('y', 0.0)), 'z': float(position.get('z', 0.0))}

    @staticmethod
    def _distance(first, second):
        return math.sqrt((first['x'] - second['x']) ** 2 + (first['y'] - second['y']) ** 2 + (first['z'] - second['z']) ** 2)
