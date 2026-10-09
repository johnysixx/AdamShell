class DomainObject:

    def __init__(
        self,
        **values
    ):
        for key, value in values.items():
            setattr(
                self,
                key,
                value,
            )

    def __eq__(
        self,
        other,
    ):
        if type(other) is type(self):
            return (
                vars(self)
                == vars(other)
            )

        return NotImplemented

    def __repr__(self):
        fields = ", ".join(
            f"{key}={value!r}"
            for key, value
            in vars(self).items()
        )

        return (
            f"<{self.__class__.__name__} "
            f"{fields}>"
        )
