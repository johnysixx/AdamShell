from core.entity.component_object import ComponentObject

class CatGroupMyth(ComponentObject):
    pass

class CatGroupNorm(ComponentObject):
    pass

class CatGroupTaboo(ComponentObject):
    pass

class CatGroupRitual(ComponentObject):
    pass

class CatGroupInstitution(ComponentObject):
    pass

class CatGroupInnovation(ComponentObject):
    pass

class CatInstitutionConflict(ComponentObject):
    pass

class CatViolation(ComponentObject):

    def __init__(self, **values):
        if 'severity' not in values:
            if 'importance' not in values:
                raise ValueError('CatViolation requires severity or importance.')
            values['severity'] = values['importance']
        super().__init__(**values)

class CatNormViolation(CatViolation):
    pass

class CatTabooViolation(CatViolation):
    pass
