class WorldObject:

    def __init__(
        self,
        object_id,
        name,
        object_type,
        creator=None,
        created_at_tick=0,
        active=True,
        destroyable=True
    ):
        self.id = object_id
        self.name = name
        self.type = object_type
        self.creator = creator
        self.created_at_tick = created_at_tick
        self.active = active
        self.destroyable = destroyable

    @property
    def identity_state(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "creator": self.creator,
            "created_at_tick": self.created_at_tick,
            "active": self.active,
            "destroyable": self.destroyable
        }
