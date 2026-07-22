class AbilitySet:

    def __init__(
        self,
        owner=None
    ):
        self.owner = owner
        self._abilities = {}

    def grant(
        self,
        name,
        ability
    ):
        if name in self._abilities:
            return False

        self._abilities[name] = ability

        return True

    def revoke(
        self,
        name
    ):
        if name not in self._abilities:
            return False

        del self._abilities[name]

        return True

    def has(
        self,
        name
    ):
        return name in self._abilities

    def get(
        self,
        name
    ):
        return self._abilities.get(
            name
        )

    def use(
        self,
        name,
        method_name,
        **kwargs
    ):
        ability = self.get(
            name
        )

        if ability is None:
            raise ValueError(
                f"Ability is not granted: {name}"
            )

        method = getattr(
            ability,
            method_name,
            None
        )

        if method is None:
            raise ValueError(
                f"Ability does not support: "
                f"{method_name}"
            )

        return method(
            **kwargs
        )

    @property
    def names(self):
        return list(
            self._abilities.keys()
        )

    @property
    def public_state(self):
        return {
            "owner": getattr(
                self.owner,
                "name",
                None
            ),
            "ability_count": len(
                self._abilities
            ),
            "abilities": self.names
        }
