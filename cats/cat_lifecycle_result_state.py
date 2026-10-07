from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatLifeCycleDayCompletedEvent:
    day: int
    cats_processed: int
    age_advances: tuple[object, ...]
    estrous_cycle_results: tuple[object, ...]
    pregnancy_advances: tuple[object, ...]
    births: tuple[object, ...]
    upbringing_results: tuple[object, ...]

    name: str = field(
        default="cat_life_cycle_day_completed",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "day",
            int(self.day),
        )

        object.__setattr__(
            self,
            "cats_processed",
            int(self.cats_processed),
        )

        collection_names = (
            "age_advances",
            "estrous_cycle_results",
            "pregnancy_advances",
            "births",
            "upbringing_results",
        )

        for collection_name in collection_names:
            values = tuple(
                getattr(
                    self,
                    collection_name,
                )
            )

            if any(
                isinstance(
                    value,
                    dict,
                )
                for value
                in values
            ):
                raise TypeError(
                    "Cat lifecycle collections "
                    "must contain result objects, "
                    "not mappings."
                )

            object.__setattr__(
                self,
                collection_name,
                values,
            )
