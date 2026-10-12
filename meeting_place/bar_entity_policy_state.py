from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BarEntityPolicyDecision:
    entity_id: str | None
    entity_class: str
    access_mode: str
    glass_mode: str
    service_mode: str

    def __post_init__(self):
        if self.entity_id is not None:
            object.__setattr__(
                self,
                "entity_id",
                str(self.entity_id),
            )

        for field_name in (
            "entity_class",
            "access_mode",
            "glass_mode",
            "service_mode",
        ):
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    "Bar entity policy "
                    f"{field_name} must be str."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )
