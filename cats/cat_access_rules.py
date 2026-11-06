from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CatAccessRules:
    can_access_anywhere: bool = True
    access_via: tuple[str, ...] = (
        "boxes",
        "cat_doors",
    )

    def __post_init__(self):
        if not isinstance(
            self.can_access_anywhere,
            bool,
        ):
            raise TypeError(
                "Cat access permission must be boolean."
            )

        if not isinstance(
            self.access_via,
            tuple,
        ):
            raise TypeError(
                "Cat access methods must use a tuple."
            )

        if any(
            not isinstance(method, str)
            or not method.strip()
            for method in self.access_via
        ):
            raise TypeError(
                "Cat access methods must be "
                "nonempty strings."
            )
