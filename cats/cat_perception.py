from cats.cat import Cat
import math
from copy import deepcopy

from cats.cat_quantum_observation_state import (
    CatQuantumCounterpartObservation,
)
from universe.dark_sector import QUANTUM_BOX_ENERGY_COST_J
from .cat_exploration_planner import CatExplorationPlanner
from .cat_olfaction import CatOlfaction
from .cat_knowledge import CatKnowledge
from .cat_perception_state import (
    CatBarObservation,
    CatCronenbergObservation,
    CatNearbyCatObservation,
    CatPerceptionFailure,
    CatPerceptionState,
    CatVisibleBoxObservation,
)

from cats.cat_perception_state import CatScentTransferCandidate

class CatPerception:
    DEFAULT_VISION_RADIUS = 8.0
    NEARBY_CAT_RADIUS = 4.0
    HUNTABLE_SIZE_RATIO = 1.2

    def __init__(self, cats_layer):
        self.cats_layer = cats_layer
        self.universe = cats_layer.universe
        self.history = []

    def observe(self, cat, vision_radius=None):
        if not isinstance(cat, Cat):
            return CatPerceptionFailure(
                reason='invalid_cat',
            )
        if cat.type != 'cat':
            return CatPerceptionFailure(
                cat=cat.name,
                reason='entity_is_not_cat',
            )
        position = getattr(cat, 'position', None)
        if position is None:
            return CatPerceptionFailure(
                cat=cat.name,
                reason='cat_has_no_position',
            )
        radius = float(vision_radius if vision_radius is not None else self.DEFAULT_VISION_RADIUS)
        nearby_cats = self._observe_nearby_cats(cat=cat, position=position, radius=min(radius, self.NEARBY_CAT_RADIUS))
        visible_cronenbergs = self._observe_cronenbergs(position=position, radius=radius)
        huntable_cronenbergs = self._huntable_cronenbergs(cat=cat, cronenbergs=visible_cronenbergs)
        visible_boxes = self._observe_quantum_boxes(cat=cat, position=position, radius=radius)
        unexplored_boxes = [
            item
            for item in visible_boxes
            if not item.occupied
            and not item.explored
        ]
        occupied_transfer_boxes = [
            item
            for item in visible_boxes
            if item.occupied
        ]
        bar_observation = self._observe_bar(cat=cat, position=position, radius=radius)
        danger = self._cronenberg_danger(cat=cat, cronenbergs=visible_cronenbergs)
        current_layer = cat.current_layer or 'quantum_layer'
        exploration_plan = CatExplorationPlanner.choose_destination(cat=cat, universe=self.universe)
        exploration_destination_layer = exploration_plan.layer
        exploration_destination_position = exploration_plan.position
        exploration_pair_energy_cost = QUANTUM_BOX_ENERGY_COST_J * 2.0
        available_cat_energy = float(cat.idea_energy)
        can_create_exploration_pair = bool(not unexplored_boxes and available_cat_energy >= exploration_pair_energy_cost and exploration_plan.selected and (exploration_destination_layer != current_layer))
        active_cat_legends = [legend for legend in getattr(self.universe, 'cat_legends', []) if getattr(legend, 'active', True)]
        shareable_legend_count = len(active_cat_legends)
        olfaction = CatOlfaction.sniff(cat=cat, universe=self.universe)
        scent_memories = CatKnowledge.remember_olfaction(cat=cat, olfaction=olfaction, current_layer=cat.current_layer or 'unknown', universe_tick=getattr(self.universe, 'universe_tick', None))
        smelled_cronenbergs = [
            item
            for item in olfaction.detected_aromas
            if item.recognition.recognized
            and item.recognition.identity == 'cronenberg'
        ]
        cronenberg_scent_recognized = bool(smelled_cronenbergs)
        scent_transfer_candidates = []
        smelled_by_id = {item.entity_id: item for item in olfaction.detected_aromas}
        boxes_by_id = {getattr(box, 'id', None): box for box in getattr(self.universe, 'quantum_boxes', [])}
        for visible_box in visible_boxes:
            box_id = visible_box.id
            if box_id is None:
                continue
            box = boxes_by_id.get(box_id)
            smelled = smelled_by_id.get(box_id)
            if box is None or smelled is None:
                continue
            recognition = smelled.recognition
            if not recognition.recognized:
                continue
            counterpart = getattr(box, 'quantum_counterpart', None)
            if counterpart is None:
                continue
            if not counterpart.paired:
                continue
            counterpart_id = counterpart.box_id
            counterpart_box = boxes_by_id.get(counterpart_id)
            if counterpart_box is None:
                continue
            scent_transfer_candidates.append(
                CatScentTransferCandidate(
                    box_id=box_id,
                    counterpart_box_id=(
                        counterpart_id
                    ),
                    identity=(
                        recognition.identity
                    ),
                    similarity=float(
                        recognition.similarity
                    ),
                    source_layer=getattr(
                        box,
                        'current_layer',
                        cat.current_layer,
                    ),
                    target_layer=getattr(
                        counterpart_box,
                        'current_layer',
                        None,
                    ),
                    box_position=deepcopy(
                        getattr(
                            box,
                            'position',
                            {},
                        )
                    ),
                    counterpart_position=deepcopy(
                        getattr(
                            counterpart_box,
                            'position',
                            {},
                        )
                    ),
                )
            )
        counterpart_observation = deepcopy(
            cat.current_quantum_counterpart_observation
        )

        if (
            counterpart_observation is not None
            and not isinstance(
                counterpart_observation,
                CatQuantumCounterpartObservation,
            )
        ):
            raise TypeError(
                'Quantum counterpart observation '
                'must be '
                'CatQuantumCounterpartObservation.'
            )

        if isinstance(
            counterpart_observation,
            CatQuantumCounterpartObservation,
        ):
            source_id = (
                counterpart_observation
                .source_box_id
            )
            counterpart_id = (
                counterpart_observation
                .counterpart_box_id
            )
            source_box = next((box for box in getattr(self.universe, 'quantum_boxes', []) if getattr(box, 'id', None) == source_id), None)
            counterpart_box = next((box for box in getattr(self.universe, 'quantum_boxes', []) if getattr(box, 'id', None) == counterpart_id), None)
            valid = source_box is not None and counterpart_box is not None and source_box.quantum_counterpart.paired and (source_box.quantum_counterpart.box_id == counterpart_id) and counterpart_box.quantum_counterpart.paired and (counterpart_box.quantum_counterpart.box_id == source_id)
            if not valid:
                cat.current_quantum_counterpart_observation = (
                    None
                )
                counterpart_observation = None
        observations = CatPerceptionState(
            cat=cat.name,
            position=deepcopy(position),
            vision_radius=radius,
            bar_known=bar_observation.known,
            bar_visible=bar_observation.visible,
            bar_distance=bar_observation.distance,
            nearby_cats=[
                item.name
                for item in nearby_cats
            ],
            nearby_cat_details=nearby_cats,
            visible_cronenbergs=[
                item.id
                for item in visible_cronenbergs
            ],
            visible_cronenberg_details=visible_cronenbergs,
            huntable_cronenbergs=[
                item.id
                for item in huntable_cronenbergs
            ],
            huntable_cronenberg_details=huntable_cronenbergs,
            cronenberg_danger=danger,
            visible_boxes=[
                item.id
                for item in visible_boxes
            ],
            visible_box_details=visible_boxes,
            unexplored_boxes=[
                item.id
                for item in unexplored_boxes
            ],
            occupied_transfer_boxes=[
                item.id
                for item in occupied_transfer_boxes
            ],
            occupied_transfer_box_details=occupied_transfer_boxes,
            interesting_unknown=bool(
                unexplored_boxes
            ),
            quantum_counterpart_observation=deepcopy(
                counterpart_observation
            ),
            current_layer=current_layer,
            available_cat_energy=available_cat_energy,
            can_create_exploration_pair=(
                can_create_exploration_pair
            ),
            exploration_pair_energy_cost=(
                exploration_pair_energy_cost
            ),
            exploration_destination_layer=(
                exploration_destination_layer
            ),
            exploration_destination_position=(
                exploration_destination_position
            ),
            exploration_plan=deepcopy(
                exploration_plan
            ),
            shareable_legend_count=(
                shareable_legend_count
            ),
            olfaction=deepcopy(
                olfaction
            ),
            scent_memories=deepcopy(
                scent_memories
            ),
            scent_transfer_candidates=deepcopy(
                scent_transfer_candidates
            ),
            smelled_entities=[
                item.entity_id
                for item
                in olfaction.detected_aromas
            ],
            ozone_detected=(
                olfaction.ozone_detected
            ),
            cronenberg_scent_recognized=(
                cronenberg_scent_recognized
            ),
            smelled_cronenbergs=deepcopy(
                smelled_cronenbergs
            ),
        )
        event = {'name': 'cat_environment_observed', 'cat': cat.name, 'observations': deepcopy(observations), 'observed': True}
        mind = cat.mind
        mind.last_observations = deepcopy(observations)
        getattr(mind, 'observation_history', []).append(deepcopy(event))
        self._record(event)
        return observations

    def _observe_nearby_cats(self, cat, position, radius):
        observed = []
        for candidate in self.cats_layer.cats:
            if candidate is cat:
                continue
            candidate_position = candidate.position
            if candidate_position is None:
                continue
            distance = self._distance(position, candidate_position)
            if distance > radius:
                continue
            observed.append(
                CatNearbyCatObservation(
                    name=candidate.name,
                    distance=distance,
                    position=deepcopy(
                        candidate_position
                    ),
                )
            )

        observed.sort(
            key=lambda item: item.distance
        )
        return observed

    def _observe_cronenbergs(self, position, radius):
        observed = []
        for cronenberg in getattr(self.universe, 'cronenbergs', []):
            if not getattr(cronenberg, 'is_alive', False):
                continue
            cronenberg_position = getattr(cronenberg, 'position', None)
            if cronenberg_position is None:
                continue
            distance = self._distance(position, cronenberg_position)
            if distance > radius:
                continue
            observed.append(
                CatCronenbergObservation(
                    id=cronenberg.id,
                    name=getattr(
                        cronenberg,
                        'name',
                        cronenberg.id,
                    ),
                    size=float(
                        getattr(
                            cronenberg,
                            'size',
                            1.0,
                        )
                    ),
                    distance=distance,
                    position=deepcopy(
                        cronenberg_position
                    ),
                )
            )

        observed.sort(
            key=lambda item: item.distance
        )
        return observed

    def _huntable_cronenbergs(self, cat, cronenbergs):
        cat_size = max(
            1e-06,
            float(cat.size),
        )

        huntable = []

        for item in cronenbergs:
            size_ratio = (
                item.size
                / cat_size
            )

            if (
                size_ratio
                > self.HUNTABLE_SIZE_RATIO
            ):
                continue

            huntable.append(
                CatCronenbergObservation(
                    id=item.id,
                    name=item.name,
                    size=item.size,
                    distance=item.distance,
                    position=deepcopy(
                        item.position
                    ),
                    size_ratio=size_ratio,
                )
            )

        return huntable

    def _observe_quantum_boxes(self, cat, position, radius):
        observed = []
        cat_layer = cat.current_layer
        for box in getattr(self.universe, 'quantum_boxes', []):
            box_layer = getattr(box, 'current_layer', None)
            transfer_superposition = getattr(box, 'is_in_cat_transfer_superposition', None)
            cross_layer_cat_transfer = bool(callable(transfer_superposition) and transfer_superposition())
            if cat_layer is not None and box_layer is not None and (box_layer != cat_layer) and (not cross_layer_cat_transfer):
                continue
            visible_to = getattr(box, 'is_visible_to', None)
            if callable(visible_to) and (not visible_to(cat)):
                continue
            box_position = getattr(box, 'position', None)
            if box_position is None:
                continue
            distance = self._distance(position, box_position)
            if distance > radius:
                continue
            cat_observation = getattr(box, 'cat_observation_state', None)
            occupancy = cat_observation(cat) if callable(cat_observation) else {'visible': True, 'occupied': False, 'occupancy_state': 'unknown', 'occupant_identity_visible': False}
            explored = self._box_was_explored(cat=cat, box_id=box.id)
            detail = CatVisibleBoxObservation(
                id=box.id,
                explored=explored,
                occupied=bool(
                    occupancy.get(
                        'occupied',
                        False,
                    )
                ),
                occupancy_state=occupancy.get(
                    'occupancy_state',
                    'unknown',
                ),
                occupant_identity_visible=bool(
                    occupancy.get(
                        'occupant_identity_visible',
                        False,
                    )
                ),
                distance=distance,
                position=deepcopy(
                    box_position
                ),
            )

            if explored:
                knowledge = (
                    CatKnowledge
                    .ensure_cat_knowledge(cat)
                )

                pairing_principle_known = bool(
                    knowledge
                    .known_principles
                    .quantum_boxes_are_paired
                )

                recognized_as_quantum_box = bool(
                    occupancy.get(
                        'recognized_as_quantum_box',
                        True,
                    )
                )

                detail.state = getattr(
                    box,
                    'state',
                    None,
                )

                detail.collapsed = bool(
                    box.collapse.collapsed
                )

                detail.recognized_as_quantum_box = (
                    recognized_as_quantum_box
                )

                detail.paired = bool(
                    recognized_as_quantum_box
                    and pairing_principle_known
                )

                detail.counterpart_known = False

            observed.append(detail)

        observed.sort(
            key=lambda item: item.distance
        )
        return observed

    def _observe_bar(
        self,
        cat,
        position,
        radius,
    ):
        quantum_space = getattr(
            self.universe,
            'quantum_space',
            None,
        )

        if quantum_space is None:
            return CatBarObservation(
                known=self._cat_knows_bar(
                    cat
                ),
                visible=False,
                distance=None,
            )

        door = getattr(
            quantum_space,
            'bar_front_door',
            None,
        )

        if not door:
            return CatBarObservation(
                known=self._cat_knows_bar(
                    cat
                ),
                visible=False,
                distance=None,
            )

        door_position = door.get(
            'position'
        )

        distance = (
            self._distance(
                position,
                door_position,
            )
            if door_position is not None
            else None
        )

        visible = bool(
            distance is not None
            and distance <= radius
        )

        return CatBarObservation(
            known=bool(
                visible
                or self._cat_knows_bar(
                    cat
                )
            ),
            visible=visible,
            distance=distance,
        )

    def _cat_knows_bar(self, cat):
        traits = cat.special_traits
        if 'sees_direct_path_to_bar' in traits:
            return True
        memory = cat.memory
        if memory is None:
            return False
        for event in getattr(memory, 'events', []):
            if event.get('location') in {'meeting_place', 'bar', 'bar_front_door'}:
                return True
            if event.get('event_type') in {'bar_entry', 'cat_drank_milk_at_bar', 'bouncer_petted_cat', 'safe_at_bar'}:
                return True
        return False

    def _box_was_explored(self, cat, box_id):
        memory = cat.memory
        if memory is None:
            return False
        for event in getattr(memory, 'events', []):
            if event.get('event_type') not in {'box_explored', 'box_entered', 'quantum_box_observed'}:
                continue
            if box_id in event.get('participants', []):
                return True
            details = event.get('details', {})
            if details.get('box_id') == box_id:
                return True
        return False

    def _cronenberg_danger(self, cat, cronenbergs):
        if not cronenbergs:
            return 0.0
        cat_size = max(1e-06, float(cat.size))
        highest_ratio = max(
            item.size / cat_size
            for item in cronenbergs
        )
        return min(1.0, highest_ratio / 2.0)

    def _distance(self, first, second):
        if first is None or second is None:
            return float('inf')
        return math.sqrt((float(first.get('x', 0.0)) - float(second.get('x', 0.0))) ** 2 + (float(first.get('y', 0.0)) - float(second.get('y', 0.0))) ** 2 + (float(first.get('z', 0.0)) - float(second.get('z', 0.0))) ** 2)

    def _record(self, event):
        self.history.append(deepcopy(event))
        quantum_events = getattr(self.universe, 'quantum_events', None)
        if quantum_events is not None:
            quantum_events.append(deepcopy(event))
        emit_event = getattr(self.cats_layer, 'emit_event', None)
        if emit_event is not None:
            emit_event(deepcopy(event))
