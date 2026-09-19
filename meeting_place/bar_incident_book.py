from universe.logger import UniverseLogger
from meeting_place.bar_incident_state import (
    BarIncidentState,
)


class BarIncidentBook:

    ALLOWED_CATEGORIES = {
        "disturbance",
        "access_violation",
        "violence",
        "theft",
        "property_damage",
        "medical_emergency",
        "cat_related",
    }

    REASON_CATEGORIES = {
        "unauthorized_area": "access_violation",
        "unknown_disturbance": "disturbance",
    }

    ALLOWED_RESOLUTIONS = {
        "bouncer_summoned",
        "ejected_and_blacklisted",
    }

    REASON_RESOLUTIONS = {
        "unknown_disturbance": "bouncer_summoned",
        "unauthorized_area": "ejected_and_blacklisted",
    }

    def __init__(
        self,
        recorder,
        event_emitter=None
    ):
        if recorder is None:
            raise ValueError(
                "BarIncidentBook requires recorder."
            )

        self.name = "bar_incident_book"
        self.type = "bar_security_record"
        self.recorder = recorder
        self.event_emitter = event_emitter

        UniverseLogger.boot(
            "BAR INCIDENT BOOK CREATED"
        )

    @property
    def incidents(
        self
    ):
        if self.recorder is None:
            return []

        incidents = []

        for recorder_entry in (
            self.recorder.entries
        ):
            if (
                recorder_entry.get(
                    "event"
                )
                != "bar_security_incident"
            ):
                continue

            incident = (
                recorder_entry.get(
                    "data"
                )
            )

            if not isinstance(
                incident,
                BarIncidentState,
            ):
                raise TypeError(
                    "Bar incident record must "
                    "be BarIncidentState."
                )

            incidents.append(
                incident
            )

        return incidents

    def record(
        self,
        incident
    ):
        if not isinstance(
            incident,
            BarIncidentState,
        ):
            raise TypeError(
                "Bar incident must be "
                "BarIncidentState."
            )

        name = incident.name

        if name != "bar_security_incident":
            raise ValueError(
                "Bar incident requires name "
                "'bar_security_incident'."
            )

        category = (
            incident.category
        )

        if not category:
            raise ValueError(
                "Bar incident requires category."
            )

        if category not in self.ALLOWED_CATEGORIES:
            raise ValueError(
                f"Unknown bar incident category: {category}"
            )

        reason = (
            incident.reason
        )

        if not reason:
            raise ValueError(
                "Bar incident requires reason."
            )

        offender = (
            incident.offender
        )

        if (
            offender is not None
            and (
                not isinstance(
                    offender,
                    str
                )
                or not offender.strip()
            )
        ):
            raise ValueError(
                "Bar incident offender must be "
                "a non-empty string or None."
            )

        if (
            reason == "unauthorized_area"
            and not offender
        ):
            raise ValueError(
                "Unauthorized area incident "
                "requires offender."
            )

        expected_category = (
            self.REASON_CATEGORIES.get(
                reason
            )
        )

        if (
            expected_category is not None
            and category != expected_category
        ):
            raise ValueError(
                f"Reason {reason} requires category "
                f"{expected_category}."
            )

        incident.resolved = False
        incident.resolution = None

        if self.event_emitter is not None:
            self.event_emitter(
                incident
            )
        else:
            self.recorder.record(
                event=incident.name,
                data=incident,
                source=self.name,
                tick=None
            )

        UniverseLogger.event(
            "BAR INCIDENT RECORDED: "
            f"{incident.reason}"
        )

        return incident

    def resolve(
        self,
        entry,
        resolution
    ):
        if not isinstance(
            entry,
            BarIncidentState,
        ):
            raise TypeError(
                "Bar incident entry must be "
                "BarIncidentState."
            )

        if entry not in self.incidents:
            raise ValueError(
                "Incident entry is not in this book."
            )

        if not resolution:
            raise ValueError(
                "Incident resolution must not be empty."
            )

        if resolution not in self.ALLOWED_RESOLUTIONS:
            raise ValueError(
                f"Unknown incident resolution: {resolution}"
            )

        reason = entry.reason

        expected_resolution = (
            self.REASON_RESOLUTIONS.get(
                reason
            )
        )

        if (
            expected_resolution is not None
            and resolution != expected_resolution
        ):
            raise ValueError(
                f"Reason {reason} requires resolution "
                f"{expected_resolution}."
            )

        entry.resolve(
            resolution
        )

        UniverseLogger.event(
            "BAR INCIDENT RESOLVED: "
            f"{entry.reason} "
            f"AS {resolution}"
        )

        return entry
