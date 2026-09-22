from dataclasses import dataclass


@dataclass(slots=True)
class EntityDepartureIntent:
    wants_to_leave: bool = False

    def request_departure(self):
        self.wants_to_leave = True

    def cancel_departure(self):
        self.wants_to_leave = False

    def to_dict(self):
        return {
            "wants_to_leave": self.wants_to_leave,
        }
