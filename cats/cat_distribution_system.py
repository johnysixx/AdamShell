class CatDistributionSystem:

    def __init__(
        self,
        meeting_entities,
        idea_entities,
        recipient_registry=None
    ):

        self.meeting_entities = (
            meeting_entities
        )

        self.idea_entities = (
            idea_entities
        )

        self.recipient_registry = (
            recipient_registry
        )

    def handle_after_milk(
        self,
        cat
    ):
        if cat.get("recipient") is not None:
            return {
                "name": "cat_distribution_skipped",
                "cat": cat.get("name"),
                "reason": "cat_already_has_recipient",
                "distributed": False
            }

        recipient = (
            self._find_waiting_recipient()
        )

        if recipient is not None:
            recipient_id = (
                recipient.get("id")
                or recipient.get("world_key")
                or recipient.get("name")
            )

            cat["recipient"] = (
                recipient_id
            )

            cat["distribution"] = {
                "recipient": recipient_id,
                "status": "assigned",
                "suggested_layer": None
            }

            recipient["needs_cat"] = False

            return {
                "name": "cat_assigned_to_recipient",
                "cat": cat.get("name"),
                "recipient": recipient_id,
                "status": "assigned",
                "distributed": True
            }

        suggested_layer = "idea_universe"

        cat["distribution"] = {
            "recipient": None,
            "status": "unassigned",
            "suggested_layer": (
                suggested_layer
            )
        }

        return {
            "name": "cat_distribution_suggested",
            "cat": cat.get("name"),
            "status": "unassigned",
            "suggested_layer": (
                suggested_layer
            ),
            "distributed": False
        }

    def _find_waiting_recipient(
        self
    ):
        if self.recipient_registry is None:
            return None

        waiting = (
            self.recipient_registry
            .waiting_for_cat()
        )

        if not waiting:
            return None

        return waiting[0]



