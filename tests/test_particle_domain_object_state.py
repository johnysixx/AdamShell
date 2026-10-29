import unittest

from universe.particle_objects import (
    CompositeParticle,
    ElementaryParticle,
    ParticleField,
    ParticleInteraction,
)
from universe.particles import Particles
from universe.universe import Universe


class ParticleDomainObjectStateTests(unittest.TestCase):

    def _assert_object_only(self, value, key):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def _formed_particles(self):
        universe = Universe()
        universe.start_big_bang()
        process = Particles(universe)
        result = process.form_particles()

        return universe, process, result

    def test_particle_registries_store_domain_objects(self):
        universe, process, result = self._formed_particles()

        self.assertIsInstance(
            process.elementary_particles["up_quark"],
            ElementaryParticle,
        )
        self.assertIsInstance(
            process.composite_particles["proton"],
            CompositeParticle,
        )
        self.assertIsInstance(
            process.fields["higgs_field"],
            ParticleField,
        )
        self.assertIsInstance(
            process.interactions["strong_interaction"],
            ParticleInteraction,
        )

        self.assertNotIn(
            "elementary_particles",
            universe.world,
        )

        self.assertEqual(
            len(process.elementary_particles),
            18,
        )
        self.assertEqual(
            len(result.elementary_particles),
            18,
        )

        public_elements = universe.world[
            "particles"
        ]["elementary_particles"]

        self.assertEqual(
            len(public_elements),
            18,
        )

        for name, particle in process.elementary_particles.items():
            with self.subTest(particle=name):
                self.assertIsInstance(
                    particle,
                    ElementaryParticle,
                )
                self.assertIs(
                    result.elementary_particles[name],
                    particle,
                )
                self.assertEqual(
                    public_elements[name],
                    particle.to_dict(),
                )
        self.assertNotIn(
            "composite_particles",
            universe.world,
        )
        self.assertIs(
            result.composite_particles["proton"],
            process.composite_particles["proton"],
        )
        self.assertIs(
            result.composite_particles["neutron"],
            process.composite_particles["neutron"],
        )
        self.assertIs(
            universe.world["particle_fields"],
            process.fields,
        )
        self.assertIs(
            universe.world["particle_interactions"],
            process.interactions,
        )

    def test_domain_entities_do_not_support_mapping_access(self):
        _, process, _ = self._formed_particles()

        self._assert_object_only(
            process.elementary_particles["electron"],
            "state",
        )
        self._assert_object_only(
            process.composite_particles["neutron"],
            "composition",
        )
        self._assert_object_only(
            process.fields["gravity_field"],
            "role",
        )
        self._assert_object_only(
            process.interactions["weak_interaction"],
            "effect",
        )

    def test_particle_values_are_read_through_attributes(self):
        _, process, _ = self._formed_particles()

        up_quark = process.elementary_particles["up_quark"]
        proton = process.composite_particles["proton"]
        higgs_field = process.fields["higgs_field"]
        weak = process.interactions["weak_interaction"]

        self.assertEqual(up_quark.family, "quark")
        self.assertEqual(up_quark.electric_charge, "+2/3")
        self.assertEqual(
            proton.composition,
            ("up_quark", "up_quark", "down_quark"),
        )
        self.assertEqual(
            higgs_field.related_particle,
            "higgs_boson",
        )
        self.assertEqual(
            weak.mediators,
            (
                "w_boson_minus",
                "w_boson_plus",
                "z_boson",
            ),
        )

    def test_nucleons_use_canonical_composite_particle_objects(self):
        universe, process, result = (
            self._formed_particles()
        )

        self.assertNotIn(
            "nucleons",
            universe.world,
        )

        self.assertEqual(
            set(process.composite_particles),
            {"proton", "neutron"},
        )

        proton = process.composite_particles["proton"]
        neutron = process.composite_particles["neutron"]

        self.assertIsInstance(
            proton,
            CompositeParticle,
        )
        self.assertIsInstance(
            neutron,
            CompositeParticle,
        )

        self.assertIs(
            result.composite_particles["proton"],
            proton,
        )
        self.assertIs(
            result.composite_particles["neutron"],
            neutron,
        )

        self.assertEqual(
            proton.composition,
            ("up_quark", "up_quark", "down_quark"),
        )
        self.assertEqual(
            neutron.composition,
            ("up_quark", "down_quark", "down_quark"),
        )

        self.assertEqual(
            proton.electric_charge,
            "+1",
        )
        self.assertEqual(
            neutron.electric_charge,
            "0",
        )

        public_composites = universe.world[
            "particles"
        ]["composite_particles"]

        self.assertIsInstance(
            public_composites["proton"],
            dict,
        )
        self.assertIsInstance(
            public_composites["neutron"],
            dict,
        )

        self.assertEqual(
            public_composites["proton"]["composition"],
            list(proton.composition),
        )
        self.assertEqual(
            public_composites["neutron"]["composition"],
            list(neutron.composition),
        )

        public_composites[
            "proton"
        ]["composition"].append("changed")

        self.assertNotIn(
            "changed",
            proton.composition,
        )
        self.assertNotIn(
            "changed",
            result.composite_particles[
                "proton"
            ].composition,
        )

    def test_public_state_serializes_objects_at_boundary(self):
        _, process, result = self._formed_particles()

        self.assertIs(
            result.elementary_particles[
                "up_quark"
            ],
            process.elementary_particles[
                "up_quark"
            ],
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot[
                "elementary_particles"
            ]["up_quark"],
            dict,
        )
        self.assertIsInstance(
            snapshot[
                "composite_particles"
            ]["proton"],
            dict,
        )
        self.assertIsInstance(
            snapshot["fields"]["higgs_field"],
            dict,
        )
        self.assertIsInstance(
            snapshot[
                "interactions"
            ]["strong_interaction"],
            dict,
        )

        snapshot[
            "elementary_particles"
        ]["up_quark"]["state"] = "changed"
        snapshot[
            "composite_particles"
        ]["proton"]["composition"].append(
            "changed"
        )
        snapshot[
            "interactions"
        ]["strong_interaction"][
            "effect"
        ] = "changed"

        self.assertEqual(
            process.elementary_particles["up_quark"].state,
            "available",
        )
        self.assertNotIn(
            "changed",
            process.composite_particles["proton"].composition,
        )
        self.assertNotEqual(
            process.interactions["strong_interaction"].effect,
            "changed",
        )

    def test_to_dict_returns_detached_sequence_values(self):
        particle = CompositeParticle(
            name="proton",
            type="composite_particle",
            family="baryon",
            state="formed",
            composition=(
                "up_quark",
                "up_quark",
                "down_quark",
            ),
            electric_charge="+1",
            future_use=("atomic_nuclei", "elements"),
        )

        snapshot = particle.to_dict()
        snapshot["composition"].append("changed")
        snapshot["future_use"].append("changed")

        self.assertNotIn("changed", particle.composition)
        self.assertNotIn("changed", particle.future_use)


if __name__ == "__main__":
    unittest.main()
