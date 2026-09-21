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
        universe, process, _ = self._formed_particles()

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

        self.assertIs(
            universe.world["elementary_particles"],
            process.elementary_particles,
        )
        self.assertIs(
            universe.world["composite_particles"],
            process.composite_particles,
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

    def test_world_nucleon_registry_points_to_objects(self):
        universe, process, _ = self._formed_particles()

        nucleons = universe.world["nucleons"]

        self.assertIsInstance(nucleons, dict)
        self.assertIs(
            nucleons["proton"],
            process.composite_particles["proton"],
        )
        self.assertIs(
            nucleons["neutron"],
            process.composite_particles["neutron"],
        )

    def test_public_state_serializes_objects_at_boundary(self):
        _, process, result = self._formed_particles()

        self.assertIsInstance(
            result["elementary_particles"]["up_quark"],
            dict,
        )
        self.assertIsInstance(
            result["composite_particles"]["proton"],
            dict,
        )
        self.assertIsInstance(
            result["fields"]["higgs_field"],
            dict,
        )
        self.assertIsInstance(
            result["interactions"]["strong_interaction"],
            dict,
        )

        result["elementary_particles"]["up_quark"][
            "state"
        ] = "changed"
        result["composite_particles"]["proton"][
            "composition"
        ].append("changed")
        result["interactions"]["strong_interaction"][
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
