import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.planet_objects import EarthPlanet, Planet
from universe.planets import Planets
from universe.stellar_system_objects import (
    ProtoplanetaryDisk,
    SecondGenerationStar,
    StellarSystem,
)
from universe.universe import Universe


class PlanetDomainObjectStateTests(unittest.TestCase):

    def _assert_object_only(self, value, key):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(hasattr(value, mapping_method))

        with self.assertRaises(TypeError):
            _ = value[key]

    def _solar_system(self, available_elements):
        elements = tuple(available_elements)
        source_cloud = StellarMaterialCloud(
            name="planet_domain_cloud",
            type="enriched_stellar_cloud",
            state="expanding",
            composition={
                element_name: {}
                for element_name in elements
            },
            can_form_stellar_systems=True,
        )
        return StellarSystem(
            name="solar_system",
            type="stellar_system",
            state="forming",
            generation=2,
            source_cloud=source_cloud,
            star=SecondGenerationStar(
                name="sun",
                type="main_sequence_star",
                state="ignited",
                generation=2,
            ),
            protoplanetary_disk=ProtoplanetaryDisk(
                name="solar_protoplanetary_disk",
                type="protoplanetary_disk",
                state="rotating",
                available_elements=elements,
                can_form_planets=True,
                can_form_water=(
                    "hydrogen" in elements
                    and "oxygen" in elements
                ),
                can_form_iron_cores="iron" in elements,
                can_form_rocky_worlds=(
                    "silicon" in elements
                    and "iron" in elements
                ),
            ),
        )

    def _formed_process(self):
        universe = Universe()
        universe.world["solar_system"] = self._solar_system(
            (
                "hydrogen",
                "carbon",
                "nitrogen",
                "oxygen",
                "magnesium",
                "silicon",
                "calcium",
                "iron",
            )
        )
        process = Planets(universe)
        result = process.form_planets()
        return universe, process, result

    def test_planets_are_domain_objects(self):
        universe, process, _ = self._formed_process()

        self.assertEqual(len(process.planets), 8)
        self.assertTrue(
            all(
                isinstance(planet, Planet)
                for planet in process.planets
            )
        )
        self.assertTrue(
            all(
                not isinstance(planet, dict)
                for planet in process.planets
            )
        )
        self.assertIs(
            universe.world["solar_planets"],
            process.planets,
        )

    def test_planet_is_object_only(self):
        _, process, _ = self._formed_process()
        mercury = process.planets[0]

        self._assert_object_only(mercury, "name")
        self.assertEqual(mercury.name, "mercury")
        self.assertEqual(mercury.orbit, 1)

    def test_earth_is_specialized_planet_object(self):
        universe, process, _ = self._formed_process()
        earth = process.find_planet("earth")

        self.assertIsInstance(earth, EarthPlanet)
        self.assertIsInstance(earth, Planet)
        self.assertIs(universe.world["earth"], earth)
        self._assert_object_only(earth, "water_possible")
        self.assertTrue(earth.has_iron_core)
        self.assertTrue(earth.has_rocky_crust)
        self.assertTrue(earth.water_possible)
        self.assertTrue(earth.organic_molecules_possible)

    def test_earth_capabilities_follow_available_elements(self):
        universe = Universe()
        universe.world["solar_system"] = self._solar_system(
            ("hydrogen",)
        )
        process = Planets(universe)

        process.form_planets()
        earth = process.find_planet("earth")

        self.assertFalse(earth.has_iron_core)
        self.assertFalse(earth.has_rocky_crust)
        self.assertFalse(earth.water_possible)
        self.assertFalse(earth.organic_molecules_possible)

    def test_public_planet_snapshots_remain_dict_boundary(self):
        _, process, result = self._formed_process()

        self.assertIsInstance(result["planets"], list)
        self.assertTrue(
            all(
                isinstance(planet, dict)
                for planet in result["planets"]
            )
        )
        self.assertEqual(result["planets"][2]["name"], "earth")
        self.assertTrue(result["planets"][2]["water_possible"])

        result["planets"][2]["name"] = "fake_earth"
        self.assertEqual(process.planets[2].name, "earth")

    def test_to_dict_is_detached_boundary(self):
        earth = EarthPlanet(
            name="earth",
            type="rocky_planet",
            state="formed",
            orbit=3,
            has_iron_core=True,
            has_rocky_crust=True,
            water_possible=True,
            organic_molecules_possible=True,
        )

        snapshot = earth.to_dict()
        snapshot["name"] = "fake_earth"
        snapshot["water_possible"] = False

        self.assertEqual(earth.name, "earth")
        self.assertTrue(earth.water_possible)

    def test_planet_validation_rejects_invalid_orbit(self):
        with self.assertRaises(TypeError):
            Planet(
                name="broken",
                type="rocky_planet",
                state="formed",
                orbit="one",
            )

        with self.assertRaises(ValueError):
            Planet(
                name="broken",
                type="rocky_planet",
                state="formed",
                orbit=0,
            )


if __name__ == "__main__":
    unittest.main()
