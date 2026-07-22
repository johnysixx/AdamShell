class Potential:

    def __init__(
        self,
        possibility,
        cycle_id,
        source=None,
        context=None
    ):
        self.possibility = possibility
        self.cycle_id = cycle_id
        self.source = source
        self.context = context or {}

        self.state = "open"

    @property
    def name(self):
        return self.possibility.name

    @property
    def is_available(self):
        return self.possibility.is_available()

    @property
    def is_open(self):
        return self.state == "open"

    def mark_actualized(self):
        if not self.is_open:
            return False

        self.state = "actualized"
        return True

    def mark_unrealized(self):
        if not self.is_open:
            return False

        self.state = "unrealized"
        return True

    @property
    def public_state(self):
        return {
            "name": self.name,
            "cycle_id": self.cycle_id,
            "source": self.source,
            "context": dict(self.context),
            "state": self.state,
            "available": self.is_available,
            "mandatory": self.possibility.mandatory,
            "probability": self.possibility.probability
        }
