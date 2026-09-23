from dataclasses import dataclass, field

@dataclass(slots=True, frozen=True)
class CatOvulationStimulationRecordedEvent:
    female: str
    male: str | None
    day: int | None
    amount: int
    stimulation: int
    threshold: int
    threshold_reached: bool
    name: str = field(
        default="cat_ovulation_stimulation_recorded",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "female",
            str(self.female),
        )

        if self.male is not None:
            object.__setattr__(
                self,
                "male",
                str(self.male),
            )

        if self.day is not None:
            object.__setattr__(
                self,
                "day",
                int(self.day),
            )

        object.__setattr__(
            self,
            "amount",
            int(self.amount),
        )
        object.__setattr__(
            self,
            "stimulation",
            int(self.stimulation),
        )
        object.__setattr__(
            self,
            "threshold",
            int(self.threshold),
        )
        object.__setattr__(
            self,
            "threshold_reached",
            bool(self.threshold_reached),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "female": self.female,
            "male": self.male,
            "day": self.day,
            "amount": self.amount,
            "stimulation": self.stimulation,
            "threshold": self.threshold,
            "threshold_reached": (
                self.threshold_reached
            ),
        }


@dataclass(slots=True, frozen=True)
class CatInducedOvulationResolvedEvent:
    female: str
    day: int | None
    stimulation: int
    threshold: int
    ovulation_induced: bool
    reason: str | None
    name: str = field(
        default="cat_induced_ovulation_resolved",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "female",
            str(self.female),
        )

        if self.day is not None:
            object.__setattr__(
                self,
                "day",
                int(self.day),
            )

        object.__setattr__(
            self,
            "stimulation",
            int(self.stimulation),
        )
        object.__setattr__(
            self,
            "threshold",
            int(self.threshold),
        )
        object.__setattr__(
            self,
            "ovulation_induced",
            bool(self.ovulation_induced),
        )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(self.reason),
            )

    def to_dict(self):
        return {
            "name": self.name,
            "female": self.female,
            "day": self.day,
            "stimulation": self.stimulation,
            "threshold": self.threshold,
            "ovulation_induced": (
                self.ovulation_induced
            ),
            "reason": self.reason,
        }


class CatOvulationResolver:
    DEFAULT_THRESHOLD = 4

    def __init__(self, universe):
        self.universe = universe
        self.history = []

    def record_stimulation(self, female, male=None, amount=1, day=None):
        reproduction = female.reproduction
        amount = int(amount)
        if amount < 1:
            raise ValueError('Ovulation stimulation must increase by at least one.')
        current = int(reproduction.ovulation_stimulation)
        threshold = int(reproduction.ovulation_threshold)
        new_value = current + amount
        reproduction.ovulation_stimulation = new_value
        event = (
            CatOvulationStimulationRecordedEvent(
                female=female.name,
                male=(
                    getattr(
                        male,
                        'name',
                        None,
                    )
                    if isinstance(
                        male,
                        dict,
                    )
                    else None
                ),
                day=day,
                amount=amount,
                stimulation=new_value,
                threshold=threshold,
                threshold_reached=(
                    new_value >= threshold
                ),
            )
        )

        self.record_event(
            event
        )

        return event.to_dict()

    def resolve(self, female, day=None):
        reproduction = female.reproduction
        stimulation = int(reproduction.ovulation_stimulation)
        threshold = int(reproduction.ovulation_threshold)
        induced = stimulation >= threshold
        reproduction.ovulation_induced = induced
        if induced:
            reproduction.last_ovulation_day = day
        event = (
            CatInducedOvulationResolvedEvent(
                female=female.name,
                day=day,
                stimulation=stimulation,
                threshold=threshold,
                ovulation_induced=induced,
                reason=(
                    None
                    if induced
                    else 'insufficient_stimulation'
                ),
            )
        )

        self.record_event(
            event
        )

        return event.to_dict()

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            (
                CatOvulationStimulationRecordedEvent,
                CatInducedOvulationResolvedEvent,
            ),
        ):
            raise TypeError(
                'Ovulation history requires a '
                'cat ovulation event object.'
            )

        self.history.append(
            event
        )

        return event

    def reset(self, female):
        reproduction = female.reproduction
        reproduction.ovulation_stimulation = 0
        reproduction.ovulation_induced = False
