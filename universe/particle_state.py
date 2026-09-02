from dataclasses import dataclass


@dataclass(slots=True)
class ParticleFormationState:

    elementary_particles_formed: bool = False
    quarks_available: bool = False
    leptons_available: bool = False
    neutrinos_available: bool = False
    gauge_bosons_available: bool = False
    higgs_available: bool = False
    protons_formed: bool = False
    neutrons_formed: bool = False
    nucleons_formed: bool = False
    particle_relationships_defined: bool = False

    def to_dict(self):
        return {
            "elementary_particles_formed": (
                self.elementary_particles_formed
            ),
            "quarks_available": self.quarks_available,
            "leptons_available": self.leptons_available,
            "neutrinos_available": (
                self.neutrinos_available
            ),
            "gauge_bosons_available": (
                self.gauge_bosons_available
            ),
            "higgs_available": self.higgs_available,
            "protons_formed": self.protons_formed,
            "neutrons_formed": self.neutrons_formed,
            "nucleons_formed": self.nucleons_formed,
            "particle_relationships_defined": (
                self.particle_relationships_defined
            ),
        }
