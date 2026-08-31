class BarServiceProtocol:

    def __init__(self, geometry):
        self.geometry = geometry

    def move_bartender(self, bartender, target):
        if bartender is None or target is None:
            return False
        if target.kind != "service_floor":
            return False
        position = getattr(bartender, "position", None)
        if position is None:
            return False
        start = self.geometry.find_cell(
            x=position["x"],
            y=position["y"],
        )
        if start is None or start.kind != "service_floor":
            return False
        queue = [start]
        visited = {start.name}
        cursor = 0
        reachable = False
        while cursor < len(queue):
            current = queue[cursor]
            cursor += 1
            if current is target:
                reachable = True
                break
            for neighbor in self.geometry.neighbors(current):
                if neighbor.kind != "service_floor":
                    continue
                if neighbor.name in visited:
                    continue
                visited.add(neighbor.name)
                queue.append(neighbor)
        if not reachable:
            return False
        bartender.position = {"x": target.x, "y": target.y}
        bartender.state = "behind_bar"
        return True

    def place_bartender(self, bartender):
        if bartender is None:
            return False
        service = self.geometry.find_cell(name="bar_service_floor")
        if service is None:
            return False
        if service.kind != "service_floor":
            return False
        bartender.position = {"x": service.x, "y": service.y}
        bartender.state = "behind_bar"
        return True
