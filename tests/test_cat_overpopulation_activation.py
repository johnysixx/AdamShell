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
            cat.state,
            (
                "aware_of_"
                "cronenberg_overpopulation"
            )
        )

        self.assertEqual(
            cat.suggested_intent,
            "hunt_nearest_cronenberg"
        )

        self.assertFalse(hasattr(cat, 'intent'))

        self.assertFalse(hasattr(cat, 'travel_via'))

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

    def test_cat_can_accept_navigation_offer(self):
        universe = Universe()

        created = universe.manifest_cat(
            name="accepting_cat",
            source="test",
            position={
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        cat = created["cat"]

        universe.cats_layer.activate_for_cronenberg_overpopulation(
            cat
        )

        target = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("target"),
                "test",
                "accept_navigation"
            )
        )

        target.position = {
            "x": 3.0,
            "y": 0.0,
            "z": 0.0
        }

        universe.cats_layer.offer_navigation_for_suggested_intent(
            cat
        )

        result = (
            universe
            .cats_layer
            .accept_navigation_offer(
                cat
            )
        )

        self.assertTrue(
            result["accepted"]
        )

        self.assertEqual(
            cat.intent,
            "hunt_nearest_cronenberg"
        )

        self.assertEqual(
            cat.active_route_id,
            result["route"].route_id
        )

        self.assertEqual(
            result["route"].state,
            "ready"
        )

        self.assertTrue(
            cat.navigation_offer[
                "accepted"
            ]
        )

    def test_cat_can_decline_navigation_offer(self):
        universe = Universe()

        created = universe.manifest_cat(
            name="declining_cat",
            source="test",
            position={
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        cat = created["cat"]

        universe.cats_layer.activate_for_cronenberg_overpopulation(
            cat
        )

        target = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("target"),
                "test",
                "decline_navigation"
            )
        )

        target.position = {
            "x": 3.0,
            "y": 0.0,
            "z": 0.0
        }

        universe.cats_layer.offer_navigation_for_suggested_intent(
            cat
        )

        result = (
            universe
            .cats_layer
            .decline_navigation_offer(
                cat
            )
        )

        self.assertTrue(
            result["declined"]
        )

        self.assertFalse(hasattr(cat, 'intent'))

        self.assertFalse(hasattr(cat, 'active_route_id'))

        self.assertFalse(
            result["route"].observation_active
        )

        self.assertEqual(
            result["route"].state,
            "released"
        )

        self.assertTrue(
            cat.navigation_offer[
                "declined"
            ]
        )

    def test_veteran_cat_returns_to_bar_at_quota(self):
        universe = Universe()

        created = universe.manifest_cat(
            name="hunter_veteran",
            source="test"
        )

        cat = created["cat"]

        cat.cronenbergs_eaten = 10

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
            cat.suggested_intent,
            "return_to_bar"
        )

        self.assertFalse(hasattr(cat, 'intent'))

        self.assertFalse(hasattr(cat, 'travel_via'))

        self.assertEqual(
            cat.hunt_quota,
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