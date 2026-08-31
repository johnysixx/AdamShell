from core.entity.component_object import ComponentObject

class CatFamily(ComponentObject):
    pass

class MaternalCare(ComponentObject):
    pass

class MaternalCareReceived(ComponentObject):
    pass

class SiblingPlay(ComponentObject):
    pass

class SiblingRivalry(ComponentObject):
    pass

class ParentalTeaching(ComponentObject):
    pass

class FamilyBonding(ComponentObject):
    pass

class CatGroupMembership(ComponentObject):
    pass

class CatCulture(ComponentObject):
    pass

class CatGroupRoles(ComponentObject):
    pass

class CatMeowInvitations(ComponentObject):
    pass

class CatNorms(ComponentObject):
    pass

class CatNeeds(ComponentObject):
    pass

class CatMindState(ComponentObject):
    pass



class CatEmergencyNursing(ComponentObject):
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
