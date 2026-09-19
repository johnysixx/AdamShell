from dataclasses import dataclass, field


@dataclass(slots=True)
class KittenCareState:
    fed_today: bool = False
    cleaned_today: bool = False
    warmed_today: bool = False
    protected_today: bool = False
    mother_present: bool = False
    left_alone_briefly: bool = False


@dataclass(slots=True)
class KittenCronenbergExperienceState:
    dead_deliveries: int = 0
    father_food_deliveries: int = 0
    live_deliveries: int = 0
    successful_kills: int = 0
    family_hunts: int = 0


@dataclass(slots=True)
class KittenUpbringingState:
    phase: str = 'complete_maternal_care'
    days_processed: int = 0
    last_processed_age: int | None = None
    last_processed_day: int | None = None
    care: KittenCareState = field(
        default_factory=KittenCareState
    )
    cronenberg_experience: KittenCronenbergExperienceState = field(
        default_factory=KittenCronenbergExperienceState
    )
    history: list = field(
        default_factory=list
    )
