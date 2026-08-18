class BarDepartureProtocol:

    def __init__(
        self,
        geometry
    ):
        self.geometry = geometry

    def leave_bar(
        self,
        guest
    ):
        if guest is None:
            return False

        guest_id = guest.get(
            "name"
        )

        position = guest.get(
            "position"
        )

        if (
            guest_id is None
            or position is None
        ):
            return False

        place = self.geometry.find_cell(
            x=position["x"],
            y=position["y"]
        )

        if place is None:
            return False

        if place["kind"] != "customer_floor":
            return False

        released = self.geometry.release_cell(
            guest_id,
            place
        )

        if not released:
            return False

        guest["state"] = "leaving_bar"
        guest["position"] = None

        return True
