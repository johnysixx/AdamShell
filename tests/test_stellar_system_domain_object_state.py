import unittest

from universe.cosmic_objects import StellarMaterialCloud
from universe.stellar_system_objects import (
    ProtoplanetaryDisk,
    SecondGenerationStar,
    StellarSystem,
)


class StellarSystemDomainObjectStateTests(unittest.TestCase):

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

    def _objects(self):
        cloud = StellarMaterialCloud(
            name="object_test_cloud",
            type="enriched_stellar_cloud",
            state="expanding",
            composition={
                "hydrogen": {},
                "oxygen": {},
                "silicon": {},
                "iron": {},
            },
            can_form_stellar_systems=True,
        )
        star = SecondGenerationStar(
            name="object_test_star",
            type="main_sequence_star",
            state="ignited",
            generation=2,
        )
        disk = ProtoplanetaryDisk(
            name="object_test_disk",
            type="protoplanetary_disk",
            state="rotating",
            available_elements=(
                "hydrogen",
                "oxygen",
                "silicon",
                "iron",
            ),
            can_form_planets=True,
            can_form_water=True,
            can_form_iron_cores=True,
            can_form_rocky_worlds=True,
        )
        system = StellarSystem(
            name="object_test_system",
            type="stellar_system",
            state="forming",
            generation=2,
            source_cloud=cloud,
            star=star,
            protoplanetary_disk=disk,
        )
        return cloud, star, disk, system

    def test_system_and_nested_entities_are_object_only(self):
        _, star, disk, system = self._objects()

        self._assert_object_only(system, "name")
        self._assert_object_only(star, "name")
        self._assert_object_only(disk, "name")

    def test_system_keeps_object_identity(self):
        cloud, star, disk, system = self._objects()

        self.assertIs(system.source_cloud, cloud)
        self.assertIs(system.star, star)
        self.assertIs(system.protoplanetary_disk, disk)
        self.assertEqual(system.formed_from, cloud.name)

    def test_available_elements_are_immutable(self):
        _, _, disk, _ = self._objects()

        self.assertIsInstance(disk.available_elements, tuple)
        self.assertTrue(disk.has_element("iron"))
        with self.assertRaises(AttributeError):
            disk.available_elements.append("gold")

    def test_legacy_nested_dicts_are_rejected(self):
        cloud, star, disk, _ = self._objects()

        with self.assertRaises(TypeError):
            StellarSystem(
                name="legacy_star_system",
                type="stellar_system",
                state="forming",
                generation=2,
                source_cloud=cloud,
                star={"name": "legacy_star"},
                protoplanetary_disk=disk,
            )

        with self.assertRaises(TypeError):
            StellarSystem(
                name="legacy_disk_system",
                type="stellar_system",
                state="forming",
                generation=2,
                source_cloud=cloud,
                star=star,
                protoplanetary_disk={"name": "legacy_disk"},
            )

        with self.assertRaises(TypeError):
            StellarSystem(
                name="legacy_cloud_system",
                type="stellar_system",
                state="forming",
                generation=2,
                source_cloud={"name": "legacy_cloud"},
                star=star,
                protoplanetary_disk=disk,
            )

    def test_to_dict_is_deeply_detached(self):
        _, _, disk, system = self._objects()

        snapshot = system.to_dict()
        snapshot["star"]["name"] = "fake_star"
        snapshot["protoplanetary_disk"][
            "available_elements"
        ].append("fake")

        self.assertEqual(system.star.name, "object_test_star")
        self.assertNotIn("fake", disk.available_elements)


if __name__ == "__main__":
    unittest.main()
