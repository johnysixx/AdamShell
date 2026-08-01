class CronenbergQuantumLinks:

    def __init__(self, owner_id):
        self.owner_id = owner_id
        self.links = []
        self.history = []

    def add_link(
        self,
        target_id,
        link_type,
        strength=1.0,
        created_tick=None,
        metadata=None
    ):
        target_id = str(target_id)
        link_type = str(link_type)
        strength = float(strength)

        existing = next(
            (
                link
                for link in self.links
                if link["target_id"] == target_id
                and link["link_type"] == link_type
            ),
            None
        )

        if existing is not None:
            existing["strength"] = max(
                existing["strength"],
                strength
            )

            return dict(existing)

        link = {
            "target_id": target_id,
            "link_type": link_type,
            "strength": strength,
            "created_tick": created_tick,
            "metadata": dict(metadata or {})
        }

        self.links.append(link)

        self.history.append({
            "event": "link_created",
            "link": dict(link)
        })

        return dict(link)

    def has_link_to(self, target_id):
        return any(
            link["target_id"] == target_id
            for link in self.links
        )

    def links_to(self, target_id):
        return [
            dict(link)
            for link in self.links
            if link["target_id"] == target_id
        ]

    def snapshot(self):
        return [
            {
                "target_id": link["target_id"],
                "link_type": link["link_type"],
                "strength": link["strength"],
                "created_tick": link["created_tick"],
                "metadata": dict(
                    link["metadata"]
                )
            }
            for link in self.links
        ]

    @property
    def public_state(self):
        return {
            "owner_id": self.owner_id,
            "link_count": len(self.links),
            "links": self.snapshot(),
            "history": list(self.history)
        }
