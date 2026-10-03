from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupNormDefinedEvent:
    group_id: str
    norm_id: str
    norm_name: str
    category: str

    name: str = field(
        default="cat_group_norm_defined",
        init=False,
    )

    defined: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "group_id": self.group_id,
            "norm_id": self.norm_id,
            "norm_name": self.norm_name,
            "category": self.category,
            "defined": self.defined,
        }
