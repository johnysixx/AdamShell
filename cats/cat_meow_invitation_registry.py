from dataclasses import dataclass, field

from cats.cat_social_objects import (
    CatMeowInvitation,
)


@dataclass(slots=True)
class CatMeowInvitationRegistry:

    _records: list = field(
        default_factory=list
    )

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
        invitation,
    ):
        if not isinstance(
            invitation,
            CatMeowInvitation,
        ):
            raise TypeError(
                "Cat MEOW invitation registry "
                "requires CatMeowInvitation."
            )

        invitation_id = getattr(
            invitation,
            "id",
            None,
        )

        if (
            not isinstance(
                invitation_id,
                str,
            )
            or not invitation_id
        ):
            raise ValueError(
                "Cat MEOW invitation requires id."
            )

        for index, current in enumerate(
            self.records()
        ):
            if current.id == invitation_id:
                self._records[
                    index
                ] = invitation

                return invitation

        self._records.append(
            invitation
        )

        return invitation

    def record(
        self,
        invitation_id,
    ):
        invitation_id = str(
            invitation_id
        )

        for invitation in self.records():
            if (
                invitation.id
                == invitation_id
            ):
                return invitation

        return None

    def records(
        self,
    ):
        for invitation in self._records:
            if not isinstance(
                invitation,
                CatMeowInvitation,
            ):
                raise TypeError(
                    "Cat MEOW invitation registry "
                    "contains invalid runtime state."
                )

        return tuple(
            self._records
        )
