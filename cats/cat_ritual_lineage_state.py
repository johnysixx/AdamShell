from dataclasses import dataclass, field

from cats.cat_lineage_children_registry import (
    CatLineageChildrenRegistry,
)


@dataclass(slots=True)
class CatRitualLineageState:

    root_ritual: str | None = None

    versions: list = field(
        default_factory=list
    )

    children: CatLineageChildrenRegistry = field(
        default_factory=(
            CatLineageChildrenRegistry
        )
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.children,
            CatLineageChildrenRegistry,
        ):
            raise TypeError(
                "Cat ritual lineage children must use "
                "CatLineageChildrenRegistry."
            )

    def register_version(
        self,
        ritual_name,
    ):
        if ritual_name not in self.versions:
            self.versions.append(
                ritual_name
            )

        return self

    def register_child(
        self,
        parent_ritual,
        child_ritual,
    ):
        self.register_version(
            child_ritual
        )

        self.children.register(
            parent_ritual,
            child_ritual,
        )

        return self

    def children_for(
        self,
        parent_ritual,
    ):
        return self.children.children_for(
            parent_ritual
        )
