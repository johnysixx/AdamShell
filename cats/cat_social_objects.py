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

    @classmethod
    def create(cls):
        return cls(
            familiarity=0.0,
            trust=0.5,
            affiliation=0.0,
            tension=0.0,
            shared_scent=0.0,
            meet_count=0,
            last_interaction=None,
        )

    def __getitem__(self, name):
        try:
            return getattr(self, name)
        except AttributeError as error:
            raise KeyError(name) from error

    def __setitem__(self, name, value):
        setattr(
            self,
            name,
            value,
        )

    def get(self, name, default=None):
        return getattr(
            self,
            name,
            default,
        )

    def setdefault(self, name, default=None):
        if not hasattr(self, name):
            setattr(
                self,
                name,
                default,
            )

        return getattr(
            self,
            name,
        )

    def update(self, values):
        for name, value in values.items():
            setattr(
                self,
                name,
                value,
            )


class CatGroupKnowledgeRecord(ComponentObject):
    pass
