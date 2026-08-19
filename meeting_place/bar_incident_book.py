from universe.logger import UniverseLogger


class BarIncidentBook:

    def __init__(self):
        self.name = "bar_incident_book"
        self.type = "bar_security_record"
        self.incidents = []

        UniverseLogger.boot(
            "BAR INCIDENT BOOK CREATED"
        )

    def record(
        self,
        incident
    ):
        if not isinstance(
            incident,
            dict
        ):
            raise TypeError(
                "Bar incident must be a dict."
            )

        entry = dict(
            incident
        )

        entry["resolved"] = False

        self.incidents.append(
            entry
        )

        UniverseLogger.event(
            "BAR INCIDENT RECORDED: "
            f"{entry.get('reason')}"
        )

        return entry

    def resolve(
        self,
        entry,
        resolution
    ):
        if entry not in self.incidents:
            raise ValueError(
                "Incident entry is not in this book."
            )

        entry["resolved"] = True
        entry["resolution"] = resolution

        UniverseLogger.event(
            "BAR INCIDENT RESOLVED: "
            f"{entry.get('reason')} "
            f"AS {resolution}"
        )

        return entry


