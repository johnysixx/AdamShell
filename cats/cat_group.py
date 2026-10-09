from core.entity.domain_object import DomainObject
from cats.cat_group_lifecycle_state import (
    CatGroupLifecycleState,
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

        super().__init__(
            **values
        )
