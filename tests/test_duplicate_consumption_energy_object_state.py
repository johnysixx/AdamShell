import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.duplicate_consumption_energy import (
    DuplicateConsumptionEnergy,
    DuplicateConsumptionEnergyResolvedEvent,
    DuplicateConsumptionEnergyStoredEvent,
)
from cats.duplicate_consumption_energy_state import (
    DuplicateConsumptionEnergyState,
)
from cats.duplicate_consumption_energy_resolution import (
    DuplicateConsumptionEnergyResolution,
)


class DuplicateConsumptionEnergyObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.energy = (
            DuplicateConsumptionEnergy(
                self.universe
            )
        )

        self.cat = self.cats.create_cat(
            name="energy_state_cat",
            color="white",
            fur_length="short",
            origin="test",
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = (
            DuplicateConsumptionEnergyState(
                energy_id="energy_1",
                cat=self.cat.name,
                source="cat_milk",
                day=1,
                amount=1.0,
                energy_kind=(
                    "duplicate_consumption"
                ),
            )
        )

        for name in (
            "get",
            "setdefault",
            "__getitem__",
            "__setitem__",
            "update",
        ):
            self.assertFalse(
                hasattr(
                    state,
                    name,
                )
            )

    def test_store_adds_object_to_queue(
        self
    ):
        state = self.energy.store(
            cat=self.cat,
            source="cat_milk",
            day=1,
            amount=1.25,
        )

        self.assertIsInstance(
            state,
            DuplicateConsumptionEnergyState,
        )

        self.assertIs(
            self.universe
            .pending_cat_consumption_energy[
                0
            ],
            state,
        )

        self.assertEqual(
            state.amount,
            1.25,
        )

        self.assertFalse(
            state.resolved
        )

    def test_resolution_mutates_object_state(
        self
    ):
        state = self.energy.store(
            cat=self.cat,
            source="cat_milk",
            day=1,
        )

        result = (
            self.energy.resolve_next(
                cat_d20_value=1
            )
        )

        self.assertTrue(
            state.resolved
        )

        self.assertEqual(
            state.cat_d20_value,
            1,
        )

        self.assertIs(
            state.resolution,
            DuplicateConsumptionEnergyResolution
            .CRONENBERG_MANIFESTED,
        )

        self.assertEqual(
            result["resolution"],
            "cronenberg_manifested",
        )

        self.assertEqual(
            state.resolved_entity_id,
            result[
                "resolved_entity_id"
            ],
        )

    def test_store_history_uses_object_state(
        self
    ):
        self.energy.store(
            cat=self.cat,
            source="cat_milk",
            day=1,
        )

        event = (
            self.energy.history[-1]
        )

        self.assertIsInstance(
            event,
            DuplicateConsumptionEnergyStoredEvent,
        )

        self.assertEqual(
            event.name,
            (
                "duplicate_consumption_"
                "energy_stored"
            ),
        )

        self.assertEqual(
            event.amount,
            1.0,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["energy_id"]

    def test_resolution_history_uses_object_state(
        self
    ):
        state = self.energy.store(
            cat=self.cat,
            source="cat_milk",
            day=1,
        )

        result = (
            self.energy.resolve_next(
                cat_d20_value=1
            )
        )

        event = (
            self.energy.history[-1]
        )

        self.assertIsInstance(
            event,
            DuplicateConsumptionEnergyResolvedEvent,
        )

        self.assertEqual(
            event.energy_id,
            state.energy_id,
        )

        self.assertEqual(
            event.cat_d20_value,
            1,
        )

        self.assertIs(
            event.resolution,
            DuplicateConsumptionEnergyResolution
            .CRONENBERG_MANIFESTED,
        )

        self.assertEqual(
            result["resolution"],
            "cronenberg_manifested",
        )

        result[
            "resolution"
        ] = "changed"

        self.assertIs(
            event.resolution,
            DuplicateConsumptionEnergyResolution
            .CRONENBERG_MANIFESTED,
        )

        with self.assertRaises(TypeError):
            _ = event["resolution"]

    def test_state_rejects_string_resolution(
        self
    ):
        with self.assertRaises(TypeError):
            DuplicateConsumptionEnergyState(
                energy_id="energy_1",
                cat=self.cat.name,
                source="cat_milk",
                day=1,
                amount=1.0,
                energy_kind="duplicate_consumption",
                resolution="cronenberg_manifested",
            )

        state = DuplicateConsumptionEnergyState(
            energy_id="energy_1",
            cat=self.cat.name,
            source="cat_milk",
            day=1,
            amount=1.0,
            energy_kind="duplicate_consumption",
        )

        with self.assertRaises(TypeError):
            state.resolve(
                resolution="cronenberg_manifested",
                cat_d20_value=1,
            )

    def test_resolved_event_rejects_string_resolution(
        self
    ):
        with self.assertRaises(TypeError):
            DuplicateConsumptionEnergyResolvedEvent(
                energy_id="energy_1",
                cat=self.cat.name,
                source="cat_milk",
                amount=1.0,
                cat_d20_value=1,
                resolution="cronenberg_manifested",
            )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            self.energy._record(
                {
                    "name": (
                        "duplicate_consumption_"
                        "energy_stored"
                    ),
                }
            )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        self.universe            .pending_cat_consumption_energy            .append({
                "name":
                    (
                        "duplicate_consumption_"
                        "energy_stored"
                    ),
                "energy_id":
                    "legacy",
                "cat":
                    self.cat.name,
                "source":
                    "cat_milk",
                "day":
                    1,
                "amount":
                    1.0,
                "energy_kind":
                    "duplicate_consumption",
                "resolved":
                    False,
                "resolution":
                    None,
                "energy_conserved":
                    True,
            })

        with self.assertRaises(
            TypeError
        ):
            self.energy.resolve_next(
                cat_d20_value=1
            )


if __name__ == "__main__":
    unittest.main()
