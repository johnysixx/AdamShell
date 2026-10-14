from dataclasses import dataclass, field
from types import MappingProxyType

from universe.atom_state import (
    AtomFormationState,
)
from universe.atoms_process_state import (
    AtomsProcessState,
)
from universe.atomic_nuclei_process_state import (
    AtomicNucleiProcessState,
)
from universe.chemical_objects import (
    ChemicalMolecule,
    NeutralAtom,
)
from universe.molecule_state import (
    MoleculeFormationState,
)
from universe.molecules_process_state import (
    MoleculesProcessState,
)
from universe.nuclear_objects import (
    AtomicNucleus,
)
from universe.nuclear_state import (
    NuclearFormationState,
)
from universe.particle_objects import (
    CompositeParticle,
    ElementaryParticle,
    ParticleField,
    ParticleInteraction,
)
from universe.particle_state import (
    ParticleFormationState,
)
from universe.particles_process_state import (
    ParticlesProcessState,
)


def _freeze_registry(
    registry,
    expected_type,
    label,
):
    values = dict(
        registry
    )

    for value in values.values():
        if not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"{label} must contain "
                f"{expected_type.__name__} objects."
            )

    return MappingProxyType(
        values
    )


@dataclass(
    slots=True,
    frozen=True,
)
class ParticleFormationResult:

    state: ParticlesProcessState
    elementary_particles: object
    composite_particles: object
    fields: object
    interactions: object
    particle_state: ParticleFormationState

    name: str = field(
        default="particles",
        init=False,
    )
    type: str = field(
        default="particle_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            ParticlesProcessState,
        ):
            raise TypeError(
                "Particle result state must use "
                "ParticlesProcessState."
            )

        if not isinstance(
            self.particle_state,
            ParticleFormationState,
        ):
            raise TypeError(
                "Particle result formation state must "
                "use ParticleFormationState."
            )

        object.__setattr__(
            self,
            "elementary_particles",
            _freeze_registry(
                self.elementary_particles,
                ElementaryParticle,
                "Elementary particle registry",
            ),
        )
        object.__setattr__(
            self,
            "composite_particles",
            _freeze_registry(
                self.composite_particles,
                CompositeParticle,
                "Composite particle registry",
            ),
        )
        object.__setattr__(
            self,
            "fields",
            _freeze_registry(
                self.fields,
                ParticleField,
                "Particle field registry",
            ),
        )
        object.__setattr__(
            self,
            "interactions",
            _freeze_registry(
                self.interactions,
                ParticleInteraction,
                "Particle interaction registry",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "elementary_particles": {
                name: particle.to_dict()
                for name, particle
                in self.elementary_particles.items()
            },
            "composite_particles": {
                name: particle.to_dict()
                for name, particle
                in self.composite_particles.items()
            },
            "fields": {
                name: field_value.to_dict()
                for name, field_value
                in self.fields.items()
            },
            "interactions": {
                name: interaction.to_dict()
                for name, interaction
                in self.interactions.items()
            },
            "particle_state": (
                self.particle_state.to_dict()
            ),
        }


@dataclass(
    slots=True,
    frozen=True,
)
class AtomicNucleiFormationResult:

    state: AtomicNucleiProcessState
    nuclei: object
    nuclear_state: NuclearFormationState

    name: str = field(
        default="atomic_nuclei",
        init=False,
    )
    type: str = field(
        default="nuclear_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            AtomicNucleiProcessState,
        ):
            raise TypeError(
                "Atomic nuclei result state must use "
                "AtomicNucleiProcessState."
            )

        if not isinstance(
            self.nuclear_state,
            NuclearFormationState,
        ):
            raise TypeError(
                "Atomic nuclei formation state must "
                "use NuclearFormationState."
            )

        object.__setattr__(
            self,
            "nuclei",
            _freeze_registry(
                self.nuclei,
                AtomicNucleus,
                "Atomic nucleus registry",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "nuclei": {
                name: nucleus.to_dict()
                for name, nucleus
                in self.nuclei.items()
            },
            "nuclear_state": (
                self.nuclear_state.to_dict()
            ),
        }


@dataclass(
    slots=True,
    frozen=True,
)
class AtomFormationResult:

    state: AtomsProcessState
    atoms: object
    atom_state: AtomFormationState

    name: str = field(
        default="atoms",
        init=False,
    )
    type: str = field(
        default="atomic_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            AtomsProcessState,
        ):
            raise TypeError(
                "Atom result state must use "
                "AtomsProcessState."
            )

        if not isinstance(
            self.atom_state,
            AtomFormationState,
        ):
            raise TypeError(
                "Atom result formation state must "
                "use AtomFormationState."
            )

        object.__setattr__(
            self,
            "atoms",
            _freeze_registry(
                self.atoms,
                NeutralAtom,
                "Neutral atom registry",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "atoms": {
                name: atom.to_dict()
                for name, atom
                in self.atoms.items()
            },
            "atom_state": (
                self.atom_state.to_dict()
            ),
        }


@dataclass(
    slots=True,
    frozen=True,
)
class MoleculeFormationResult:

    state: MoleculesProcessState
    molecules: object
    molecule_state: MoleculeFormationState

    name: str = field(
        default="molecules",
        init=False,
    )
    type: str = field(
        default="molecular_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            MoleculesProcessState,
        ):
            raise TypeError(
                "Molecule result state must use "
                "MoleculesProcessState."
            )

        if not isinstance(
            self.molecule_state,
            MoleculeFormationState,
        ):
            raise TypeError(
                "Molecule result formation state must "
                "use MoleculeFormationState."
            )

        object.__setattr__(
            self,
            "molecules",
            _freeze_registry(
                self.molecules,
                ChemicalMolecule,
                "Molecule registry",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "molecules": {
                name: molecule.to_dict()
                for name, molecule
                in self.molecules.items()
            },
            "molecule_state": (
                self.molecule_state.to_dict()
            ),
        }
