from core.entity.domain_object import DomainObject

class CatGroupMyth(DomainObject):
    pass

class CatGroupNorm(DomainObject):
    pass

class CatGroupTaboo(DomainObject):
    pass

class CatGroupRitual(DomainObject):
    pass

class CatGroupInstitution(DomainObject):
    pass

class CatGroupInnovation(DomainObject):
    pass

class CatInstitutionConflict(DomainObject):
    pass

class CatViolation(DomainObject):

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
