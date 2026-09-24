from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType

from cats.genotype import CatGenotype
from cats.phenotype_resolver import CatPhenotypeResolver
from cats.kitten_viability_resolver import KittenGeneticViabilityResolver
from cats.cat_birth_objects import CatBirthProfile, KittenEmbryo


class _FrozenEmbryoList(tuple):
    pass


class _FrozenEmbryoSet(frozenset):
    pass


def _freeze_embryo_payload(value):
    if isinstance(value, dict):
        return MappingProxyType({
            key: _freeze_embryo_payload(item)
            for key, item in value.items()
        })

    if isinstance(value, list):
        return _FrozenEmbryoList(
            _freeze_embryo_payload(item)
            for item in value
        )

    if isinstance(value, tuple):
        return tuple(
            _freeze_embryo_payload(item)
            for item in value
        )

    if isinstance(value, set):
        return _FrozenEmbryoSet(
            _freeze_embryo_payload(item)
            for item in value
        )

    if isinstance(value, frozenset):
        return frozenset(
            _freeze_embryo_payload(item)
            for item in value
        )

    return deepcopy(value)


def _thaw_embryo_payload(value):
    if isinstance(
        value,
        MappingProxyType,
    ):
        return {
            key: _thaw_embryo_payload(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        _FrozenEmbryoList,
    ):
        return [
            _thaw_embryo_payload(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return tuple(
            _thaw_embryo_payload(item)
            for item in value
        )

    if isinstance(
        value,
        _FrozenEmbryoSet,
    ):
        return {
            _thaw_embryo_payload(item)
            for item in value
        }

    if isinstance(value, frozenset):
        return frozenset(
            _thaw_embryo_payload(item)
            for item in value
        )

    return deepcopy(value)


@dataclass(slots=True, frozen=True)
class KittenGeneticViabilitySnapshot:

    status: str
    viable: bool
    rare: bool
    reason: str | None
    details: object
    special_traits: tuple[str, ...]
    genotype: CatGenotype
    name: str = field(
        default=(
            "kitten_genetic_viability_resolved"
        ),
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.genotype,
            CatGenotype,
        ):
            raise TypeError(
                "Viability snapshot requires "
                "a CatGenotype object."
            )

        object.__setattr__(
            self,
            "status",
            str(self.status),
        )

        object.__setattr__(
            self,
            "viable",
            bool(self.viable),
        )

        object.__setattr__(
            self,
            "rare",
            bool(self.rare),
        )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(self.reason),
            )

        object.__setattr__(
            self,
            "details",
            _freeze_embryo_payload(
                self.details
            ),
        )

        object.__setattr__(
            self,
            "special_traits",
            tuple(
                str(trait)
                for trait
                in self.special_traits
            ),
        )

    @classmethod
    def from_boundary(
        cls,
        payload,
    ):
        if not isinstance(
            payload,
            dict,
        ):
            raise TypeError(
                "Kitten viability boundary "
                "payload must be dict."
            )

        return cls(
            status=payload["status"],
            viable=payload["viable"],
            rare=payload["rare"],
            reason=payload.get(
                "reason"
            ),
            details=payload.get(
                "details"
            ),
            special_traits=tuple(
                payload.get(
                    "special_traits",
                    (),
                )
            ),
            genotype=payload[
                "genotype"
            ],
        )

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "viable": self.viable,
            "rare": self.rare,
            "reason": self.reason,
            "details": (
                _thaw_embryo_payload(
                    self.details
                )
            ),
            "special_traits": list(
                self.special_traits
            ),
            "genotype": self.genotype,
        }


@dataclass(slots=True, frozen=True)
class NonviableKittenEmbryoReplacedByCronenbergEvent:

    embryo_id: str
    mother: str
    father: str
    genotype: CatGenotype
    viability: (
        KittenGeneticViabilitySnapshot
    )
    cronenberg_id: str
    name: str = field(
        default=(
            "nonviable_kitten_embryo_"
            "replaced_by_cronenberg"
        ),
        init=False,
    )
    kitten_created: bool = field(
        default=False,
        init=False,
    )
    cronenberg_created: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.genotype,
            CatGenotype,
        ):
            raise TypeError(
                "Nonviable embryo event "
                "requires a CatGenotype object."
            )

        if not isinstance(
            self.viability,
            KittenGeneticViabilitySnapshot,
        ):
            raise TypeError(
                "Nonviable embryo event "
                "requires a viability object."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "embryo_id": self.embryo_id,
            "mother": self.mother,
            "father": self.father,
            "genotype": self.genotype,
            "viability": (
                self.viability.to_dict()
            ),
            "kitten_created": (
                self.kitten_created
            ),
            "cronenberg_created": (
                self.cronenberg_created
            ),
            "cronenberg_id": (
                self.cronenberg_id
            ),
        }


@dataclass(slots=True, frozen=True)
class KittenEmbryoCreatedEvent:

    embryo_id: str
    mother: str
    father: str
    genetic_status: str
    rare: bool
    profile: CatBirthProfile
    name: str = field(
        default="kitten_embryo_created",
        init=False,
    )
    kitten_created: bool = field(
        default=False,
        init=False,
    )
    cronenberg_created: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.profile,
            CatBirthProfile,
        ):
            raise TypeError(
                "Embryo event profile requires "
                "a CatBirthProfile object."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "embryo_id": self.embryo_id,
            "mother": self.mother,
            "father": self.father,
            "genetic_status": (
                self.genetic_status
            ),
            "rare": self.rare,
            "profile": (
                self.profile.to_dict()
            ),
            "kitten_created": (
                self.kitten_created
            ),
            "cronenberg_created": (
                self.cronenberg_created
            ),
        }


class KittenEmbryoResolver:

    def __init__(self, universe):
        self.universe = universe
        self.history = []
        self.embryo_count = 0

    def create_embryo(self, mother, father, rng, genotype_override=None):
        self._validate_parents(mother, father)
        self.embryo_count += 1
        embryo_id = f'embryo_{self.embryo_count:04d}'
        genotype = genotype_override if genotype_override is not None else CatGenotype.inherit(mother_genotype=mother.genotype, father_genotype=father.genotype, rng=rng)
        viability = KittenGeneticViabilityResolver.resolve(genotype)
        if not viability['viable']:
            cronenberg = self.universe.create_cronenberg_from_quantum_error(error=RuntimeError(f'Nonviable kitten genotype replaced embryo {embryo_id}.'), source_component='kitten_embryo_resolver', source_operation='nonviable_embryo')
            event = (
                NonviableKittenEmbryoReplacedByCronenbergEvent(
                    embryo_id=embryo_id,
                    mother=mother.name,
                    father=father.name,
                    genotype=genotype,
                    viability=(
                        KittenGeneticViabilitySnapshot
                        .from_boundary(
                            viability
                        )
                    ),
                    cronenberg_id=cronenberg.id,
                )
            )

            self.record_event(
                event
            )

            event_snapshot = (
                event.to_dict()
            )

            self.universe.quantum_events.append(
                event.to_dict()
            )

            return {
                'embryo': None,
                'viability': viability,
                'cronenberg': cronenberg,
                'event': event_snapshot,
                'viable': False,
            }
        phenotype = CatPhenotypeResolver.resolve(genotype)
        embryo = KittenEmbryo(**{'id': embryo_id, 'type': 'kitten_embryo', 'state': 'gestating', 'mother_name': mother.name, 'father_name': father.name, 'genotype': genotype, 'phenotype': phenotype, 'profile': dict(phenotype['profile']), 'viability': viability, 'genetic_status': viability['status'], 'rare': viability['rare'], 'special_traits': list(viability['special_traits'])})
        event = KittenEmbryoCreatedEvent(
            embryo_id=embryo_id,
            mother=mother.name,
            father=father.name,
            genetic_status=viability['status'],
            rare=viability['rare'],
            profile=CatBirthProfile(
                **phenotype['profile']
            ),
        )

        self.record_event(
            event
        )

        return {
            'embryo': embryo,
            'viability': viability,
            'phenotype': phenotype,
            'cronenberg': None,
            'event': event.to_dict(),
            'viable': True,
        }

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            (
                NonviableKittenEmbryoReplacedByCronenbergEvent,
                KittenEmbryoCreatedEvent,
            ),
        ):
            raise TypeError(
                "Kitten embryo history requires "
                "a kitten embryo event object."
            )

        self.history.append(
            event
        )

        return event

    @staticmethod
    def _validate_parents(mother, father):
        if getattr(mother, 'sex', None) != 'female':
            raise ValueError('Embryo mother must be female.')
        if getattr(father, 'sex', None) != 'male':
            raise ValueError('Embryo father must be male.')
        if not hasattr(mother, 'genotype'):
            raise ValueError('Mother has no genotype.')
        if not hasattr(father, 'genotype'):
            raise ValueError('Father has no genotype.')
