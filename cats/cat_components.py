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
        memory,
    ):
        from cats.cat_social_objects import (
            CatSocialMemory,
        )

        if not isinstance(
            memory,
            CatSocialMemory,
        ):
            raise TypeError(
                "Cat social memory registry requires "
                "CatSocialMemory."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.other_cat
                == memory.other_cat
            ):
                self._records[
                    index
                ] = memory

                return memory

        self._records.append(
            memory
        )

        return memory

    def record(
        self,
        other_cat,
    ):
        other_cat = str(
            other_cat
        )

        for memory in self.records():
            if memory.other_cat == other_cat:
                return memory

        return None

    def records(
        self,
    ):
        from cats.cat_social_objects import (
            CatSocialMemory,
        )

        for memory in self._records:
            if not isinstance(
                memory,
                CatSocialMemory,
            ):
                raise TypeError(
                    "Cat social memory registry contains "
                    "invalid runtime state."
                )

        return tuple(
            self._records
        )


class CatBonds(DomainObject):

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
        bond,
    ):
        from cats.cat_social_objects import (
            CatBond,
        )

        if not isinstance(
            bond,
            CatBond,
        ):
            raise TypeError(
                "Cat bond registry requires "
                "CatBond."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.other_cat
                == bond.other_cat
            ):
                self._records[
                    index
                ] = bond

                return bond

        self._records.append(
            bond
        )

        return bond

    def record(
        self,
        other_cat,
    ):
        other_cat = str(
            other_cat
        )

        for bond in self.records():
            if bond.other_cat == other_cat:
                return bond

        return None

    def records(
        self,
    ):
        from cats.cat_social_objects import (
            CatBond,
        )

        for bond in self._records:
            if not isinstance(
                bond,
                CatBond,
            ):
                raise TypeError(
                    "Cat bond registry contains "
                    "invalid runtime state."
                )

        return tuple(
            self._records
        )


class CatHumanBonds(DomainObject):

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
        bond,
    ):
        if not isinstance(
            bond,
            CatHumanBond,
        ):
            raise TypeError(
                "Cat human bond registry requires "
                "CatHumanBond."
            )

        human = getattr(
            bond,
            "human",
            None,
        )

        if (
            not isinstance(
                human,
                str,
            )
            or not human
        ):
            raise ValueError(
                "Cat human bond requires human."
            )

        for index, current in enumerate(
            self.records()
        ):
            if current.human == human:
                self._records[
                    index
                ] = bond

                return bond

        self._records.append(
            bond
        )

        return bond

    def record(
        self,
        human_name,
    ):
        human_name = str(
            human_name
        )

        for bond in self.records():
            if bond.human == human_name:
                return bond

        return None

    def records(
        self,
    ):
        for bond in self._records:
            if not isinstance(
                bond,
                CatHumanBond,
            ):
                raise TypeError(
                    "Cat human bond registry contains "
                    "invalid runtime state."
                )

        return tuple(
            self._records
        )



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
