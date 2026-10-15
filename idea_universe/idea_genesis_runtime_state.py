from dataclasses import dataclass, field


def _entity_name(value):
    return getattr(
        value,
        "name",
        str(value),
    )


def _snapshot_record(value):
    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        return to_dict()

    return value


@dataclass(slots=True, frozen=True)
class IdeaGenesisBootstrapResult:
    god: object
    tiamat: object
    apsu: object
    serpent: object | None


@dataclass(slots=True, frozen=True)
class IdeaFirstDivineGenerationResult:
    lahmu: object
    lahamu: object


@dataclass(slots=True, frozen=True)
class IdeaSecondDivineGenerationResult:
    anshar: object
    kishar: object


@dataclass(slots=True, frozen=True)
class IdeaGenesisWordEvent:
    word: str
    day: int | None = None

    kind: str = field(
        default="genesis",
        init=False,
    )

    def to_dict(self):
        snapshot = {
            "kind": self.kind,
            "word": self.word,
        }

        if self.day is not None:
            snapshot["day"] = self.day

        return snapshot


@dataclass(slots=True, frozen=True)
class IdeaGenesisLifeEvent:
    word: str
    day: int
    aquatic_life_archetype: bool = False
    flying_life_archetype: bool = False
    created: str | None = None

    kind: str = field(
        default="genesis",
        init=False,
    )

    def to_dict(self):
        snapshot = {
            "kind": self.kind,
            "word": self.word,
            "day": self.day,
            "aquatic_life_archetype": (
                self.aquatic_life_archetype
            ),
            "flying_life_archetype": (
                self.flying_life_archetype
            ),
        }

        if self.created is not None:
            snapshot["created"] = self.created

        return snapshot


@dataclass(slots=True, frozen=True)
class IdeaDivineGenealogyEvent:
    generation: int | str
    parents: tuple[str, ...]
    children: tuple[str, ...]
    epithets: tuple[str, ...] = ()

    kind: str = field(
        default="divine_genealogy",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "parents",
            tuple(self.parents),
        )
        object.__setattr__(
            self,
            "children",
            tuple(self.children),
        )
        object.__setattr__(
            self,
            "epithets",
            tuple(self.epithets),
        )

    def to_dict(self):
        snapshot = {
            "kind": self.kind,
            "generation": self.generation,
            "parents": list(self.parents),
            "children": list(self.children),
        }

        if self.epithets:
            snapshot["epithets"] = {
                self.children[0]:
                    list(self.epithets)
            }

        return snapshot


@dataclass(slots=True, frozen=True)
class IdeaDivineManifestationEvent:
    mask: str
    mask_of: str
    parents: tuple[str, ...]

    kind: str = field(
        default="divine_manifestation",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "parents",
            tuple(self.parents),
        )

    def to_dict(self):
        return {
            "kind": self.kind,
            "mask": self.mask,
            "mask_of": self.mask_of,
            "parents": list(self.parents),
        }


@dataclass(slots=True, frozen=True)
class IdeaDivineAuthorityEvent:
    mask: str
    title: str

    kind: str = field(
        default="divine_authority",
        init=False,
    )

    def to_dict(self):
        return {
            "kind": self.kind,
            "mask": self.mask,
            "title": self.title,
        }


@dataclass(slots=True, frozen=True)
class IdeaDivineConfrontationResult:
    marduk: object
    tiamat: object

    event: str = field(
        default="marduk_confronts_tiamat",
        init=False,
    )


@dataclass(slots=True, frozen=True)
class IdeaDivineConflictEvent:
    actor_mask: str
    actor: object
    target: object

    kind: str = field(
        default="divine_conflict",
        init=False,
    )

    event: str = field(
        default="tiamat_defeated",
        init=False,
    )

    def to_dict(self):
        return {
            "kind": self.kind,
            "event": self.event,
            "actor_mask": self.actor_mask,
            "actor": _entity_name(
                self.actor
            ),
            "target": _entity_name(
                self.target
            ),
        }


@dataclass(slots=True, frozen=True)
class IdeaCosmicOrderEvent:
    actor_mask: str
    actor: object
    source: object

    kind: str = field(
        default="cosmic_order",
        init=False,
    )

    event: str = field(
        default="cosmos_ordered_from_tiamat",
        init=False,
    )

    def to_dict(self):
        return {
            "kind": self.kind,
            "event": self.event,
            "actor_mask": self.actor_mask,
            "actor": _entity_name(
                self.actor
            ),
            "source": _entity_name(
                self.source
            ),
        }


@dataclass(slots=True, frozen=True)
class IdeaCanonicalCosmicOrderEvent:
    genesis_record: object
    mesopotamian_record: object

    kind: str = field(
        default="canonical_event",
        init=False,
    )

    event: str = field(
        default="cosmic_order_established",
        init=False,
    )

    witnesses: tuple[str, str] = field(
        default=(
            "genesis",
            "mesopotamian",
        ),
        init=False,
    )

    genesis_event: str = field(
        default="heavenly_lights_created",
        init=False,
    )

    mesopotamian_event: str = field(
        default="cosmos_ordered_from_tiamat",
        init=False,
    )

    def to_dict(self):
        return {
            "kind": self.kind,
            "event": self.event,
            "witnesses": {
                "genesis": {
                    "event": self.genesis_event,
                    "record": _snapshot_record(
                        self.genesis_record
                    ),
                },
                "mesopotamian": {
                    "event": self.mesopotamian_event,
                    "record": _snapshot_record(
                        self.mesopotamian_record
                    ),
                },
            },
        }


@dataclass(slots=True, frozen=True)
class IdeaDivineFunctionAssignment:
    god_name: str
    function: str

    def to_dict(self):
        return {
            "god": self.god_name,
            "function": self.function,
        }


@dataclass(slots=True, frozen=True)
class IdeaDivineOrderEvent:
    actor_mask: str
    actor: object
    assignments: tuple[
        IdeaDivineFunctionAssignment,
        ...,
    ]

    kind: str = field(
        default="divine_order",
        init=False,
    )

    event: str = field(
        default="divine_order_established",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "assignments",
            tuple(self.assignments),
        )

        if not all(
            isinstance(
                assignment,
                IdeaDivineFunctionAssignment,
            )
            for assignment
            in self.assignments
        ):
            raise TypeError(
                "Divine order assignments must "
                "be IdeaDivineFunctionAssignment."
            )

    def to_dict(self):
        return {
            "kind": self.kind,
            "event": self.event,
            "actor_mask": self.actor_mask,
            "actor": _entity_name(
                self.actor
            ),
            "assignments": {
                assignment.god_name:
                    assignment.function
                for assignment
                in self.assignments
            },
        }
