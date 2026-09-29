from core.entity.component_object import ComponentObject
from cats.cat_group_lifecycle_state import (
    CatGroupLifecycleState,
)


class CatGroupCulture(ComponentObject):
    pass


class CatGroup(ComponentObject):

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

    def to_dict(self):
        snapshot = super().to_dict()
        snapshot.pop("_state", None)
        snapshot["state"] = self.state.value
        return snapshot
