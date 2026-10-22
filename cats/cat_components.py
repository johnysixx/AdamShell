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

class CatCulturalTraditionEvaluations(
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
        record,
    ):
        from cats.cat_cultural_tradition_evaluation_state import (
            CatCulturalTraditionEvaluationState,
        )

        if not isinstance(
            record,
            CatCulturalTraditionEvaluationState,
        ):
            raise TypeError(
                "Cultural tradition registry requires "
                "CatCulturalTraditionEvaluationState."
            )

        tradition = getattr(
            record,
            "tradition",
            None,
        )

        if (
            not isinstance(
                tradition,
                str,
            )
            or not tradition
        ):
            raise ValueError(
                "Stored cultural tradition evaluation "
                "requires tradition."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.tradition
                == tradition
            ):
                self._records[
                    index
                ] = record

                return record

        self._records.append(
            record
        )

        return record

    def record(
        self,
        tradition,
    ):
        tradition = str(
            tradition
        )

        for record in self.records():
            if (
                record.tradition
                == tradition
            ):
                return record

        return None

    def has(
        self,
        tradition,
    ):
        return (
            self.record(
                tradition
            )
            is not None
        )

    def release(
        self,
        tradition,
    ):
        tradition = str(
            tradition
        )

        for index, record in enumerate(
            self.records()
        ):
            if (
                record.tradition
                == tradition
            ):
                del self._records[
                    index
                ]

                return record

        return None

    def records(
        self,
    ):
        from cats.cat_cultural_tradition_evaluation_state import (
            CatCulturalTraditionEvaluationState,
        )

        for record in self._records:
            if not isinstance(
                record,
                CatCulturalTraditionEvaluationState,
            ):
                raise TypeError(
                    "Cultural tradition registry contains "
                    "invalid runtime state."
                )

        return tuple(
            self._records
        )


class CatCulturalPreferences(
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
        record,
    ):
        from cats.cat_cultural_preference_state import (
            CatCulturalPreferenceState,
        )

        if not isinstance(
            record,
            CatCulturalPreferenceState,
        ):
            raise TypeError(
                "Cultural preference registry requires "
                "CatCulturalPreferenceState."
            )

        name = getattr(
            record,
            "name",
            None,
        )

        if (
            not isinstance(
                name,
                str,
            )
            or not name
        ):
            raise ValueError(
                "Stored cultural preference requires name."
            )

        for index, current in enumerate(
            self.records()
        ):
            if current.name == name:
                self._records[
                    index
                ] = record

                return record

        self._records.append(
            record
        )

        return record

    def record(
        self,
        name,
    ):
        name = str(
            name
        )

        for record in self.records():
            if record.name == name:
                return record

        return None

    def has(
        self,
        name,
    ):
        return (
            self.record(
                name
            )
            is not None
        )

    def records(
        self,
    ):
        from cats.cat_cultural_preference_state import (
            CatCulturalPreferenceState,
        )

        for record in self._records:
            if not isinstance(
                record,
                CatCulturalPreferenceState,
            ):
                raise TypeError(
                    "Cultural preference registry contains "
                    "invalid runtime state."
                )

        return tuple(
            self._records
        )


class CatMemeticSelections(
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
        from cats.cat_memetic_selection_state import (
            CatMemeticSelectionState,
        )

        if not isinstance(
            state,
            CatMemeticSelectionState,
        ):
            raise TypeError(
                "Memetic selection registry requires "
                "CatMemeticSelectionState."
            )

        meme_id = getattr(
            state,
            "meme_id",
            None,
        )

        if (
            not isinstance(
                meme_id,
                str,
            )
            or not meme_id
        ):
            raise ValueError(
                "Stored memetic selection requires "
                "meme_id."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.meme_id
                == meme_id
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
        meme_id,
    ):
        meme_id = str(
            meme_id
        )

        for state in self.records():
            if (
                state.meme_id
                == meme_id
            ):
                return state

        return None

    def has(
        self,
        meme_id,
    ):
        return (
            self.record(
                meme_id
            )
            is not None
        )

    def records(
        self,
    ):
        from cats.cat_memetic_selection_state import (
            CatMemeticSelectionState,
        )

        for state in self._records:
            if not isinstance(
                state,
                CatMemeticSelectionState,
            ):
                raise TypeError(
                    "Memetic selection registry contains "
                    "invalid runtime state."
                )

        return tuple(
            self._records
        )


class CatCulture(DomainObject):

    def __init__(
        self,
        exposures=0,
        **values
    ):
        for reserved_name in (
            "adopted_traditions",
            "rejected_traditions",
            "preferences",
            "myths",
            "innovations",
        ):
            if reserved_name in values:
                raise TypeError(
                    "CatCulture registry state cannot "
                    "be supplied as mapping data."
                )

        self.adopted_traditions = (
            CatCulturalTraditionEvaluations()
        )

        self.rejected_traditions = (
            CatCulturalTraditionEvaluations()
        )

        self.preferences = (
            CatCulturalPreferences()
        )

        self.myths = (
            CatMemeticSelections()
        )

        self.innovations = (
            CatMemeticSelections()
        )

        self.exposures = int(
            exposures
        )

        super().__init__(
            **values
        )

class CatGroupRoles(DomainObject):

    def __init__(
        self,
        history=None,
        role_events=0,
    ):
        self._active = []
        self.history = []
        self.role_events = int(
            role_events
        )

        for event in list(
            history or []
        ):
            self.record_event(
                event
            )

    @property
    def is_empty(
        self,
    ):
        return not self._active

    @property
    def count(
        self,
    ):
        return len(
            self._active
        )

    def store(
        self,
        state,
    ):
        from cats.cat_group_role_state import (
            CatGroupRoleState,
        )

        if not isinstance(
            state,
            CatGroupRoleState,
        ):
            raise TypeError(
                "Cat group role registry requires "
                "CatGroupRoleState."
            )

        role = getattr(
            state,
            "role",
            None,
        )

        if (
            not isinstance(
                role,
                str,
            )
            or not role
        ):
            raise ValueError(
                "Stored cat group role requires role."
            )

        for index, current in enumerate(
            self.records()
        ):
            if current.role == role:
                self._active[
                    index
                ] = state

                return state

        self._active.append(
            state
        )

        return state

    def record(
        self,
        role,
    ):
        role = str(
            role
        )

        for state in self.records():
            if state.role == role:
                return state

        return None

    def has(
        self,
        role,
    ):
        return (
            self.record(
                role
            )
            is not None
        )

    def release(
        self,
        role,
    ):
        role = str(
            role
        )

        for index, state in enumerate(
            self.records()
        ):
            if state.role == role:
                del self._active[
                    index
                ]

                return state

        return None

    def roles(
        self,
    ):
        return tuple(
            state.role
            for state
            in self.records()
        )

    def records(
        self,
    ):
        from cats.cat_group_role_state import (
            CatGroupRoleState,
        )

        for state in self._active:
            if not isinstance(
                state,
                CatGroupRoleState,
            ):
                raise TypeError(
                    "Cat group role registry contains "
                    "invalid runtime state."
                )

            role = getattr(
                state,
                "role",
                None,
            )

            if (
                not isinstance(
                    role,
                    str,
                )
                or not role
            ):
                raise ValueError(
                    "Cat group role registry contains "
                    "state without role."
                )

        return tuple(
            self._active
        )

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

    def __init__(
        self,
        owner,
    ):
        owner = str(
            owner
        )

        if not owner:
            raise ValueError(
                "Cat territory registry requires owner."
            )

        self.owner = owner
        self._claims = []

    @property
    def is_empty(
        self,
    ):
        return not self._claims

    @property
    def count(
        self,
    ):
        return len(
            self._claims
        )

    def store(
        self,
        claim,
    ):
        from cats.cat_social_objects import (
            CatTerritoryClaim,
        )

        if not isinstance(
            claim,
            CatTerritoryClaim,
        ):
            raise TypeError(
                "Cat territory registry requires "
                "CatTerritoryClaim."
            )

        if claim.owner != self.owner:
            raise ValueError(
                "Cat territory claim owner does not "
                "match registry owner."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.layer
                == claim.layer
                and current.location
                == claim.location
            ):
                self._claims[
                    index
                ] = claim

                return claim

        self._claims.append(
            claim
        )

        return claim

    def record(
        self,
        layer,
        location=None,
    ):
        layer = str(
            layer
        )

        for claim in self.records():
            if (
                claim.layer
                == layer
                and claim.location
                == location
            ):
                return claim

        return None

    def claim_at(
        self,
        layer,
        location,
    ):
        claim = self.record(
            layer,
            location,
        )

        if claim is not None:
            return claim

        if location is None:
            return None

        return self.record(
            layer,
            None,
        )

    def has(
        self,
        layer,
        location=None,
    ):
        return (
            self.record(
                layer,
                location,
            )
            is not None
        )

    def records(
        self,
    ):
        from cats.cat_social_objects import (
            CatTerritoryClaim,
        )

        for claim in self._claims:
            if not isinstance(
                claim,
                CatTerritoryClaim,
            ):
                raise TypeError(
                    "Cat territory registry contains "
                    "invalid runtime state."
                )

            if claim.owner != self.owner:
                raise ValueError(
                    "Cat territory registry contains "
                    "claim for another owner."
                )

        return tuple(
            self._claims
        )


class CatRelationships(DomainObject):

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
        relationship,
    ):
        from cats.cat_social_objects import (
            CatRelationship,
        )

        if not isinstance(
            relationship,
            CatRelationship,
        ):
            raise TypeError(
                "Cat relationship registry requires "
                "CatRelationship."
            )

        other_cat = getattr(
            relationship,
            "other_cat",
            None,
        )

        if (
            not isinstance(
                other_cat,
                str,
            )
            or not other_cat
        ):
            raise ValueError(
                "Stored cat relationship requires "
                "other_cat."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.other_cat
                == other_cat
            ):
                self._records[
                    index
                ] = relationship

                return relationship

        self._records.append(
            relationship
        )

        return relationship

    def record(
        self,
        other_cat,
    ):
        other_cat = str(
            other_cat
        )

        for relationship in self.records():
            if (
                relationship.other_cat
                == other_cat
            ):
                return relationship

        return None

    def profile(
        self,
        other_cat,
    ):
        from cats.cat_social_objects import (
            CatRelationship,
        )

        relationship = self.record(
            other_cat
        )

        if relationship is not None:
            return relationship

        return CatRelationship.create(
            other_cat=other_cat
        )

    def ensure(
        self,
        other_cat,
    ):
        from cats.cat_social_objects import (
            CatRelationship,
        )

        relationship = self.record(
            other_cat
        )

        if relationship is not None:
            return relationship

        relationship = (
            CatRelationship.create(
                other_cat=other_cat
            )
        )

        return self.store(
            relationship
        )

    def has(
        self,
        other_cat,
    ):
        return (
            self.record(
                other_cat
            )
            is not None
        )

    def records(
        self,
    ):
        from cats.cat_social_objects import (
            CatRelationship,
        )

        for relationship in self._records:
            if not isinstance(
                relationship,
                CatRelationship,
            ):
                raise TypeError(
                    "Cat relationship registry contains "
                    "invalid runtime state."
                )

            other_cat = getattr(
                relationship,
                "other_cat",
                None,
            )

            if (
                not isinstance(
                    other_cat,
                    str,
                )
                or not other_cat
            ):
                raise ValueError(
                    "Cat relationship registry contains "
                    "relationship without other_cat."
                )

        return tuple(
            self._records
        )


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
