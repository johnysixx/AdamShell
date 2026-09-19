from dataclasses import dataclass


@dataclass(slots=True)
class BarIncidentState:
    category: str
    reason: str
    offender: str | None
    name: str = "bar_security_incident"
    blacklist_after: bool | None = None
    resolved: bool = False
    resolution: str | None = None

    def resolve(
        self,
        resolution,
    ):
        self.resolved = True
        self.resolution = resolution

        return self

    def to_dict(self):
        state = {
            "name":
                self.name,
            "category":
                self.category,
            "reason":
                self.reason,
            "offender":
                self.offender,
            "resolved":
                self.resolved,
            "resolution":
                self.resolution,
        }

        if self.blacklist_after is not None:
            state[
                "blacklist_after"
            ] = self.blacklist_after

        return state
