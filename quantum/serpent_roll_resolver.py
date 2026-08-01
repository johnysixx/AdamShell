import random
from copy import deepcopy


class SerpentRollResolver:

    SMALL_EFFECTS = (
        "quantum_tick",
        "quantum_box",
        "quantum_geometry_shift"
    )

    LARGE_EFFECTS = (
        "quantum_error",
        "cat_manifestation",
        "cronenberg_quantum_counterpart"
    )

    ALL_EFFECTS = (
        SMALL_EFFECTS
        + LARGE_EFFECTS
    )

    def __init__(self):
        self.name = "serpent_roll_resolver"
        self.history = []

    def resolve(
        self,
        public_roll,
        rng=None
    ):
        rng = rng or random

        if not isinstance(public_roll, dict):
            raise TypeError(
                "Serpent roll must be a public event."
            )

        if public_roll.get("name") != (
            "serpent_d20_rolled"
        ):
            raise ValueError(
                "Invalid Serpent d20 event."
            )

        value = int(
            public_roll["value"]
        )

        if value < 1 or value > 20:
            raise ValueError(
                "Serpent d20 value must be 1-20."
            )

        effect_count = self._effect_count(
            value=value,
            rng=rng
        )

        require_large = self._requires_large_effect(
            value=value,
            rng=rng
        )

        selected = self._select_effects(
            effect_count=effect_count,
            require_large=require_large,
            value=value,
            rng=rng
        )

        event = {
            "name": "serpent_roll_resolved",
            "roll_id": public_roll["roll_id"],
            "value": value,
            "intensity": self._intensity(value),
            "effect_count": len(selected),
            "selected_effects": selected,
            "all_effects_triggered": (
                set(selected)
                == set(self.ALL_EFFECTS)
            ),
            "visibility": "universe_only"
        }

        self.history.append(event)

        return deepcopy(event)

    def _effect_count(
        self,
        value,
        rng
    ):
        if value <= 5:
            # Nízký hod může vzácně neudělat nic.
            if rng.random() < 0.08:
                return 0

            return 1

        if value <= 10:
            return rng.randint(1, 2)

        if value <= 14:
            return rng.randint(2, 4)

        if value <= 19:
            return rng.randint(3, 6)

        # Přirozená dvacítka může spustit
        # několik efektů nebo úplně všechny.
        if rng.random() < 0.50:
            return len(self.ALL_EFFECTS)

        return rng.randint(
            5,
            len(self.ALL_EFFECTS)
        )

    def _requires_large_effect(
        self,
        value,
        rng
    ):
        if value <= 5:
            return rng.random() < 0.02

        if value <= 10:
            return rng.random() < 0.10

        if value <= 14:
            return rng.random() < 0.35

        if value <= 19:
            return rng.random() < 0.75

        return True

    def _select_effects(
        self,
        effect_count,
        require_large,
        value,
        rng
    ):
        if effect_count <= 0:
            return []

        if effect_count >= len(
            self.ALL_EFFECTS
        ):
            effects = list(
                self.ALL_EFFECTS
            )

            rng.shuffle(effects)

            return effects

        pool = list(
            self.ALL_EFFECTS
        )

        selected = []

        if require_large:
            large_effect = rng.choice(
                list(self.LARGE_EFFECTS)
            )

            selected.append(
                large_effect
            )

            pool.remove(
                large_effect
            )

        remaining_count = (
            effect_count
            - len(selected)
        )

        if remaining_count > 0:
            selected.extend(
                rng.sample(
                    pool,
                    remaining_count
                )
            )

        # U vysokých hodů chceme zvýšit šanci,
        # že mezi výsledky bude více velkých jevů.
        if value >= 15:
            selected = self._promote_large_effects(
                selected=selected,
                target_count=effect_count,
                rng=rng
            )

        return selected

    def _promote_large_effects(
        self,
        selected,
        target_count,
        rng
    ):
        selected = list(selected)

        large_count = sum(
            1
            for effect in selected
            if effect in self.LARGE_EFFECTS
        )

        desired_large_count = min(
            target_count,
            2
        )

        while large_count < desired_large_count:
            available_large = [
                effect
                for effect in self.LARGE_EFFECTS
                if effect not in selected
            ]

            removable_small = [
                effect
                for effect in selected
                if effect in self.SMALL_EFFECTS
            ]

            if (
                not available_large
                or not removable_small
            ):
                break

            replacement = rng.choice(
                available_large
            )

            removed = rng.choice(
                removable_small
            )

            selected.remove(
                removed
            )

            selected.append(
                replacement
            )

            large_count += 1

        return selected

    def _intensity(self, value):
        if value <= 5:
            return "low"

        if value <= 10:
            return "moderate"

        if value <= 14:
            return "high"

        if value <= 19:
            return "severe"

        return "unbounded"

    @property
    def public_state(self):
        return {
            "name": self.name,
            "resolution_count": len(
                self.history
            )
        }


