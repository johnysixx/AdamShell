class Particles:

    def __init__(self, universe):
        self.universe = universe
        self.name = "particles"
        self.type = "particle_layer"
        self.state = "ready"

        self.elementary_particles = {}
        self.composite_particles = {}
        self.fields = {}
        self.interactions = {}

        self.particle_state = {
            "elementary_particles_formed": False,
            "quarks_available": False,
            "leptons_available": False,
            "neutrinos_available": False,
            "gauge_bosons_available": False,
            "higgs_available": False,
            "protons_formed": False,
            "neutrons_formed": False,
            "nucleons_formed": False,
            "particle_relationships_defined": False
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "elementary_particles": self.elementary_particles,
            "composite_particles": self.composite_particles,
            "fields": self.fields,
            "interactions": self.interactions,
            "particle_state": self.particle_state
        }

    def form_particles(self):
        big_bang = self.universe.world.get("big_bang", {})

        if big_bang.get("state") != "completed":
            self.state = "failed"
            self.public_state["state"] = self.state

            print("PARTICLE FORMATION FAILED: Big Bang process is not completed")
            self.write_to_world()
            return self.public_state

        self.state = "formed"
        self.public_state["state"] = self.state

        self.form_quarks()
        self.form_leptons()
        self.form_bosons()
        self.form_fields()
        self.form_nucleons()
        self.define_interactions()

        self.particle_state["elementary_particles_formed"] = True
        self.particle_state["particle_relationships_defined"] = True

        self.record_history()
        self.write_to_world()

        print("ELEMENTARY PARTICLES FORMED")
        print("QUARKS AVAILABLE")
        print("LEPTONS AND NEUTRINOS AVAILABLE")
        print("GAUGE BOSONS AVAILABLE")
        print("HIGGS FIELD AND HIGGS BOSON AVAILABLE")
        print("PROTONS AND NEUTRONS FORMED")
        print("PARTICLE RELATIONSHIPS DEFINED")

        return self.public_state

    def form_quarks(self):
        self.add_elementary_particle("up_quark", "quark", "+2/3", "light_quark")
        self.add_elementary_particle("down_quark", "quark", "-1/3", "light_quark")
        self.add_elementary_particle("charm_quark", "quark", "+2/3", "heavy_quark")
        self.add_elementary_particle("strange_quark", "quark", "-1/3", "heavy_quark")
        self.add_elementary_particle("top_quark", "quark", "+2/3", "heavy_quark")
        self.add_elementary_particle("bottom_quark", "quark", "-1/3", "heavy_quark")

        self.particle_state["quarks_available"] = True

    def form_leptons(self):
        self.add_elementary_particle("electron", "lepton", "-1", "charged_lepton")
        self.add_elementary_particle("muon", "lepton", "-1", "charged_lepton")
        self.add_elementary_particle("tau", "lepton", "-1", "charged_lepton")

        self.add_elementary_particle("electron_neutrino", "lepton", "0", "neutrino")
        self.add_elementary_particle("muon_neutrino", "lepton", "0", "neutrino")
        self.add_elementary_particle("tau_neutrino", "lepton", "0", "neutrino")

        self.particle_state["leptons_available"] = True
        self.particle_state["neutrinos_available"] = True

    def form_bosons(self):
        self.add_elementary_particle("photon", "gauge_boson", "0", "electromagnetic_force_carrier")
        self.add_elementary_particle("gluon", "gauge_boson", "0", "strong_force_carrier")
        self.add_elementary_particle("w_boson_minus", "gauge_boson", "-1", "weak_force_carrier")
        self.add_elementary_particle("w_boson_plus", "gauge_boson", "+1", "weak_force_carrier")
        self.add_elementary_particle("z_boson", "gauge_boson", "0", "weak_force_carrier")
        self.add_elementary_particle("higgs_boson", "scalar_boson", "0", "higgs_field_excitation")

        self.particle_state["gauge_bosons_available"] = True
        self.particle_state["higgs_available"] = True

    def form_fields(self):
        self.fields["higgs_field"] = {
            "name": "higgs_field",
            "type": "field",
            "state": "active",
            "role": "mass_mechanism",
            "related_particle": "higgs_boson"
        }

        self.fields["gravity_field"] = {
            "name": "gravity_field",
            "type": "symbolic_field",
            "state": "active",
            "role": "spacetime_curvature",
            "note": "graviton is not modeled as confirmed particle here"
        }

    def add_elementary_particle(self, name, particle_family, electric_charge, role):
        self.elementary_particles[name] = {
            "name": name,
            "type": "elementary_particle",
            "family": particle_family,
            "electric_charge": electric_charge,
            "role": role,
            "state": "available",
            "origin": "early_universe_particle_formation"
        }

    def form_nucleons(self):
        self.composite_particles["proton"] = {
            "name": "proton",
            "type": "composite_particle",
            "family": "baryon",
            "state": "formed",
            "composition": ["up_quark", "up_quark", "down_quark"],
            "electric_charge": "+1",
            "future_use": ["atomic_nuclei", "elements"]
        }

        self.composite_particles["neutron"] = {
            "name": "neutron",
            "type": "composite_particle",
            "family": "baryon",
            "state": "formed",
            "composition": ["up_quark", "down_quark", "down_quark"],
            "electric_charge": "0",
            "future_use": ["atomic_nuclei", "isotopes"]
        }

        self.particle_state["protons_formed"] = True
        self.particle_state["neutrons_formed"] = True
        self.particle_state["nucleons_formed"] = True

    def define_interactions(self):
        self.interactions["strong_interaction"] = {
            "name": "strong_interaction",
            "mediator": "gluon",
            "acts_on": ["quarks"],
            "effect": "binds quarks into protons and neutrons"
        }

        self.interactions["electromagnetic_interaction"] = {
            "name": "electromagnetic_interaction",
            "mediator": "photon",
            "acts_on": ["charged_particles"],
            "effect": "relates charged particles and light"
        }

        self.interactions["weak_interaction"] = {
            "name": "weak_interaction",
            "mediators": ["w_boson_minus", "w_boson_plus", "z_boson"],
            "acts_on": ["quarks", "leptons", "neutrinos"],
            "effect": "allows particle transformation and beta decay"
        }

        self.interactions["higgs_mechanism"] = {
            "name": "higgs_mechanism",
            "field": "higgs_field",
            "particle": "higgs_boson",
            "acts_on": ["massive_particles"],
            "effect": "allows particles to acquire mass"
        }

        self.interactions["beta_decay_pattern"] = {
            "name": "beta_decay_pattern",
            "example": "neutron -> proton + electron + electron_antineutrino",
            "interaction": "weak_interaction"
        }

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "particles_formed",
            "description": "Elementary particles, force carriers, the Higgs mechanism, and composite nucleons form after the origin process."
        })

    def write_to_world(self):
        self.universe.world["particles"] = self.public_state
        self.universe.world["elementary_particles"] = self.elementary_particles
        self.universe.world["composite_particles"] = self.composite_particles
        self.universe.world["nucleons"] = {
            "proton": self.composite_particles["proton"],
            "neutron": self.composite_particles["neutron"]
        }
        self.universe.world["particle_fields"] = self.fields
        self.universe.world["particle_interactions"] = self.interactions
        self.universe.world["particle_state"] = self.particle_state
