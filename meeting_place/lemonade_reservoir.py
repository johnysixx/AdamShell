from universe.logger import UniverseLogger
from .lemonade_profile import (
    LemonadeAddedEvent,
    LemonadeBatchRecord,
    LemonadeProfile,
    LemonadeServedEvent,
    LemonadeTraitProfile,
)


class LemonadeReservoir:

    def __init__(self):
        self.name = "cronenberg_lemonade_reservoir"
        self.type = "physical_drink_reservoir"
        self.location = "behind_bar_counter"

        self.amount_litres = 0.0
        self.total_added_litres = 0.0
        self.total_served_litres = 0.0

        self.serving_size_litres = 0.5

        self.events = []
        self.batch_history = []
        self.current_profile = None

    @property
    def is_present(self):
        return self.amount_litres > 0.0

    @property
    def is_available(self):
        return (
            self.amount_litres
            >= self.serving_size_litres
        )

    def add_lemonade(
        self,
        amount_litres,
        source="cronenberg_processing",
        profile=None,
    ):
        amount_litres = float(
            amount_litres
        )

        if amount_litres <= 0.0:
            raise ValueError(
                "Lemonade amount must be positive."
            )

        if (
            profile is not None
            and not isinstance(
                profile,
                LemonadeProfile,
            )
        ):
            raise TypeError(
                "Lemonade reservoir requires "
                "LemonadeProfile objects."
            )

        self.amount_litres += amount_litres
        self.total_added_litres += amount_litres

        previous_amount = (
            self.amount_litres - amount_litres
        )

        if profile is not None:
            self.batch_history.append(
                LemonadeBatchRecord(
                    amount_litres=amount_litres,
                    source=source,
                    profile=profile,
                )
            )

            self.current_profile = (
                self._mix_profiles(
                    current_profile=self.current_profile,
                    current_amount=previous_amount,
                    added_profile=profile,
                    added_amount=amount_litres,
                )
            )

        event = LemonadeAddedEvent(
            source=source,
            amount_litres=amount_litres,
            remaining_litres=self.amount_litres,
        )

        self.events.append(
            event
        )

        UniverseLogger.event(
            f"LEMONADE ADDED: "
            f"{amount_litres:.2f} litres "
            f"FROM={source}"
        )

        UniverseLogger.event(
            f"LEMONADE AVAILABLE: "
            f"{self.amount_litres:.2f} litres"
        )

        return event.to_dict()

    def _mix_profiles(
        self,
        current_profile,
        current_amount,
        added_profile,
        added_amount,
    ):
        if current_profile is None:
            return added_profile

        if not isinstance(
            current_profile,
            LemonadeProfile,
        ):
            raise TypeError(
                "Current lemonade profile must be "
                "LemonadeProfile."
            )

        if not isinstance(
            added_profile,
            LemonadeProfile,
        ):
            raise TypeError(
                "Added lemonade profile must be "
                "LemonadeProfile."
            )

        total_amount = (
            float(current_amount)
            + float(added_amount)
        )

        if total_amount <= 0.0:
            return added_profile

        mixed_traits = {}

        for trait_name in (
            LemonadeTraitProfile.TRAIT_NAMES
        ):
            current_value = float(
                current_profile.traits.value_for(
                    trait_name,
                    0.0,
                )
            )

            added_value = float(
                added_profile.traits.value_for(
                    trait_name,
                    0.0,
                )
            )

            mixed_traits[trait_name] = round(
                (
                    current_value * current_amount
                    + added_value * added_amount
                ) / total_amount,
                4,
            )

        source_ids = []
        seen_source_ids = set()

        for source_id in (
            current_profile.source_cronenbergs
            + added_profile.source_cronenbergs
        ):
            if source_id in seen_source_ids:
                continue
            seen_source_ids.add(source_id)
            source_ids.append(source_id)

        dominant_trait = max(
            mixed_traits,
            key=mixed_traits.get,
        ) if mixed_traits else None

        return LemonadeProfile(
            traits=LemonadeTraitProfile(
                **mixed_traits
            ),
            source_mass=round(
                current_profile.source_mass
                + added_profile.source_mass,
                4,
            ),
            source_cronenbergs=tuple(
                source_ids
            ),
            entanglement_strength=round(
                current_profile.entanglement_strength
                + added_profile.entanglement_strength,
                4,
            ),
            entangled_pairs=(
                current_profile.entangled_pairs
                + added_profile.entangled_pairs
            ),
            dominant_trait=dominant_trait,
        )

    def serve(
        self,
        drinker_name,
        location,
    ):
        if not self.is_available:
            UniverseLogger.event(
                f"LEMONADE NOT AVAILABLE FOR "
                f"{drinker_name}"
            )

            return None

        self.amount_litres -= (
            self.serving_size_litres
        )

        self.total_served_litres += (
            self.serving_size_litres
        )

        event = LemonadeServedEvent(
            drinker=drinker_name,
            location=location,
            amount_litres=(
                self.serving_size_litres
            ),
            price=0,
            lemonade_profile=self.current_profile,
            remaining_litres=(
                self.amount_litres
            ),
        )

        self.events.append(
            event
        )

        UniverseLogger.event(
            f"LEMONADE REMAINING: {self.amount_litres:.2f} litres"
        )

        UniverseLogger.event(
            f"FREE LEMONADE SERVED TO "
            f"{drinker_name} "
            f"AT={location}"
        )

        if not self.is_present:
            UniverseLogger.event(
                "LEMONADE RESERVOIR IS EMPTY"
            )

        return event.to_dict()

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "present": self.is_present,
            "available": self.is_available,
            "amount_litres": self.amount_litres,
            "serving_size_litres": (
                self.serving_size_litres
            ),
            "total_added_litres": (
                self.total_added_litres
            ),
            "current_profile": (
                self.current_profile.to_dict()
                if self.current_profile is not None
                else None
            ),
            "batch_count": len(self.batch_history),
            "total_served_litres": (
                self.total_served_litres
            ),
        }
