from dataclasses import dataclass, field

from cats.cat_meow_bar_access_state import (
    CatMeowBarAccessState,
)

@dataclass(slots=True, frozen=True)
class CatBarGuidanceAccessSnapshot:

    source: str
    inviting_cat: str
    invitation_id: str
    permanent: bool = False

    @classmethod
    def from_state(
        cls,
        state,
    ):
        if not isinstance(
            state,
            CatMeowBarAccessState,
        ):
            raise TypeError(
                "Bar guidance access requires "
                "CatMeowBarAccessState."
            )

        return cls(
            source=state.source,
            inviting_cat=state.inviting_cat,
            invitation_id=state.invitation_id,
            permanent=state.permanent,
        )

    def to_state(self):
        return CatMeowBarAccessState(
            source=self.source,
            inviting_cat=self.inviting_cat,
            invitation_id=self.invitation_id,
            permanent=self.permanent,
        )


@dataclass(slots=True, frozen=True)
class CatBarGuidanceAdmissionSnapshot:

    human: str
    inviting_cat: str
    invitation_id: str
    cat_present: bool
    entered_together: bool
    permanent_access: bool
    entered: bool

    name: str = field(
        default="cat_invited_human_entered",
        init=False,
    )

    @classmethod
    def from_boundary(
        cls,
        payload,
    ):
        if not isinstance(
            payload,
            dict,
        ):
            raise TypeError(
                "Bar guidance admission boundary "
                "must be dict."
            )

        return cls(
            human=payload["human"],
            inviting_cat=payload[
                "inviting_cat"
            ],
            invitation_id=payload[
                "invitation_id"
            ],
            cat_present=payload[
                "cat_present"
            ],
            entered_together=payload[
                "entered_together"
            ],
            permanent_access=payload[
                "permanent_access"
            ],
            entered=payload["entered"],
        )

    def to_dict(self):
        return {
            "name": self.name,
            "human": self.human,
            "inviting_cat":
                self.inviting_cat,
            "invitation_id":
                self.invitation_id,
            "cat_present":
                self.cat_present,
            "entered_together":
                self.entered_together,
            "permanent_access":
                self.permanent_access,
            "entered": self.entered,
        }


@dataclass(slots=True, frozen=True)
class CatGuidedHumanToBarEvent:

    cat: str
    human: str
    invitation_id: str
    access: CatBarGuidanceAccessSnapshot
    admission: CatBarGuidanceAdmissionSnapshot

    name: str = field(
        default="cat_guided_human_to_bar",
        init=False,
    )

    guided: bool = field(
        default=True,
        init=False,
    )

    permanent_access: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.access,
            CatBarGuidanceAccessSnapshot,
        ):
            raise TypeError(
                "Bar guidance event access "
                "requires "
                "CatBarGuidanceAccessSnapshot."
            )

        if not isinstance(
            self.admission,
            CatBarGuidanceAdmissionSnapshot,
        ):
            raise TypeError(
                "Bar guidance event admission "
                "requires "
                "CatBarGuidanceAdmissionSnapshot."
            )

    def to_dict(
        self,
        access_state=None,
    ):
        access = (
            self.access.to_state()
            if access_state is None
            else access_state
        )

        if not isinstance(
            access,
            CatMeowBarAccessState,
        ):
            raise TypeError(
                "Bar guidance boundary access "
                "requires "
                "CatMeowBarAccessState."
            )

        return {
            "name": self.name,
            "cat": self.cat,
            "human": self.human,
            "invitation_id":
                self.invitation_id,
            "access": access,
            "admission_result":
                self.admission.to_dict(),
            "guided": self.guided,
            "permanent_access":
                self.permanent_access,
        }


class CatBarGuidanceSystem:

    def __init__(self, invitation_system, meeting_place):
        self.invitation_system = invitation_system
        self.meeting_place = meeting_place
        self.history = []

    def guide(self, cat, human, invitation_id):
        invitation = self.invitation_system.get(invitation_id)
        if invitation is None:
            return self._failed(cat, human, 'unknown_invitation')
        if invitation.cat != cat.name:
            return self._failed(cat, human, 'wrong_cat')
        if invitation.human != self._name(human):
            return self._failed(cat, human, 'wrong_human')
        if not invitation.understood:
            return self._failed(cat, human, 'MEOW_not_understood')
        if invitation.used:
            return self._failed(cat, human, 'invitation_already_used')
        temporary_access = CatMeowBarAccessState(
            source='cat_MEOW_invitation',
            inviting_cat=cat.name,
            invitation_id=invitation_id,
            permanent=False,
        )
        self._set(human, 'meow_bar_invitation', temporary_access)
        self._set(human, 'guided_by_cat', cat.name)
        add_entity = getattr(self.meeting_place, 'add_entity', None)
        if not callable(add_entity):
            return self._failed(cat, human, 'meeting_place_cannot_admit')
        escorted_entry = getattr(self.meeting_place, 'add_cat_invited_human', None)
        if callable(escorted_entry):
            admission_result = escorted_entry(human, cat, self.invitation_system)
            if not admission_result.get('entered', False):
                return self._failed(cat, human, admission_result.get('reason', 'escorted_entry_denied'))
        else:
            return self._failed(cat, human, 'meeting_place_has_no_escorted_entry')
        self.invitation_system.mark_used(invitation_id)
        cat.meow_invitations.understood += 1
        cat.meow_invitations.guided_to_bar += 1
        event = CatGuidedHumanToBarEvent(
            cat=cat.name,
            human=self._name(human),
            invitation_id=invitation_id,
            access=(
                CatBarGuidanceAccessSnapshot
                .from_state(
                    temporary_access
                )
            ),
            admission=(
                CatBarGuidanceAdmissionSnapshot
                .from_boundary(
                    admission_result
                )
            ),
        )

        self.record_event(
            event
        )

        cat.meow_invitations.history.append(
            event.to_dict()
        )

        return event.to_dict(
            access_state=temporary_access
        )

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            CatGuidedHumanToBarEvent,
        ):
            raise TypeError(
                "Cat bar guidance history "
                "requires a "
                "CatGuidedHumanToBarEvent object."
            )

        self.history.append(
            event
        )

        return event

    def _failed(self, cat, human, reason):
        return {'name': 'cat_bar_guidance_failed', 'cat': getattr(cat, 'name', None), 'human': self._name(human), 'reason': reason, 'guided': False}

    def _name(self, entity):
        return getattr(entity, 'name', None)

    def _set(self, entity, key, value):
        setattr(entity, key, value)
