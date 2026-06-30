from core.entity.entity import Entity


class EntityFactory:

    def create(self, name, universe=None):

        entity = Entity(name)
        entity.word = universe
        entity.birth_allowed = False

        return entity