from copy import deepcopy

from cats.cat_myth_lineage_state import (
    CatMythLineageState,
)

class CatGroupMythLineageSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def register_origin(self, group_id, myth_id):
        group = self.group_system._group(group_id)
        myth = group.myths.get(myth_id)
        if myth is None:
            return {'name': 'cat_myth_lineage_denied', 'reason': 'unknown_myth', 'registered': False}
        lineage = self._lineage(
            group,
            myth_id,
            create=True,
        )

        lineage.register_version(
            myth_id
        )
        myth.lineage_root = myth_id
        myth.parent_version = None
        myth.generation = 0
        return {'name': 'cat_myth_lineage_registered', 'group_id': group_id, 'myth_id': myth_id, 'registered': True}

    def register_descendant(self, group_id, root_myth_id, parent_myth_id, child_myth_id):
        group = self.group_system._group(group_id)
        lineage = self._lineage(
            group,
            root_myth_id,
            create=True,
        )

        lineage.register_version(
            root_myth_id
        )

        lineage.register_child(
            parent_myth_id,
            child_myth_id,
        )
        return {'name': 'cat_myth_descendant_registered', 'group_id': group_id, 'root_myth_id': root_myth_id, 'parent_myth_id': parent_myth_id, 'child_myth_id': child_myth_id, 'registered': True}

    def lineage(
        self,
        group_id,
        root_myth_id,
    ):
        group = self.group_system._group(
            group_id
        )

        lineage = self._lineage(
            group,
            root_myth_id,
            create=False,
        )

        return deepcopy(lineage)

    def _lineage(
        self,
        group,
        root_myth_id,
        create=False,
    ):
        lineage = group.myth_lineages.get(
            root_myth_id
        )

        if lineage is None:
            if not create:
                return None

            lineage = (
                CatMythLineageState(
                    root_myth=root_myth_id
                )
            )

            group.myth_lineages[
                root_myth_id
            ] = lineage

        elif not isinstance(
            lineage,
            CatMythLineageState,
        ):
            raise TypeError(
                'Cat myth lineage record must be '
                'CatMythLineageState.'
            )

        return lineage
