from core.entity.domain_object import DomainObject
from cats.cat_group_lifecycle_state import (
    CatGroupLifecycleState,
)
from cats.cat_group_memory_registry import (
    CatGroupMemoryRegistry,
)
from cats.cat_group_territory_state import (
    CatGroupTerritories,
)
from cats.cat_group_diplomacy_state import (
    CatGroupDiplomacyRegistry,
)
from cats.cat_group_knowledge_registry import (
    CatGroupKnowledgeRegistry,
)
from cats.cat_group_culture_registry import (
    CatGroupPreferenceRegistry,
    CatGroupTraditionRegistry,
)
from cats.cat_group_myth_registry import (
    CatGroupMythLineageRegistry,
    CatGroupMythRegistry,
)
from cats.cat_group_innovation_registry import (
    CatGroupInnovationRegistry,
    CatGroupInnovationTreeRegistry,
)


class CatGroupCulture(DomainObject):

    def __init__(
        self,
        **values
    ):
        for reserved_name in (
            "traditions",
            "preferences",
        ):
            if reserved_name in values:
                raise TypeError(
                    "Cat group culture registry state "
                    "cannot be supplied as mapping data."
                )

        self.traditions = (
            CatGroupTraditionRegistry()
        )

        self.preferences = (
            CatGroupPreferenceRegistry()
        )

        super().__init__(
            **values
        )


class CatGroup(DomainObject):

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if not isinstance(
            state,
            CatGroupLifecycleState,
        ):
            raise TypeError(
                "Cat group state must use "
                "CatGroupLifecycleState."
            )

        self._state = state

    def __init__(
        self,
        **values
    ):
        culture = values.get(
            "culture"
        )

        if isinstance(
            culture,
            dict
        ):
            values["culture"] = (
                CatGroupCulture(
                    **culture
                )
            )

        group_memory = values.get(
            "group_memory"
        )

        if not isinstance(
            group_memory,
            CatGroupMemoryRegistry,
        ):
            raise TypeError(
                "Cat group memory must use "
                "CatGroupMemoryRegistry."
            )

        territories = values.get(
            "territories"
        )

        if not isinstance(
            territories,
            CatGroupTerritories,
        ):
            raise TypeError(
                "Cat group territories must use "
                "CatGroupTerritories."
            )

        diplomacy = values.get(
            "diplomacy"
        )

        if not isinstance(
            diplomacy,
            CatGroupDiplomacyRegistry,
        ):
            raise TypeError(
                "Cat group diplomacy must use "
                "CatGroupDiplomacyRegistry."
            )

        knowledge = values.get(
            "knowledge"
        )

        if not isinstance(
            knowledge,
            CatGroupKnowledgeRegistry,
        ):
            raise TypeError(
                "Cat group knowledge must use "
                "CatGroupKnowledgeRegistry."
            )

        myths = values.get(
            "myths"
        )

        if not isinstance(
            myths,
            CatGroupMythRegistry,
        ):
            raise TypeError(
                "Cat group myths must use "
                "CatGroupMythRegistry."
            )

        myth_lineages = values.get(
            "myth_lineages"
        )

        if not isinstance(
            myth_lineages,
            CatGroupMythLineageRegistry,
        ):
            raise TypeError(
                "Cat group myth lineages must use "
                "CatGroupMythLineageRegistry."
            )

        innovations = values.get(
            "innovations"
        )

        if not isinstance(
            innovations,
            CatGroupInnovationRegistry,
        ):
            raise TypeError(
                "Cat group innovations must use "
                "CatGroupInnovationRegistry."
            )

        innovation_tree = values.get(
            "innovation_tree"
        )

        if not isinstance(
            innovation_tree,
            CatGroupInnovationTreeRegistry,
        ):
            raise TypeError(
                "Cat group innovation tree must use "
                "CatGroupInnovationTreeRegistry."
            )

        super().__init__(
            **values
        )
