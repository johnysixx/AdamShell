class ExistenceResolver:

    @staticmethod
    def get_strongest_world(entity):
        existence_by_world = entity.get(
            "existence_by_world",
            {}
        )

        native_world = entity.get("native_world")

        if not existence_by_world:
            return native_world

        highest_existence = max(
            existence_by_world.values()
        )

        strongest_worlds = [
            world
            for world, existence in existence_by_world.items()
            if existence == highest_existence
        ]

        if native_world in strongest_worlds:
            return native_world

        return strongest_worlds[0]
