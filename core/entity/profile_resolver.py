class EntityProfileResolver:

    @classmethod
    def find_profile(cls, world, technical_name):
        visited = set()

        exact_profile = cls._search(
            value=world,
            technical_name=technical_name,
            visited=visited,
            match_name=False
        )

        if exact_profile is not None:
            return exact_profile

        visited.clear()

        return cls._search(
            value=world,
            technical_name=technical_name,
            visited=visited,
            match_name=True
        )

    @classmethod
    def _search(
            cls,
            value,
            technical_name,
            visited,
            match_name
    ):
        value_id = id(value)

        if value_id in visited:
            return None

        if isinstance(value, (dict, list)):
            visited.add(value_id)

        if isinstance(value, dict):
            if cls._matches(
                    value,
                    technical_name,
                    match_name
            ):
                return value

            for nested_value in value.values():
                result = cls._search(
                    value=nested_value,
                    technical_name=technical_name,
                    visited=visited,
                    match_name=match_name
                )

                if result is not None:
                    return result

        if isinstance(value, list):
            for nested_value in value:
                result = cls._search(
                    value=nested_value,
                    technical_name=technical_name,
                    visited=visited,
                    match_name=match_name
                )

                if result is not None:
                    return result

        return None

    @staticmethod
    def _matches(
            profile,
            technical_name,
            match_name
    ):
        if profile.get("entity_id") == technical_name:
            return True

        if profile.get("world_key") == technical_name:
            return True

        if match_name:
            return profile.get("name") == technical_name

        return False
