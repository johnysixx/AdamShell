from universe.logger import UniverseLogger


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
        profile=None
    ):
        amount_litres = float(
            amount_litres
        )

        if amount_litres <= 0.0:
            raise ValueError(
                "Lemonade amount must be positive."
            )

        self.amount_litres += amount_litres
        self.total_added_litres += amount_litres

        previous_amount = (
            self.amount_litres - amount_litres
        )

        if profile is not None:
            profile = dict(profile)

            self.batch_history.append({
                "amount_litres": amount_litres,
                "source": source,
                "profile": profile
            })

            self.current_profile = (
                self._mix_profiles(
                    current_profile=self.current_profile,
                    current_amount=previous_amount,
                    added_profile=profile,
                    added_amount=amount_litres
                )
            )

        event = {
            "name": "lemonade_added",
            "source": source,
            "amount_litres": amount_litres,
            "remaining_litres": self.amount_litres
        }

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

        return event

    def _copy_profile(self, profile):
        if profile is None:
            return None

        return {
            "traits": dict(
                profile.get("traits", {})
            ),
            "source_count": profile.get(
                "source_count",
                0
            ),
            "source_mass": profile.get(
                "source_mass",
                0.0
            ),
            "source_cronenbergs": list(
                profile.get(
                    "source_cronenbergs",
                    []
                )
            ),
            "entangled_pair_count": profile.get(
                "entangled_pair_count",
                0
            ),
            "entanglement_strength": profile.get(
                "entanglement_strength",
                0.0
            ),
            "entangled_pairs": [
                dict(pair)
                for pair in profile.get(
                    "entangled_pairs",
                    []
                )
            ],
            "dominant_trait": profile.get(
                "dominant_trait"
            )
        }

    def _mix_profiles(
        self,
        current_profile,
        current_amount,
        added_profile,
        added_amount
    ):
        if current_profile is None:
            return dict(added_profile)

        total_amount = (
            float(current_amount)
            + float(added_amount)
        )

        if total_amount <= 0.0:
            return dict(added_profile)

        current_traits = current_profile.get(
            "traits",
            {}
        )

        added_traits = added_profile.get(
            "traits",
            {}
        )

        trait_names = set(
            current_traits
        ) | set(added_traits)

        mixed_traits = {}

        for trait_name in trait_names:
            current_value = float(
                current_traits.get(
                    trait_name,
                    0.0
                )
            )

            added_value = float(
                added_traits.get(
                    trait_name,
                    0.0
                )
            )

            mixed_traits[trait_name] = round(
                (
                    current_value * current_amount
                    + added_value * added_amount
                ) / total_amount,
                4
            )

        source_ids = list(dict.fromkeys(
            list(
                current_profile.get(
                    "source_cronenbergs",
                    []
                )
            )
            + list(
                added_profile.get(
                    "source_cronenbergs",
                    []
                )
            )
        ))

        return {
            "traits": mixed_traits,
            "source_count": len(source_ids),
            "source_mass": round(
                float(
                    current_profile.get(
                        "source_mass",
                        0.0
                    )
                )
                + float(
                    added_profile.get(
                        "source_mass",
                        0.0
                    )
                ),
                4
            ),
            "source_cronenbergs": source_ids,
            "entangled_pair_count": (
                int(
                    current_profile.get(
                        "entangled_pair_count",
                        0
                    )
                )
                + int(
                    added_profile.get(
                        "entangled_pair_count",
                        0
                    )
                )
            ),
            "entanglement_strength": round(
                float(
                    current_profile.get(
                        "entanglement_strength",
                        0.0
                    )
                )
                + float(
                    added_profile.get(
                        "entanglement_strength",
                        0.0
                    )
                ),
                4
            ),
            "entangled_pairs": (
                list(
                    current_profile.get(
                        "entangled_pairs",
                        []
                    )
                )
                + list(
                    added_profile.get(
                        "entangled_pairs",
                        []
                    )
                )
            ),
            "dominant_trait": max(
                mixed_traits,
                key=mixed_traits.get
            ) if mixed_traits else None
        }

    def serve(
        self,
        drinker_name,
        location
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

        serving_profile = self._copy_profile(
            self.current_profile
        )

        event = {
            "name": "free_lemonade_served",
            "drinker": drinker_name,
            "location": location,
            "amount_litres": (
                self.serving_size_litres
            ),
            "price": 0,
            "lemonade_profile": serving_profile,
            "remaining_litres": (
                self.amount_litres
            )
        }

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

        return event

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
            "current_profile": self.current_profile,
            "batch_count": len(self.batch_history),
            "total_served_litres": (
                self.total_served_litres
            )
        }
