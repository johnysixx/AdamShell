import unittest

from universe.atomic_nuclei import AtomicNuclei
from universe.atomic_time import AtomicTime
from universe.atoms import Atoms
from universe.big_bang import BigBang
from universe.biochemical_foundations import BiochemicalFoundations
from universe.cosmic_clouds import CosmicClouds
from universe.heavy_element_nucleosynthesis import (
    HeavyElementNucleosynthesis,
)
from universe.isotopes import Isotopes
from universe.molecules import Molecules
from universe.particles import Particles
from universe.physical_record_state import (
    AtomicTimeStandard,
    CosmicHistoryEvent,
    RadioactiveDecayPattern,
)
from universe.planetary_materials import PlanetaryMaterials
from universe.planets import Planets
from universe.radioactive_decay import RadioactiveDecay
from universe.stars import Stars
from universe.stellar_nucleosynthesis import StellarNucleosynthesis
from universe.stellar_systems import StellarSystems
from universe.supernova_enrichment import SupernovaEnrichment
from universe.universe import Universe


class UniversePhysicalRecordObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def test_big_bang_phases_use_cosmic_history_events(
        self,
    ):
        universe = Universe()
        result = universe.start_big_bang()

        phase = universe.big_bang.phases[0]

        self.assertIsInstance(
            phase,
            CosmicHistoryEvent,
        )
        self.assertIs(
            universe.world["cosmic_history"][0],
            phase,
        )
        self.assertEqual(
            phase.name,
            "primordial_void",
        )
        self.assertIs(
            result.phases[0],
            phase,
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot["phases"][0],
            dict,
        )

        self._assert_object_only(
            phase,
            "name",
        )

    def test_process_history_writers_use_common_event_object(
        self,
    ):
        process_types = (
            AtomicNuclei,
            AtomicTime,
            Atoms,
            BiochemicalFoundations,
            CosmicClouds,
            HeavyElementNucleosynthesis,
            Isotopes,
            Molecules,
            Particles,
            PlanetaryMaterials,
            Planets,
            RadioactiveDecay,
            Stars,
            StellarNucleosynthesis,
            StellarSystems,
            SupernovaEnrichment,
        )

        for process_type in process_types:
            with self.subTest(
                process=process_type.__name__,
            ):
                universe = Universe()
                process = process_type(
                    universe
                )
                process.record_history()

                event = universe.world[
                    "cosmic_history"
                ][-1]

                self.assertIsInstance(
                    event,
                    CosmicHistoryEvent,
                )
                self._assert_object_only(
                    event,
                    "name",
                )

    def test_atomic_time_registry_uses_value_object(
        self,
    ):
        universe = Universe()
        process = AtomicTime(universe)
        result = process.define_si_second()

        standard = process.time_standards[
            "si_second"
        ]

        self.assertIsInstance(
            standard,
            AtomicTimeStandard,
        )
        self.assertIs(
            universe.world["time_standards"][
                "si_second"
            ],
            standard,
        )
        self.assertEqual(
            standard.frequency_hz,
            9_192_631_770,
        )
        self.assertIsInstance(
            result["time_standards"][
                "si_second"
            ],
            dict,
        )
        self._assert_object_only(
            standard,
            "frequency_hz",
        )

    def test_decay_registry_uses_value_objects(
        self,
    ):
        universe = Universe()
        process = RadioactiveDecay(universe)
        result = process.define_reference_decay()

        pattern = process.decay_patterns[
            "carbon_14_decay"
        ]

        self.assertIsInstance(
            pattern,
            RadioactiveDecayPattern,
        )
        self.assertIs(
            universe.world["decay_patterns"][
                "carbon_14_decay"
            ],
            pattern,
        )
        self.assertEqual(
            pattern.state,
            "available",
        )
        self.assertIsInstance(
            result["decay_patterns"][
                "carbon_14_decay"
            ],
            dict,
        )
        self._assert_object_only(
            pattern,
            "state",
        )


if __name__ == "__main__":
    unittest.main()
