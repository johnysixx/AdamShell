from dataclasses import dataclass, field


@dataclass(slots=True)
class FelineAwarenessState:
    name: str
    domain: str
    known_to_exist: bool = True
    description: str | None = None
    known_teachers: list[str] = field(
        default_factory=list
    )
    transfer_mode: str = (
        "awareness_only"
    )
    received_from: str | None = None
    received_on_day: int | None = None

    def copy_for_transfer(
        self,
        received_from=None,
        received_on_day=None,
    ):
        return FelineAwarenessState(
            name=self.name,
            domain=self.domain,
            known_to_exist=(
                self.known_to_exist
            ),
            description=self.description,
            known_teachers=list(
                self.known_teachers
            ),
            transfer_mode=(
                self.transfer_mode
            ),
            received_from=received_from,
            received_on_day=(
                None
                if received_on_day is None
                else int(received_on_day)
            ),
        )
