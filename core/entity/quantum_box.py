import random
import uuid
from dataclasses import dataclass, field

from core.actualization.possibility import Possibility
from core.actualization.potential import Potential


@dataclass(slots=True)
class QuantumBoxCounterpartState:
    box_id: str | None = None
    layer: str | None = None
    paired: bool = False

    def pair(
        self,
        box_id,
        layer
    ):
        self.box_id = box_id
        self.layer = layer
        self.paired = True
        return self

    def clear(self):
        previous = self.to_dict()
        self.box_id = None
        self.layer = None
        self.paired = False
        return previous

    def to_dict(self):
        return {
            'box_id': self.box_id,
            'layer': self.layer,
            'paired': self.paired,
        }


@dataclass(slots=True)
class QuantumBoxCatTransferState:
    active: bool = False
    state: str = 'inactive'
    cat_name: str | None = None
    source_box_id: str | None = None
    target_box_id: str | None = None
    source_layer: str | None = None
    target_layer: str | None = None
    started_tick: int | None = None

    def begin(
        self,
        cat_name,
        source_box_id,
        target_box_id,
        source_layer,
        target_layer,
        started_tick=None
    ):
        self.active = True
        self.state = (
            'cat_transfer_superposition'
        )
        self.cat_name = cat_name
        self.source_box_id = source_box_id
        self.target_box_id = target_box_id
        self.source_layer = source_layer
        self.target_layer = target_layer
        self.started_tick = started_tick
        return self

    def complete(
        self,
        clear_source=True
    ):
        self.active = False
        self.state = 'completed'
        self.cat_name = None
        self.target_box_id = None
        self.target_layer = None

        if clear_source:
            self.source_box_id = None
            self.source_layer = None
            self.started_tick = None

        return self

    def to_dict(self):
        return {
            'active': self.active,
            'state': self.state,
            'cat_name': self.cat_name,
            'source_box_id':
                self.source_box_id,
            'target_box_id':
                self.target_box_id,
            'source_layer': self.source_layer,
            'target_layer': self.target_layer,
            'started_tick': self.started_tick,
        }


@dataclass(slots=True)
class QuantumBoxEnergyState:
    available: bool = True
    consumed: bool = False
    purpose: str | None = None

    def consume_for_cat_transfer(self):
        self.available = False
        self.consumed = True
        self.purpose = 'cat_layer_transfer'
        return self

    def to_dict(self):
        return {
            'available': self.available,
            'consumed': self.consumed,
            'purpose': self.purpose,
        }


@dataclass(slots=True)
class QuantumBoxContentState:
    possibilities: list[str] = field(
        default_factory=lambda: [
            'empty',
            'cat',
        ]
    )
    resolved: str | None = None

    def resolve(self, result):
        self.resolved = result
        return result

    def to_dict(self):
        return {
            'possibilities': list(
                self.possibilities
            ),
            'resolved': self.resolved,
        }


@dataclass(slots=True)
class QuantumBoxCollapseState:
    collapsed: bool = False
    cause: str | None = None
    observer: str | None = None
    tick: int | None = None

    def resolve(
        self,
        cause,
        observer=None,
        tick=None
    ):
        self.collapsed = True
        self.cause = cause
        self.observer = observer
        self.tick = tick
        return self

    def to_dict(self):
        return {
            'collapsed': self.collapsed,
            'cause': self.cause,
            'observer': self.observer,
            'tick': self.tick,
        }


class QuantumBox:

    def __init__(self, rng=None):
        rng = rng or random
        self.id = f'quantum_box_{uuid.uuid4().hex[:8]}'
        self.position = {'x': rng.uniform(-1.0, 1.0), 'y': rng.uniform(-1.0, 1.0), 'z': rng.uniform(-1.0, 1.0)}
        self.state = 'superposition'
        self.age_ticks = 0
        self.box_class = '1x'
        self.current_layer = 'quantum_layer'
        self.quantum_counterpart = (
            QuantumBoxCounterpartState()
        )
        self.cat_transfer = (
            QuantumBoxCatTransferState()
        )
        self.energy = QuantumBoxEnergyState()
        self.content = QuantumBoxContentState()
        self.collapse = (
            QuantumBoxCollapseState()
        )

    def pair_with(self, counterpart):
        if counterpart is self:
            raise ValueError('Quantum box cannot pair with itself.')
        if self.box_class != '1x':
            raise ValueError('Only 1x boxes are supported.')
        if counterpart.box_class != '1x':
            raise ValueError('Only 1x boxes are supported.')
        self.quantum_counterpart.pair(
            box_id=counterpart.id,
            layer=counterpart.current_layer,
        )
        counterpart.quantum_counterpart.pair(
            box_id=self.id,
            layer=self.current_layer,
        )
        return {'name': 'quantum_boxes_paired', 'box_a': self.id, 'box_b': counterpart.id, 'layer_a': self.current_layer, 'layer_b': counterpart.current_layer, 'paired': True}

    def clear_counterpart(self):
        return self.quantum_counterpart.clear()

    def begin_cat_transfer(self, cat, target_box, tick=None):
        if not self.quantum_counterpart.paired:
            raise RuntimeError('Source quantum box has no counterpart.')
        if self.quantum_counterpart.box_id != target_box.id:
            raise RuntimeError('Target box is not the paired counterpart.')
        if not target_box.energy.available:
            raise RuntimeError('Target box has no available energy.')
        transfer_values = {
            'cat_name': getattr(cat, 'name', None),
            'source_box_id': self.id,
            'target_box_id': target_box.id,
            'source_layer': self.current_layer,
            'target_layer': target_box.current_layer,
            'started_tick': tick,
        }
        self.cat_transfer.begin(
            **transfer_values
        )
        target_box.cat_transfer.begin(
            **transfer_values
        )
        self.state = 'cat_transfer_superposition'
        target_box.state = 'cat_transfer_superposition'
        return self.cat_transfer.to_dict()

    def is_in_cat_transfer_superposition(self):
        return bool(
            self.cat_transfer.active
            and self.cat_transfer.state
            == 'cat_transfer_superposition'
        )

    def is_visible_to(self, observer):
        if not self.is_in_cat_transfer_superposition():
            return True
        return getattr(observer, 'type', None) == 'cat'

    def cat_observation_state(self, observer):
        if not self.is_visible_to(observer):
            return {'visible': False, 'recognized_as_quantum_box': False, 'occupied': None}
        occupied = self.is_in_cat_transfer_superposition()
        return {'visible': True, 'recognized_as_quantum_box': True, 'occupied': occupied, 'occupancy_state': 'cat_transfer_occupied' if occupied else 'unoccupied', 'occupant_identity_visible': False}

    def consume_for_cat_transfer(self):
        self.energy.consume_for_cat_transfer()
        self.state = 'consumed'
        return self.energy.to_dict()

    @property
    def possibilities(self):
        return tuple(
            self.content.possibilities
        )

    def generate_potentials(self, cycle_id):
        if self.collapse.collapsed:
            return []
        probability = 1.0 / len(self.possibilities)
        return [Potential(possibility=Possibility(name=possibility_name, probability=probability, action=lambda result=possibility_name: self.resolve_state(result=result, cause='actualization', observer='reality', tick=cycle_id)), cycle_id=cycle_id, source=self.id, context={'type': 'quantum_box_collapse', 'quantum_box_id': self.id, 'result': possibility_name, 'exclusive_group': self.id}) for possibility_name in self.possibilities]

    def resolve_state(self, result, cause, observer=None, tick=None):
        if self.collapse.collapsed:
            return self.content.resolved
        if result not in self.possibilities:
            raise ValueError(f'Unknown quantum box result: {result}')
        self.content.resolve(result)
        self.state = 'collapsed'
        self.collapse.resolve(
            cause=cause,
            observer=observer,
            tick=tick,
        )
        print(f'QUANTUM BOX COLLAPSED: {self.id} CAUSE={cause} RESULT={result}')
        return {'type': 'quantum_box_collapsed', 'quantum_box_id': self.id, 'result': result, 'cause': cause, 'observer': observer, 'tick': tick}

    def collapse_state(self, cause, observer=None, tick=None, rng=None):
        if self.collapse.collapsed:
            return self.content.resolved
        rng = rng or random
        result = rng.choice(self.possibilities)
        event = self.resolve_state(result=result, cause=cause, observer=observer, tick=tick)
        return event['result']

    @property
    def public_state(self):
        return {
            'id': self.id,
            'type': 'quantum_box',
            'position': self.position.copy(),
            'state': self.state,
            'content_state': (
                'unresolved'
                if not self.collapse.collapsed
                else self.content.resolved
            ),
            'collapsed': self.collapse.collapsed,
            'box_class': self.box_class,
            'current_layer': self.current_layer,
            'quantum_counterpart': (
                self.quantum_counterpart
                .to_dict()
            ),
            'cat_transfer': (
                self.cat_transfer.to_dict()
            ),
            'energy': self.energy.to_dict(),
        }
