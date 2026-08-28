class ExistenceResolver:

    @staticmethod
    def _get(entity, key, default=None):
        return getattr(entity, key, default)

    @staticmethod
    def get_strongest_world(entity):
        existence_by_world = ExistenceResolver._get(entity, 'existence_by_world', {})
        native_world = ExistenceResolver._get(entity, 'native_world')
        if not existence_by_world:
            return native_world
        highest_existence = max(existence_by_world.values())
        strongest_worlds = [world for world, existence in existence_by_world.items() if existence == highest_existence]
        if native_world in strongest_worlds:
            return native_world
        return strongest_worlds[0]

    @staticmethod
    def remove_from_strongest_world(entity):
        strongest_world = ExistenceResolver.get_strongest_world(entity)
        existence_by_world = ExistenceResolver._get(entity, 'existence_by_world', {})
        if strongest_world is None:
            return {'world': None, 'removed_existence_pct': 0.0}
        removed_existence_pct = float(existence_by_world.get(strongest_world, 0.0))
        if strongest_world in existence_by_world:
            existence_by_world[strongest_world] = 0.0
        return {'world': strongest_world, 'removed_existence_pct': removed_existence_pct}

    @staticmethod
    def exists_anywhere(entity):
        existence_by_world = ExistenceResolver._get(entity, 'existence_by_world', {})
        return any((float(existence) > 0.0 for existence in existence_by_world.values()))
