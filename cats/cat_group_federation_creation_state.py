from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatFederationCreatedResult:
    federation_id: str
    founder_group: str

    name: str = field(
        default="cat_federation_created",
        init=False,
    )

    created: bool = field(
        default=True,
        init=False,
    )
