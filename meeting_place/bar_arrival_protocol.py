class BarArrivalProtocol:

    def __init__(self, geometry):
        self.geometry = geometry

    def arrive(self, guest):
        if guest is None:
            return False
        entrance = self.geometry.find_cell(name='entrance_door')
        if entrance is None:
            return False
        destination = self.geometry.nearest_reachable_cell(entrance, kind='customer_floor')
        if destination is None:
            destination = self.geometry.expand_bar()
        if destination is None:
            return False
        path = self.geometry.shortest_walkable_path(entrance, destination)
        if path is None:
            return False
        guest_id = getattr(guest, 'name', None)
        if guest_id is None:
            return False
        occupied = self.geometry.occupy_cell(guest_id, destination)
        if not occupied:
            return False
        guest.position = {'x': destination['x'], 'y': destination['y']}
        guest.state = 'at_bar'
        return True
