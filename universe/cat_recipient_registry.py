class CatRecipientRegistry:

    def __init__(self):
        self.recipients = []

    def register(self, entity):
        if isinstance(
            entity,
            dict
        ):
            raise TypeError(
                "Cat recipient must be an object entity."
            )

        if not hasattr(
            entity,
            "type"
        ):
            raise TypeError(
                "Cat recipient requires entity identity."
            )
        if entity not in self.recipients:
            self.recipients.append(entity)
        return entity

    def find(self, entity_id):
        for entity in self.recipients:
            if getattr(entity, 'id', None) == entity_id or getattr(entity, 'name', None) == entity_id or getattr(entity, 'world_key', None) == entity_id:
                return entity
        return None

    def waiting_for_cat(self):
        return [entity for entity in self.recipients if getattr(entity, 'needs_cat', False)]

    @property
    def public_state(self):
        return {'type': 'cat_recipient_registry', 'recipient_count': len(self.recipients), 'recipients': [dict(entity) for entity in self.recipients]}
