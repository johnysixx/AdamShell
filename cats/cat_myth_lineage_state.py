from dataclasses import dataclass, field

from cats.cat_lineage_children_registry import (
    CatLineageChildrenRegistry,
)


@dataclass(slots=True)
class CatMythLineageState:

    root_myth: str | None = None

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
                "Cat myth lineage children must use "
                "CatLineageChildrenRegistry."
            )

    def register_version(
        self,
        myth_id,
    ):
        if myth_id not in self.versions:
            self.versions.append(
                myth_id
            )

        return self

    def register_child(
        self,
        parent_myth_id,
        child_myth_id,
    ):
        self.register_version(
            child_myth_id
        )

        self.children.register(
            parent_myth_id,
            child_myth_id,
        )

        return self

    def children_for(
        self,
        parent_myth_id,
    ):
        return self.children.children_for(
            parent_myth_id
        )
