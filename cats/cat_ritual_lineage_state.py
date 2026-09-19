from dataclasses import dataclass, field


@dataclass(slots=True)
class CatRitualLineageState:
    root_ritual: str | None = None
    versions: list = field(
        default_factory=list
    )
    children: dict = field(
        default_factory=dict
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

        children = self.children.get(
            parent_ritual
        )

        if children is None:
            children = []

            self.children[
                parent_ritual
            ] = children

        if child_ritual not in children:
            children.append(
                child_ritual
            )

        return self
