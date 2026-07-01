class CreationEvent:

    def __init__(self, name):
        self.name = name

    def apply(self, universe):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement apply()"
        )