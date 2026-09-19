from cats.cat import Cat

from cats.cat_distribution_state import CatDistributionState

class CatDistributionSystem:

    def __init__(self, meeting_entities, idea_entities, recipient_registry=None):
        self.meeting_entities = meeting_entities
        self.idea_entities = idea_entities
        self.recipient_registry = recipient_registry

    def handle_after_milk(self, cat):
        distribution = cat.distribution

        if not isinstance(
            distribution,
            CatDistributionState,
        ):
            raise TypeError(
                'Cat distribution state '
                'must be CatDistributionState.'
            )

        if not isinstance(cat, Cat):
            raise TypeError('CatDistributionSystem requires Cat.')
        if cat.recipient is not None:
            return {'name': 'cat_distribution_skipped', 'cat': cat.name, 'reason': 'cat_already_has_recipient', 'distributed': False}
        recipient = self._find_waiting_recipient()
        if recipient is not None:
            recipient_id = getattr(recipient, 'id', None) or getattr(recipient, 'world_key', None) or getattr(recipient, 'name', None)
            cat.recipient = recipient_id
            distribution.recipient = recipient_id
            distribution.status = 'assigned'
            distribution.suggested_layer = None
            recipient.needs_cat = False
            return {'name': 'cat_assigned_to_recipient', 'cat': cat.name, 'recipient': recipient_id, 'status': 'assigned', 'distributed': True}
        suggested_layer = 'idea_universe'
        distribution.recipient = None
        distribution.status = 'unassigned'
        distribution.suggested_layer = suggested_layer
        return {'name': 'cat_distribution_suggested', 'cat': cat.name, 'status': 'unassigned', 'suggested_layer': suggested_layer, 'distributed': False}

    def _find_waiting_recipient(self):
        if self.recipient_registry is None:
            return None
        waiting = self.recipient_registry.waiting_for_cat()
        if not waiting:
            return None
        return waiting[0]
