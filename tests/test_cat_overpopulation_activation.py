import unittest

from universe.universe import Universe


class CatOverpopulationActivationTests(
    unittest.TestCase
):

    def test_existing_cat_hunts_below_quota(self):
        universe = Universe()

        created = universe.manifest_cat(
            name="hunter_existing",
            source="test"
        )

        cat = created["cat"]

        result = (
            universe
            .cats_layer
            .activate_for_cronenberg_overpopulation(
                cat,
                hunt_quota=10
            )
        )

        self.assertTrue(
            result["activated"]
        )

        self.assertEqual(
            cat["state"],
            (
                "aware_of_"
                "cronenberg_overpopulation"
            )
        )

        self.assertEqual(
            cat["suggested_intent"],
            "hunt_nearest_cronenberg"
        )

        self.assertNotIn(
            "intent",
            cat
        )

        self.assertNotIn(
            "travel_via",
            cat
        )

        self.assertTrue(
            result["cat_access_unchanged"]
        )

        self.assertTrue(
            universe.cats_layer.can_travel(
                cat,
                "boxes"
            )
        )

        self.assertTrue(
            universe.cats_layer.can_travel(
                cat,
                "cat_doors"
            )
        )

    def test_veteran_cat_returns_to_bar_at_quota(self):
        universe = Universe()

        created = universe.manifest_cat(
            name="hunter_veteran",
            source="test"
        )

        cat = created["cat"]

        cat["cronenbergs_eaten"] = 10

        result = (
            universe
            .cats_layer
            .activate_for_cronenberg_overpopulation(
                cat,
                hunt_quota=10
            )
        )

        self.assertTrue(
            result["activated"]
        )

        self.assertEqual(
            cat["suggested_intent"],
            "return_to_bar"
        )

        self.assertNotIn(
            "intent",
            cat
        )

        self.assertNotIn(
            "travel_via",
            cat
        )

        self.assertEqual(
            cat["hunt_quota"],
            10
        )

        self.assertEqual(
            result["cronenbergs_eaten"],
            10
        )

        self.assertTrue(
            result["cat_access_unchanged"]
        )


if __name__ == "__main__":
    unittest.main()