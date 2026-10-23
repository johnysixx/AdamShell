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


class CatGroupCulture(DomainObject):
    pass


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

        super().__init__(
            **values
        )
