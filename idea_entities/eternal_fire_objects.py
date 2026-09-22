from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EternalFireFuelConsumption:
    dry_grass: float = 0.0
    wood_sticks: float = 0.0

    def __post_init__(self):
        if self.dry_grass < 0.0:
            raise ValueError("Consumed dry grass must not be negative")
        if self.wood_sticks < 0.0:
            raise ValueError("Consumed wood sticks must not be negative")

    def to_dict(self):
        return {
            "dry_grass": self.dry_grass,
            "wood_sticks": self.wood_sticks,
        }


@dataclass(slots=True)
class EternalFireFuel:
    dry_grass: float = 0.0
    wood_sticks: float = 0.0
    wood_added_by: str | None = None

    def __post_init__(self):
        self.dry_grass = float(self.dry_grass)
        self.wood_sticks = float(self.wood_sticks)
        self._validate_nonnegative()

    def _validate_nonnegative(self):
        if self.dry_grass < 0.0:
            raise ValueError("Dry grass fuel must not be negative")
        if self.wood_sticks < 0.0:
            raise ValueError("Wood fuel must not be negative")

    @property
    def total(self):
        return self.dry_grass + self.wood_sticks

    def consume_next(self, *, wood_step):
        if wood_step <= 0.0:
            raise ValueError("Wood consumption step must be positive")

        dry_grass_consumed = 0.0
        wood_sticks_consumed = 0.0

        if self.dry_grass > 0.0:
            dry_grass_consumed = min(1.0, self.dry_grass)
            self.dry_grass -= dry_grass_consumed
        elif self.wood_sticks > 0.0:
            wood_sticks_consumed = min(
                float(wood_step),
                self.wood_sticks,
            )
            self.wood_sticks -= wood_sticks_consumed

        self._validate_nonnegative()

        return EternalFireFuelConsumption(
            dry_grass=dry_grass_consumed,
            wood_sticks=wood_sticks_consumed,
        )

    def to_dict(self):
        snapshot = {
            "dry_grass": self.dry_grass,
            "wood_sticks": self.wood_sticks,
        }

        if self.wood_added_by is not None:
            snapshot["wood_added_by"] = self.wood_added_by

        return snapshot


@dataclass(frozen=True, slots=True)
class EternalFireMeaning:
    warmth: bool = True
    must_be_preserved: bool = True
    requires_fuel: bool = True
    understood_by: tuple[str, ...] = (
        "pazuzu_masculine_principle",
        "lilith",
        "serpent",
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "understood_by",
            tuple(self.understood_by),
        )

    def to_dict(self):
        return {
            "warmth": self.warmth,
            "must_be_preserved": self.must_be_preserved,
            "requires_fuel": self.requires_fuel,
            "understood_by": list(self.understood_by),
        }
