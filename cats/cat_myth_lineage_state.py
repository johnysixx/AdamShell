from dataclasses import dataclass, field


@dataclass(slots=True)
class CatMythLineageState:
    root_myth: str | None = None
    versions: list = field(
        default_factory=list
    )
    children: dict = field(
        default_factory=dict
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

        children = self.children.get(
            parent_myth_id
        )

        if children is None:
            children = []

            self.children[
                parent_myth_id
            ] = children

        if child_myth_id not in children:
            children.append(
                child_myth_id
            )

        return self
