class CatRecipientRegistry:

    def __init__(self):
        self.recipients = []

    def register(
        self,
        entity
    ):
        if not isinstance(
            entity,
            dict
        ):
            raise TypeError(
                "Cat recipient must be a dict."
            )

        if entity not in self.recipients:
            self.recipients.append(
                entity
            )

        return entity

    def find(
        self,
        entity_id
    ):
        for entity in self.recipients:
            if (
                entity.get("id")
                == entity_id
                or entity.get("name")
                == entity_id
                or entity.get("world_key")
                == entity_id
            ):
                return entity

        return None

    def waiting_for_cat(
        self
    ):
        return [
            entity
            for entity in self.recipients
            if entity.get(
                "needs_cat",
                False
            )
        ]

    @property
    def public_state(self):
        return {
            "type": "cat_recipient_registry",
            "recipient_count": len(
                self.recipients
            ),
            "recipients": [
                dict(entity)
                for entity in self.recipients
            ]
        }
