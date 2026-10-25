from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CronenbergQuantumPairConsumedEvent:
    pair_id: str
    participants: tuple[str, str]
    recombined_id: str
    combined_size: float
    recombined_size: float
    combined_energy: float
    retained_energy: float
    released_energy: float
    dark_energy_created: float
    tick: int
    name: str = field(
        default="cronenberg_quantum_pair_consumed",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "pair_id": self.pair_id,
            "participants": list(self.participants),
            "recombined_id": self.recombined_id,
            "combined_size": self.combined_size,
            "recombined_size": self.recombined_size,
            "combined_energy": self.combined_energy,
            "retained_energy": self.retained_energy,
            "released_energy": self.released_energy,
            "dark_energy_created": self.dark_energy_created,
            "tick": self.tick,
        }


@dataclass(slots=True, frozen=True)
class CronenbergQuantumPairConsumptionResult:
    first: object
    second: object
    recombined: object
    event: CronenbergQuantumPairConsumedEvent
    result: str = field(
        default="quantum_pair_consumption_recombined",
        init=False,
    )

    def to_dict(self):
        return {
            "result": self.result,
            "first": self.first.id,
            "second": self.second.id,
            "recombined": self.recombined.id,
            "event": self.event.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class CronenbergQuantumPairMergedEvent:
    pair_id: str
    parents: tuple[str, str]
    merged_id: str
    merged_size: float
    merged_energy: float
    merged_spin: float
    source: str
    tick: int
    name: str = field(
        default="cronenberg_quantum_pair_merged",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "pair_id": self.pair_id,
            "parents": list(self.parents),
            "merged_id": self.merged_id,
            "merged_size": self.merged_size,
            "merged_energy": self.merged_energy,
            "merged_spin": self.merged_spin,
            "source": self.source,
            "tick": self.tick,
        }


@dataclass(slots=True, frozen=True)
class CronenbergQuantumPairMergeResult:
    first: object
    second: object
    merged: object
    event: CronenbergQuantumPairMergedEvent
    result: str = field(
        default="quantum_pair_merged",
        init=False,
    )

    def to_dict(self):
        return {
            "result": self.result,
            "first": self.first.id,
            "second": self.second.id,
            "merged": self.merged.id,
            "event": self.event.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class CronenbergQuantumCounterpartCreatedEvent:
    original_id: str
    counterpart_id: str
    pair_id: str
    original_spin: float
    counterpart_spin: float
    source: str
    tick: int
    name: str = field(
        default="cronenberg_quantum_counterpart_created",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "original_id": self.original_id,
            "counterpart_id": self.counterpart_id,
            "pair_id": self.pair_id,
            "original_spin": self.original_spin,
            "counterpart_spin": self.counterpart_spin,
            "source": self.source,
            "tick": self.tick,
        }


@dataclass(slots=True, frozen=True)
class CronenbergQuantumCounterpartCreatedResult:
    original: object
    counterpart: object
    pair_id: str
    event: CronenbergQuantumCounterpartCreatedEvent
    result: str = field(
        default="counterpart_created",
        init=False,
    )

    def to_dict(self):
        return {
            "result": self.result,
            "original": self.original,
            "counterpart": self.counterpart,
            "pair_id": self.pair_id,
            "event": self.event.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class CronenbergQuantumCounterpartAlreadyExistsResult:
    original: object
    counterpart: object
    pair_id: str
    result: str = field(
        default="counterpart_already_exists",
        init=False,
    )

    def to_dict(self):
        return {
            "result": self.result,
            "original": self.original,
            "counterpart": self.counterpart,
            "pair_id": self.pair_id,
        }
