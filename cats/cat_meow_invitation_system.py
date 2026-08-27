from copy import deepcopy
from uuid import uuid4

from cats.cat import Cat
from cats.cat_human_bond_system import (
    CatHumanBondSystem
)


class CatMeowInvitationSystem:

    def __init__(
        self,
        cats_layer=None
    ):
        self.cats_layer = cats_layer

        self.bonds = CatHumanBondSystem(
            cats_layer
        )

        self.invitations = {}

    def offer(
        self,
        cat,
        human
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "MEOW can only be offered by Cat."
            )

        evaluation = self.bonds.evaluate(
            cat,
            human
        )

        if not evaluation[
            "right_human"
        ]:
            return {
                "name": "cat_MEOW_not_offered",
                "cat": cat.name,
                "human": self._name(
                    human
                ),
                "reason": "not_recognized_as_right_human",
                "offered": False
            }

        invitation_id = (
            "MEOW_"
            + uuid4().hex[:8]
        )

        invitation = {
            "id": invitation_id,
            "name": "cat_MEOW_invitation",
            "cat": cat.name,
            "human": self._name(
                human
            ),
            "sound": "MEOW",
            "meaning": "follow_me",
            "offered": True,
            "understood": None,
            "accepted": False,
            "used": False
        }

        self.invitations[
            invitation_id
        ] = invitation

        cat.meow_invitations[
            "offered"
        ] += 1

        cat.meow_invitations[
            "history"
        ].append(
            deepcopy(
                invitation
            )
        )

        return deepcopy(
            invitation
        )

    def interpret(
        self,
        invitation_id,
        human,
        understood
    ):
        invitation = self.invitations.get(
            invitation_id
        )

        if invitation is None:
            return {
                "name": "cat_MEOW_interpretation_failed",
                "reason": "unknown_invitation",
                "understood": False
            }

        if (
            invitation[
                "human"
            ]
            != self._name(
                human
            )
        ):
            return {
                "name": "cat_MEOW_interpretation_failed",
                "reason": "wrong_human",
                "understood": False
            }

        invitation[
            "understood"
        ] = bool(
            understood
        )

        invitation[
            "accepted"
        ] = bool(
            understood
        )

        return {
            "name": (
                "human_understood_MEOW"
                if understood
                else "human_heard_only_meow"
            ),
            "invitation_id": invitation_id,
            "human": invitation[
                "human"
            ],
            "understood": bool(
                understood
            ),
            "meaning": (
                "follow_me"
                if understood
                else None
            )
        }

    def get(
        self,
        invitation_id
    ):
        invitation = self.invitations.get(
            invitation_id
        )

        if invitation is None:
            return None

        return deepcopy(
            invitation
        )

    def mark_used(
        self,
        invitation_id
    ):
        invitation = self.invitations[
            invitation_id
        ]

        invitation[
            "used"
        ] = True

    def _name(
        self,
        entity
    ):
        if isinstance(
            entity,
            dict
        ):
            return entity.get(
                "name"
            )

        return getattr(
            entity,
            "name",
            None
        )
