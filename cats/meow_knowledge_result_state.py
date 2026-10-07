from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class MeowTeacherRoleResult:

    allowed: bool
    reason: str
    role: str | None = None


@dataclass(slots=True, frozen=True)
class MeowKnowledgeReadinessResult:

    allowed: bool
    reason: str
    missing_experiences: tuple[str, ...] = ()
    teacher_role: MeowTeacherRoleResult | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "missing_experiences",
            tuple(
                self.missing_experiences
            ),
        )

        if (
            self.teacher_role is not None
            and not isinstance(
                self.teacher_role,
                MeowTeacherRoleResult,
            )
        ):
            raise TypeError(
                "MEOW readiness teacher role "
                "must be MeowTeacherRoleResult."
            )


@dataclass(slots=True, frozen=True)
class MeowKnowledgeLesson:

    name: str
    teacher: str
    student: str
    day: int
    knowledge: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(
            self,
            "knowledge",
            tuple(
                self.knowledge
            ),
        )


@dataclass(slots=True, frozen=True)
class MeowKnowledgeTransmissionDeniedEvent:

    mother: str | None
    kitten: str | None
    day: int
    reason: str
    missing_experiences: tuple[str, ...]

    name: str = field(
        default=(
            "meow_knowledge_transmission_denied"
        ),
        init=False,
    )

    transmitted: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "missing_experiences",
            tuple(
                self.missing_experiences
            ),
        )


@dataclass(slots=True, frozen=True)
class MeowKnowledgeTransmittedEvent:

    mother: str
    kitten: str
    day: int
    knowledge: tuple[str, ...]
    adult_meowing_learned: bool
    human_communication_learned: bool
    learning_complete: bool
    teacher_role: str
    transmission_source: str
    awareness_transferred: int
    ability_methods_transferred: int = 0

    name: str = field(
        default="meow_knowledge_transmitted",
        init=False,
    )

    transmitted: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "knowledge",
            tuple(
                self.knowledge
            ),
        )
