from cats.cat_culture_objects import (
    CatGroupInnovation,
)
from cats.cat_innovation_tree_state import (
    CatInnovationTreeState,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatGroupInnovationRegistry(
    DomainObject
):

    def __init__(
        self,
    ):
        self._records = []

    @property
    def is_empty(
        self,
    ):
        return not self._records

    @property
    def count(
        self,
    ):
        return len(
            self._records
        )

    def store(
        self,
        innovation,
    ):
        if not isinstance(
            innovation,
            CatGroupInnovation,
        ):
            raise TypeError(
                "Cat group innovation registry requires "
                "CatGroupInnovation."
            )

        innovation_id = getattr(
            innovation,
            "innovation_id",
            None,
        )

        if (
            not isinstance(
                innovation_id,
                str,
            )
            or not innovation_id
        ):
            raise ValueError(
                "Stored cat group innovation requires "
                "innovation_id."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.innovation_id
                == innovation_id
            ):
                self._records[
                    index
                ] = innovation

                return innovation

        self._records.append(
            innovation
        )

        return innovation

    def record(
        self,
        innovation_id,
    ):
        innovation_id = str(
            innovation_id
        )

        for innovation in self.records():
            if (
                innovation.innovation_id
                == innovation_id
            ):
                return innovation

        return None

    def has(
        self,
        innovation_id,
    ):
        return (
            self.record(
                innovation_id
            )
            is not None
        )

    def release(
        self,
        innovation_id,
    ):
        innovation_id = str(
            innovation_id
        )

        for index, innovation in enumerate(
            self.records()
        ):
            if (
                innovation.innovation_id
                == innovation_id
            ):
                del self._records[
                    index
                ]

                return innovation

        return None

    def records(
        self,
    ):
        for innovation in self._records:
            if not isinstance(
                innovation,
                CatGroupInnovation,
            ):
                raise TypeError(
                    "Cat group innovation registry "
                    "contains invalid runtime state."
                )

            innovation_id = getattr(
                innovation,
                "innovation_id",
                None,
            )

            if (
                not isinstance(
                    innovation_id,
                    str,
                )
                or not innovation_id
            ):
                raise ValueError(
                    "Cat group innovation record "
                    "requires innovation_id."
                )

        return tuple(
            self._records
        )


class CatGroupInnovationTreeRegistry(
    DomainObject
):

    def __init__(
        self,
    ):
        self._records = []

    @property
    def is_empty(
        self,
    ):
        return not self._records

    @property
    def count(
        self,
    ):
        return len(
            self._records
        )

    def store(
        self,
        state,
    ):
        if not isinstance(
            state,
            CatInnovationTreeState,
        ):
            raise TypeError(
                "Cat group innovation tree registry "
                "requires CatInnovationTreeState."
            )

        innovation_id = getattr(
            state,
            "innovation_id",
            None,
        )

        if (
            not isinstance(
                innovation_id,
                str,
            )
            or not innovation_id
        ):
            raise ValueError(
                "Stored cat innovation tree state "
                "requires innovation_id."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.innovation_id
                == innovation_id
            ):
                self._records[
                    index
                ] = state

                return state

        self._records.append(
            state
        )

        return state

    def record(
        self,
        innovation_id,
    ):
        innovation_id = str(
            innovation_id
        )

        for state in self.records():
            if (
                state.innovation_id
                == innovation_id
            ):
                return state

        return None

    def has(
        self,
        innovation_id,
    ):
        return (
            self.record(
                innovation_id
            )
            is not None
        )

    def release(
        self,
        innovation_id,
    ):
        innovation_id = str(
            innovation_id
        )

        for index, state in enumerate(
            self.records()
        ):
            if (
                state.innovation_id
                == innovation_id
            ):
                del self._records[
                    index
                ]

                return state

        return None

    def records(
        self,
    ):
        for state in self._records:
            if not isinstance(
                state,
                CatInnovationTreeState,
            ):
                raise TypeError(
                    "Cat group innovation tree registry "
                    "contains invalid runtime state."
                )

            innovation_id = getattr(
                state,
                "innovation_id",
                None,
            )

            if (
                not isinstance(
                    innovation_id,
                    str,
                )
                or not innovation_id
            ):
                raise ValueError(
                    "Cat innovation tree record "
                    "requires innovation_id."
                )

        return tuple(
            self._records
        )
