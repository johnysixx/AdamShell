from core.entity.domain_object import DomainObject

from cats.maternal_care_phase import (
    MaternalCarePhase,
)

from cats.cat_group_role_state import (
    CatGroupRoleAssignedEvent,
    CatGroupRoleReleasedEvent,
    CatGroupRoleSpecializedEvent,
)

class CatFamily(DomainObject):
    pass

class MaternalCare(DomainObject):
    pass

class MaternalCareReceived(DomainObject):
    last_phase: MaternalCarePhase | None

    def __setattr__(self, key, value):
        if (
            key == "last_phase"
            and value is not None
            and not isinstance(
                value,
                MaternalCarePhase,
            )
        ):
            raise TypeError(
                "Maternal care received phase "
                "must use MaternalCarePhase."
            )

        super().__setattr__(
            key,
            value,
        )

class SiblingPlay(DomainObject):
    pass

class SiblingRivalry(DomainObject):
    pass

class ParentalTeaching(DomainObject):
    pass

class FamilyBonding(DomainObject):
    pass

class CatGroupMembership(DomainObject):
    pass

class CatCulture(DomainObject):
    pass

class CatGroupRoles(DomainObject):
    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            (
                CatGroupRoleAssignedEvent,
                CatGroupRoleReleasedEvent,
                CatGroupRoleSpecializedEvent,
            ),
        ):
            raise TypeError(
                "Cat group role history requires "
                "a cat group role event object."
            )

        self.history.append(
            event
        )

        return event

class CatMeowInvitations(DomainObject):
    pass

class CatNorms(DomainObject):
    pass

class CatNeeds(DomainObject):
    pass

class CatMindState(DomainObject):
    pass


class CatHumanBond(DomainObject):
    pass


class CatTerritories(DomainObject):
    pass


class CatSocialMemories(DomainObject):
    pass


class CatBonds(DomainObject):
    pass


class CatHumanBonds(DomainObject):
    pass



class CatEmergencyNursing(DomainObject):
    DEFAULT_CAPABILITY_PERCENT = 12

    @classmethod
    def create_state(cls, name, sex):
        import hashlib

        capable = False

        if sex == "female":
            digest = hashlib.sha256(
                f"{name}|emergency_lactation".encode("utf-8")
            ).digest()

            roll = (
                int.from_bytes(
                    digest[:4],
                    "big"
                )
                % 10000
            )

            capable = (
                roll
                < cls.DEFAULT_CAPABILITY_PERCENT * 100
            )

        return cls(
            can_induce_lactation=capable,
            induced_lactation=False,
            active=False,
            foster_kittens=[],
            rescued_litters=[],
            garfield_consultations=0,
            milk_feedings=0,
            last_advice=None,
        )
