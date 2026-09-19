from dataclasses import dataclass, field


@dataclass(slots=True)
class CatAccessRules:
    can_access_anywhere: bool = True
    access_via: list = field(
        default_factory=lambda: [
            "boxes",
            "cat_doors",
        ]
    )

    def to_dict(self):
        return {
            "can_access_anywhere": (
                self.can_access_anywhere
            ),
            "access_via": list(
                self.access_via
            ),
        }
