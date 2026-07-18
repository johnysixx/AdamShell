class StaffGlassShelf:

    def __init__(self):
        self.name = "staff_glass_shelf"
        self.location = "back_room"
        self.glasses = {}

        print("STAFF GLASS SHELF CREATED IN BACK ROOM")

    def create_staff_glass(self, staff_member):
        staff_name = getattr(
            staff_member,
            "name",
            None
        )

        if staff_name is None:
            return None

        if staff_name in self.glasses:
            return self.glasses[staff_name]

        glass = {
            "name": f"{staff_name}_glass",
            "type": "staff_personal_glass",
            "owner": staff_name,
            "state": "clean",
            "dirt": 0.0,
            "location": self.name
        }

        self.glasses[staff_name] = glass

        print(
            f"STAFF GLASS CREATED: "
            f"{glass['name']}"
        )

        return glass
