from copy import deepcopy

from cats.cat_innovation_tree_state import (
    CatInnovationTreeState,
)

class CatGroupInnovationTreeSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def register(
        self,
        group_id,
        innovation_id,
        parent_innovation_id=None,
    ):
        group = self.group_system._group(
            group_id
        )

        innovation = group.innovations.get(
            innovation_id
        )

        if innovation is None:
            return {
                'name':
                    'cat_innovation_tree_denied',
                'reason':
                    'unknown_innovation',
                'registered':
                    False,
            }

        parent_state = None
        generation = 0

        if parent_innovation_id is not None:
            parent_state = self._state(
                group,
                parent_innovation_id,
                create=False,
            )

            generation = (
                int(
                    parent_state.generation
                )
                if parent_state is not None
                else 0
            ) + 1

        state = self._state(
            group,
            innovation_id,
            create=True,
        )

        state.register(
            innovation_id=innovation_id,
            parent=parent_innovation_id,
            generation=generation,
        )

        if parent_state is not None:
            parent_state.add_child(
                innovation_id
            )

        innovation.parent_innovation = (
            parent_innovation_id
        )

        innovation.generation = (
            state.generation
        )

        return {
            'name':
                'cat_innovation_tree_registered',
            'group_id':
                group_id,
            'innovation_id':
                innovation_id,
            'parent':
                parent_innovation_id,
            'generation':
                innovation.generation,
            'registered':
                True,
        }

    def descendants(
        self,
        group_id,
        innovation_id,
    ):
        group = self.group_system._group(
            group_id
        )

        state = self._state(
            group,
            innovation_id,
            create=False,
        )

        if state is None:
            return []

        result = []
        stack = list(
            state.children
        )

        while stack:
            current = stack.pop(0)

            result.append(
                current
            )

            current_state = self._state(
                group,
                current,
                create=False,
            )

            if current_state is not None:
                stack.extend(
                    current_state.children
                )

        return result

    def tree(
        self,
        group_id,
    ):
        group = self.group_system._group(
            group_id
        )

        for innovation_id in (
            group.innovation_tree
        ):
            self._state(
                group,
                innovation_id,
                create=False,
            )

        return deepcopy(
            group.innovation_tree
        )

    def _state(
        self,
        group,
        innovation_id,
        create=False,
    ):
        state = group.innovation_tree.get(
            innovation_id
        )

        if state is None:
            if not create:
                return None

            state = CatInnovationTreeState(
                innovation_id=innovation_id
            )

            group.innovation_tree[
                innovation_id
            ] = state

        elif not isinstance(
            state,
            CatInnovationTreeState,
        ):
            raise TypeError(
                'Cat innovation tree record '
                'must be '
                'CatInnovationTreeState.'
            )

        return state
