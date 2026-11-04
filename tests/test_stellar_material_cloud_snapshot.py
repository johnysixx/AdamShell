import unittest

from universe.cosmic_objects import StellarMaterialCloud


class MutableComponent:

    def __init__(self):
        self.values = {
            "values": ["original"],
        }

    def to_dict(self):
        return {
            "nested": self.values,
        }


class StellarMaterialCloudSnapshotTests(
    unittest.TestCase
):

    def make_cloud(self, composition):
        return StellarMaterialCloud(
            name="snapshot_cloud",
            type="germinal_cloud",
            state="condensing",
            composition=composition,
            can_form_stars=True,
        )

    def test_serialized_component_detaches_nested_state(self):
        component = MutableComponent()

        cloud = self.make_cloud({
            "hydrogen": component,
        })

        self.assertIs(
            cloud.composition["hydrogen"],
            component,
        )

        first = cloud.to_dict()
        second = cloud.to_dict()

        first["composition"]["hydrogen"][
            "nested"
        ]["values"].append("snapshot_only")

        self.assertEqual(
            component.values["values"],
            ["original"],
        )

        self.assertEqual(
            second["composition"]["hydrogen"][
                "nested"
            ]["values"],
            ["original"],
        )

        self.assertEqual(
            cloud.to_dict()["composition"][
                "hydrogen"
            ]["nested"]["values"],
            ["original"],
        )

        self.assertIs(
            cloud.composition["hydrogen"],
            component,
        )

    def test_shared_component_snapshots_are_independent(self):
        component = MutableComponent()

        cloud = self.make_cloud({
            "hydrogen": component,
            "helium": component,
        })

        snapshot = cloud.to_dict()

        snapshot["composition"]["hydrogen"][
            "nested"
        ]["values"].append("hydrogen_only")

        self.assertEqual(
            snapshot["composition"]["hydrogen"][
                "nested"
            ]["values"],
            ["original", "hydrogen_only"],
        )

        self.assertEqual(
            snapshot["composition"]["helium"][
                "nested"
            ]["values"],
            ["original"],
        )

        self.assertEqual(
            component.values["values"],
            ["original"],
        )

        self.assertIs(
            cloud.composition["hydrogen"],
            cloud.composition["helium"],
        )

        self.assertIs(
            cloud.composition["hydrogen"],
            component,
        )

    def test_plain_mapping_component_is_also_detached(self):
        component = {
            "details": {
                "tags": ["original"],
            },
        }

        cloud = self.make_cloud({
            "hydrogen": component,
        })

        first = cloud.to_dict()
        second = cloud.to_dict()

        first["composition"]["hydrogen"][
            "details"
        ]["tags"].append("snapshot_only")

        self.assertEqual(
            component["details"]["tags"],
            ["original"],
        )

        self.assertEqual(
            second["composition"]["hydrogen"][
                "details"
            ]["tags"],
            ["original"],
        )

        self.assertIs(
            cloud.composition["hydrogen"],
            component,
        )

        with self.assertRaises(TypeError):
            cloud.composition["helium"] = component


if __name__ == "__main__":
    unittest.main()
