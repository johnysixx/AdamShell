from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class GarfieldTrainingAssignedEvent:
    cat: str
    instructor: str = field(default="Garfield", init=False)
    name: str = field(default="garfield_training_assigned", init=False)
    required: bool = field(default=True, init=False)


@dataclass(slots=True, frozen=True)
class GarfieldTrainingNotRequiredResult:
    cat: str
    name: str = field(default="garfield_training_not_required", init=False)
    completed: bool = field(default=False, init=False)


@dataclass(slots=True, frozen=True)
class GarfieldTrainingCompletedEvent:
    cat: str
    instructor: str = field(default="Garfield", init=False)
    name: str = field(default="garfield_training_completed", init=False)
    completed: bool = field(default=True, init=False)
