from dataclasses import dataclass, field


@dataclass(slots=True)
class CatInnovationTreeState:
    innovation_id: str | None = None
    parent: str | None = None
    children: list = field(
        default_factory=list
    )
    generation: int = 0

    def register(
        self,
        innovation_id,
        parent,
        generation,
    ):
        self.innovation_id = innovation_id
        self.parent = parent
        self.generation = int(
            generation
        )

        return self

    def add_child(
        self,
        child_innovation_id,
    ):
        if (
            child_innovation_id
            not in self.children
        ):
            self.children.append(
                child_innovation_id
            )

        return self
