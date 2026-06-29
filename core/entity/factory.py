from core.entity.entity import Entity


class EntityFactory:

    def create(self, name):

        return Entity(name)