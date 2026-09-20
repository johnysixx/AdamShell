from dataclasses import dataclass


@dataclass(slots=True)
class BarPaymentState:
    name: str
    entity: str | None
    payment_kind: str
    existence_paid_pct: float | None = None
    energy_paid_j: float | None = None
    idea_existence_gain_pct: float | None = None
    existence_converted_to_energy_pct: float | None = None
    generated_energy_j: float | None = None
    bar_energy_j: float | None = None
    entity_type: str | None = None

    def to_dict(self):
        result = {
            "name": self.name,
            "entity": self.entity,
            "payment_kind": self.payment_kind,
        }

        for name, value in (
            ("existence_paid_pct", self.existence_paid_pct),
            ("energy_paid_j", self.energy_paid_j),
            ("idea_existence_gain_pct", self.idea_existence_gain_pct),
            (
                "existence_converted_to_energy_pct",
                self.existence_converted_to_energy_pct,
            ),
            ("generated_energy_j", self.generated_energy_j),
            ("bar_energy_j", self.bar_energy_j),
        ):
            if value is not None:
                result[name] = value

        if self.entity_type is not None or self.payment_kind == "unsupported":
            result["entity_type"] = self.entity_type

        return result
