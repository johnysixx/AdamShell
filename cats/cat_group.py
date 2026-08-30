from core.entity.component_object import ComponentObject


class CatGroupCulture(ComponentObject):
    pass


class CatGroup(ComponentObject):

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
