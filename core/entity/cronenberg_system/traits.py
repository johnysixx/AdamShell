import random


class CronenbergTraits:

    TRAIT_NAMES = (
        "acidity",
        "sweetness",
        "bitterness",
        "viscosity",
        "stability",
        "dark_energy_affinity",
        "growth_efficiency",
        "cat_scent",
        "quantum_coherence"
    )

    def __init__(
        self,
        error,
        source_component,
        source_operation,
        quantum_tick=None,
        rng=None
    ):
        rng = rng or random

        self.source_component = source_component
        self.source_operation = source_operation
        self.error_type = type(error).__name__
        self.quantum_tick = quantum_tick

        self.values = {
            trait_name: rng.uniform(0.50, 1.50)
            for trait_name in self.TRAIT_NAMES
        }

        self.birth_influences = []

        self._apply_error_influence()
        self._apply_source_influence()
        self._apply_operation_influence()
        self._normalize()

    def _shift(
        self,
        trait_name,
        amount,
        reason
    ):
        old_value = self.values[trait_name]

        self.values[trait_name] = (
            old_value + float(amount)
        )

        self.birth_influences.append({
            "trait": trait_name,
            "amount": float(amount),
            "reason": reason
        })

    def _apply_error_influence(self):
        influences = {
            "RuntimeError": (
                ("stability", -0.15),
                ("dark_energy_affinity", 0.15)
            ),
            "ValueError": (
                ("acidity", 0.15),
                ("stability", -0.10)
            ),
            "MemoryError": (
                ("growth_efficiency", 0.20),
                ("viscosity", 0.15)
            ),
            "OverflowError": (
                ("sweetness", 0.10),
                ("growth_efficiency", 0.15)
            ),
            "TimeoutError": (
                ("viscosity", 0.20),
                ("growth_efficiency", -0.10)
            ),
            "RecursionError": (
                ("quantum_coherence", 0.25),
                ("stability", -0.15)
            ),
            "AttributeError": (
                ("bitterness", 0.15),
                ("cat_scent", 0.10)
            ),
            "KeyError": (
                ("acidity", 0.10),
                ("quantum_coherence", 0.10)
            ),
            "TypeError": (
                ("bitterness", 0.10),
                ("dark_energy_affinity", 0.10)
            )
        }

        for trait_name, amount in influences.get(
            self.error_type,
            ()
        ):
            self._shift(
                trait_name,
                amount,
                f"error_type:{self.error_type}"
            )

    def _apply_source_influence(self):
        source = str(
            self.source_component
        ).lower()

        if "geometry" in source:
            self._shift(
                "quantum_coherence",
                0.15,
                "source:geometry"
            )
            self._shift(
                "viscosity",
                0.10,
                "source:geometry"
            )

        if "cat" in source:
            self._shift(
                "cat_scent",
                0.20,
                "source:cat"
            )
            self._shift(
                "stability",
                -0.05,
                "source:cat"
            )

        if "box" in source:
            self._shift(
                "bitterness",
                0.10,
                "source:box"
            )
            self._shift(
                "quantum_coherence",
                0.10,
                "source:box"
            )

        if "entropy" in source:
            self._shift(
                "dark_energy_affinity",
                0.20,
                "source:entropy"
            )

    def _apply_operation_influence(self):
        operation = str(
            self.source_operation
        ).lower()

        if "paradox" in operation:
            self._shift(
                "quantum_coherence",
                0.20,
                "operation:paradox"
            )
            self._shift(
                "stability",
                -0.20,
                "operation:paradox"
            )

        if "collapse" in operation:
            self._shift(
                "acidity",
                0.10,
                "operation:collapse"
            )
            self._shift(
                "dark_energy_affinity",
                0.10,
                "operation:collapse"
            )

        if "travel" in operation:
            self._shift(
                "growth_efficiency",
                0.10,
                "operation:travel"
            )

        if "detour" in operation:
            self._shift(
                "cat_scent",
                0.15,
                "operation:detour"
            )
            self._shift(
                "viscosity",
                0.10,
                "operation:detour"
            )

    def _normalize(self):
        for trait_name in self.TRAIT_NAMES:
            self.values[trait_name] = round(
                max(
                    0.10,
                    min(
                        2.00,
                        self.values[trait_name]
                    )
                ),
                4
            )

    def get(
        self,
        trait_name,
        default=None
    ):
        return self.values.get(
            trait_name,
            default
        )

    def snapshot(self):
        return dict(
            self.values
        )

    @property
    def public_state(self):
        return {
            "values": self.snapshot(),
            "birth_influences": [
                dict(influence)
                for influence
                in self.birth_influences
            ],
            "source_component": (
                self.source_component
            ),
            "source_operation": (
                self.source_operation
            ),
            "error_type": self.error_type,
            "quantum_tick": self.quantum_tick
        }
