class Possibility:

    def __init__(
        self,
        name,
        probability,
        action=None,
        condition=None,
        mandatory=False
    ):
        if not 0.0 <= probability <= 1.0:
            raise ValueError(
                "Probability must be between 0.0 and 1.0"
            )

        self.name = name
        self.probability = probability
        self.action = action
        self.condition = condition
        self.mandatory = mandatory

    def is_available(self):
        if self.condition is None:
            return True

        return bool(
            self.condition()
        )

    def actualize(self):
        if self.action is None:
            return {
                "name": self.name
            }

        return self.action()

    @property
    def public_state(self):
        return {
            "name": self.name,
            "probability": self.probability,
            "mandatory": self.mandatory,
            "available": self.is_available()
        }
