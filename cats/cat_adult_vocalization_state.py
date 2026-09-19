from dataclasses import dataclass


@dataclass(slots=True)
class CatAdultVocalizationState:
    food_request: bool = False
    door_request: bool = False
    attention_request: bool = False
    greeting: bool = False
    warning: bool = False
    follow_me: bool = False
    distress_call: bool = False
    human_summoning: bool = False

    @classmethod
    def create(
        cls,
        learned=False,
    ):
        learned = bool(
            learned
        )

        return cls(
            food_request=learned,
            door_request=learned,
            attention_request=learned,
            greeting=learned,
            warning=learned,
            follow_me=learned,
            distress_call=learned,
            human_summoning=learned,
        )

    @classmethod
    def names(cls):
        return (
            "food_request",
            "door_request",
            "attention_request",
            "greeting",
            "warning",
            "follow_me",
            "distress_call",
            "human_summoning",
        )

    def knows(
        self,
        vocalization,
    ):
        self._require_name(
            vocalization
        )

        return bool(
            getattr(
                self,
                vocalization,
            )
        )

    def learn(
        self,
        vocalization,
    ):
        self._require_name(
            vocalization
        )

        setattr(
            self,
            vocalization,
            True,
        )

        return self

    def learned_count(
        self,
    ):
        return sum(
            1
            for vocalization
            in self.names()
            if self.knows(
                vocalization
            )
        )

    @property
    def complete(self):
        return (
            self.learned_count()
            == len(
                self.names()
            )
        )

    def to_dict(self):
        return {
            "food_request":
                self.food_request,
            "door_request":
                self.door_request,
            "attention_request":
                self.attention_request,
            "greeting":
                self.greeting,
            "warning":
                self.warning,
            "follow_me":
                self.follow_me,
            "distress_call":
                self.distress_call,
            "human_summoning":
                self.human_summoning,
        }

    @classmethod
    def _require_name(
        cls,
        vocalization,
    ):
        if (
            vocalization
            not in cls.names()
        ):
            raise ValueError(
                "Unknown adult feline "
                "vocalization."
            )
