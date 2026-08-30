from copy import deepcopy

class CatGroupMigrationSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def migrate(self, group_id, cats, layer, location, position=None, reason='group_migration'):
        group = self.group_system._group(group_id)
        if getattr(group, 'dissolved', False):
            return {'name': 'cat_group_migration_denied', 'group_id': group_id, 'reason': 'group_dissolved', 'migrated': False}
        members = self.group_system._member_objects(group, cats)
        if not members:
            return {'name': 'cat_group_migration_denied', 'group_id': group_id, 'reason': 'no_members', 'migrated': False}
        old_layer = getattr(group, 'current_layer', None)
        old_location = getattr(group, 'current_location', None)
        for member in members:
            member.current_layer = layer
            member.location = location
            if position is not None:
                member.position = dict(position)
            member.state = 'migrating_with_group'
        group.current_layer = layer
        group.current_location = location
        group.migration_count += 1
        event = {'name': 'cat_group_migrated', 'group_id': group_id, 'from_layer': old_layer, 'from_location': old_location, 'to_layer': layer, 'to_location': location, 'position': dict(position) if position is not None else None, 'reason': reason, 'members': [member.name for member in members], 'migrated': True}
        group.history.append(deepcopy(event))
        for member in members:
            member.social_interactions.append(deepcopy(event))
        return event
