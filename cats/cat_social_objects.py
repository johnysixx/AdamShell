from core.entity.component_object import ComponentObject


class CatMeowInvitation(ComponentObject):
    pass


class CatGuestIncident(ComponentObject):
    pass



class GarfieldTraining(ComponentObject):
    pass


class CatLegend(ComponentObject):
    pass



class CatTerritoryClaim(ComponentObject):
    pass


class CatSocialMemory(ComponentObject):
    pass


class CatBond(ComponentObject):
    pass


class CatRelationship(ComponentObject):

    def __init__(
        self,
        familiarity=0.0,
        trust=0.5,
        affiliation=0.0,
        tension=0.0,
        shared_scent=0.0,
        meet_count=0,
        last_interaction=None,
        trust_history=None,
    ):
        super().__init__(
            familiarity=familiarity,
            trust=trust,
            affiliation=affiliation,
            tension=tension,
            shared_scent=shared_scent,
            meet_count=meet_count,
            last_interaction=last_interaction,
            trust_history=(
                []
                if trust_history is None
                else trust_history
            ),
        )

    @classmethod
    def create(cls):
        return cls()


class CatGroupKnowledgeRecord(ComponentObject):
    pass
