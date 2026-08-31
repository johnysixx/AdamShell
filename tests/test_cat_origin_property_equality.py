import unittest

from universe.universe import Universe


class CatOriginPropertyEqualityTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.origins = (
            "manual_creation",
            "dice_manifestation",
            "natural_birth",
            "canonical_birth"
        )

        self.cats = [
            self.universe.manifest_cat(
                name=f"cat_{index}",
                source=origin
            )["cat"]
            for index, origin
            in enumerate(
                self.origins,
                start=1
            )
        ]

    def test_origin_does_not_change_core_properties(self):
        required_properties = {
            "type",
            "state",
            "color",
            "pattern",
            "eye_color",
            "fur_length",
            "sex",
            "genotype",
            "reproduction",
            "idea_energy",
            "size",
            "strength",
            "cronenbergs_eaten",
            "cronenberg_mass_eaten",
            "memory",
            "access",
            "special_traits"
        }

        for cat in self.cats:
            with self.subTest(
                origin=cat.origin
            ):
                self.assertTrue(
                    required_properties
                    .issubset(vars(cat))
                )

                self.assertEqual(
                    cat.type,
                    "cat"
                )

                self.assertEqual(
                    cat.idea_energy,
                    100
                )

                self.assertEqual(
                    cat.size,
                    1.0
                )

                self.assertEqual(
                    cat.strength,
                    1.0
                )

    def test_all_origins_have_same_access(self):
        expected_access = {
            "can_access_anywhere": True,
            "access_via": [
                "boxes",
                "cat_doors"
            ]
        }

        for cat in self.cats:
            with self.subTest(
                origin=cat.origin
            ):
                self.assertEqual(
                    cat.access,
                    expected_access
                )

                self.assertTrue(
                    self.universe
                    .cats_layer
                    .can_travel(
                        cat,
                        via="boxes"
                    )
                )

                self.assertTrue(
                    self.universe
                    .cats_layer
                    .can_travel(
                        cat,
                        via="cat_doors"
                    )
                )

    def test_origin_is_metadata_only(self):
        observed_origins = {
            cat.origin
            for cat in self.cats
        }

        self.assertEqual(
            observed_origins,
            set(self.origins)
        )

        shared_property_names = [
            set(vars(cat).keys())
            - {"name", "origin"}
            for cat in self.cats
        ]

        first = shared_property_names[0]

        for properties in shared_property_names[1:]:
            self.assertEqual(
                properties,
                first
            )


if __name__ == "__main__":
    unittest.main()