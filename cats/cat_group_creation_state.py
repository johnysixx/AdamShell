from dataclasses import dataclass, field

from cats.cat_group import CatGroup


@dataclass(slots=True, frozen=True)
class CatGroupCreationDeniedResult:
    cat: str
    reason: str

    name: str = field(
        default="cat_group_creation_denied",
        init=False,
    )

    created: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupCreatedEvent:
    group_id: str
    group_name: str
    founder: str

    name: str = field(
        default="cat_group_created",
        init=False,
    )

    created: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupCreatedResult:
    group_id: str
    group_name: str
    founder: str
    group: CatGroup

    name: str = field(
        default="cat_group_created",
        init=False,
    )

    created: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.group,
            CatGroup,
        ):
            raise TypeError(
                "Cat group creation result "
                "must contain CatGroup."
            )
