from cats.estrous_cycle_resolver import (
    CatEstrousCycleResolver
)
from cats.development_resolver import (
    CatDevelopmentResolver
)
from cats.mating_resolver import (
    CatMatingResolver
)
from cats.kitten_birth_resolver import (
    KittenBirthResolver
)


class CatLifeCycleHandler:

    name = "cat_life_cycle"

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

        self.development_resolver = (
            CatDevelopmentResolver(
                universe
            )
        )

        self.estrous_cycle_resolver = (
            CatEstrousCycleResolver(
                universe
            )
        )

        self.mating_resolver = (
            CatMatingResolver(
                universe
            )
        )

        self.birth_resolver = (
            KittenBirthResolver(
                universe
            )
        )

    def tick_day(
        self,
        day
    ):
        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        if cats_layer is None:
            event = {
                "name": (
                    "cat_life_cycle_day_completed"
                ),
                "day": day,
                "cats_processed": 0,
                "age_advances": [],
                "pregnancy_advances": [],
                "births": []
            }

            self.history.append(
                event
            )

            return event

        age_advances = []
        estrous_cycle_results = []
        pregnancy_advances = []
        births = []

        # Kopie seznamu je důležitá:
        # porod může během iterace přidat nová koťata.
        cats = list(
            cats_layer.cats
        )

        for cat in cats:
            # Biologicky narozené kočky mají age_days.
            # Kvantově manifestované kočky bez známého
            # biologického věku zatím automaticky nestárnou.
            if "age_days" in cat:
                age_result = (
                    self.development_resolver
                    .advance_age(
                        cat,
                        days=1
                    )
                )

                age_advances.append(
                    age_result
                )

            reproduction = cat.get(
                "reproduction",
                {}
            )

            estrous_result = (
                self.estrous_cycle_resolver
                .tick_day(
                    cat,
                    day=day
                )
            )

            estrous_cycle_results.append(
                estrous_result
            )

            if not reproduction.get(
                "pregnant",
                False
            ):
                continue

            pregnancy_result = (
                self.mating_resolver
                .advance_pregnancy(
                    cat,
                    days=1
                )
            )

            pregnancy_advances.append(
                pregnancy_result
            )

            if not pregnancy_result.get(
                "ready_for_birth",
                False
            ):
                continue

            birth_result = (
                self.birth_resolver
                .give_birth(
                    cat,
                    current_day=day
                )
            )

            births.append(
                birth_result
            )

        event = {
            "name": (
                "cat_life_cycle_day_completed"
            ),
            "day": day,
            "cats_processed": len(cats),
            "age_advances": age_advances,
            "estrous_cycle_results": (
                estrous_cycle_results
            ),
            "pregnancy_advances": (
                pregnancy_advances
            ),
            "births": births
        }

        self.history.append(
            event
        )

        return event