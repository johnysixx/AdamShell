from dataclasses import dataclass, field


@dataclass(
    slots=True,
    frozen=True,
)
class CatLineageBranchState:

    parent: str
    children: tuple[str, ...] = ()

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "parent",
            str(
                self.parent
            ),
        )

        object.__setattr__(
            self,
            "children",
            tuple(
                str(child)
                for child
                in self.children
            ),
        )


@dataclass(slots=True)
class CatLineageChildrenRegistry:

    _branches: list = field(
        default_factory=list
    )

    @property
    def is_empty(
        self,
    ):
        return not self._branches

    def register(
        self,
        parent,
        child,
    ):
        parent = str(
            parent
        )

        child = str(
            child
        )

        for index, branch in enumerate(
            self.branches()
        ):
            if branch.parent != parent:
                continue

            if child in branch.children:
                return branch

            updated = (
                CatLineageBranchState(
                    parent=branch.parent,
                    children=(
                        *branch.children,
                        child,
                    ),
                )
            )

            self._branches[
                index
            ] = updated

            return updated

        branch = (
            CatLineageBranchState(
                parent=parent,
                children=(
                    child,
                ),
            )
        )

        self._branches.append(
            branch
        )

        return branch

    def branch(
        self,
        parent,
    ):
        parent = str(
            parent
        )

        for branch in self.branches():
            if branch.parent == parent:
                return branch

        return None

    def children_for(
        self,
        parent,
    ):
        branch = self.branch(
            parent
        )

        if branch is None:
            return ()

        return branch.children

    def branches(
        self,
    ):
        for branch in self._branches:
            if not isinstance(
                branch,
                CatLineageBranchState,
            ):
                raise TypeError(
                    "Cat lineage children registry "
                    "contains invalid runtime state."
                )

        return tuple(
            self._branches
        )
