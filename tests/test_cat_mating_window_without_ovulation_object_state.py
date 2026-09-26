import unittest

from cats import Cats
from cats.mating_contact import (
    CatMatingWindowClosedWithoutOvulationEvent,
)
from cats.mating_resolver import (
    CatMatingResolver,
)
from cats.ovulation_resolver import (
    CatInducedOvulationResolvedEvent,
)
from universe.universe import Universe


class CatMatingWindowWithoutOvulationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.start_big_bang()

        self.cats = Cats(
            self.universe
        )

        self.female = (
            self.cats.create_cat(
                name="mother",
                color="black",
                fur_length="short",
                sex="female",
            )
        )

        self.male = (
            self.cats.create_cat(
                name="father",
                color="orange",
                fur_length="long",
                sex="male",
            )
        )

        self.female.reproduction.ovulation_threshold = 4
        self.female.reproduction.estrus_active = True
        self.female.reproduction.estrous_phase = "estrus"

        self.resolver = (
            CatMatingResolver(
                self.universe
            )
        )

        self.resolver.mate(
            self.female,
            self.male,
            current_day=10,
        )

    def test_history_uses_object_state_and_reuses_ovulation_event(
        self
    ):
        result = (
            self.resolver
            .close_mating_window(
                self.female,
                current_day=11,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        ovulation_event = (
            self.resolver
            .ovulation_resolver
            .history[-1]
        )

        self.assertIsInstance(
            event,
            CatMatingWindowClosedWithoutOvulationEvent,
        )

        self.assertIsInstance(
            ovulation_event,
            CatInducedOvulationResolvedEvent,
        )

        self.assertIs(
            event.ovulation,
            ovulation_event,
        )

        self.assertFalse(
            event.ovulation_induced
        )

        self.assertFalse(
            event.pregnancy_started
        )

        self.assertEqual(
            event.mating_contact_count,
            1,
        )

        self.assertEqual(
            result,
            event.to_dict(),
        )

    def test_event_and_nested_ovulation_have_no_mapping_api(
        self
    ):
        self.resolver.close_mating_window(
            self.female,
            current_day=11,
        )

        event = (
            self.resolver
            .history[-1]
        )

        for obj in (
            event,
            event.ovulation,
        ):
            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
            ):
                self.assertFalse(
                    hasattr(
                        obj,
                        mapping_method,
                    )
                )

            with self.assertRaises(
                TypeError
            ):
                _ = obj["name"]

    def test_boundary_is_detached_from_nested_ovulation_event(
        self
    ):
        result = (
            self.resolver
            .close_mating_window(
                self.female,
                current_day=11,
            )
        )

        event = (
            self.resolver
            .history[-1]
        )

        result[
            "ovulation"
        ][
            "reason"
        ] = "changed"

        self.assertEqual(
            event.ovulation.reason,
            "insufficient_stimulation",
        )

        self.assertFalse(
            self.female
            .reproduction
            .mating_window_open
        )

        self.assertEqual(
            self.female
            .reproduction
            .mating_contacts,
            [],
        )

    def test_event_rejects_mapping_ovulation(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            CatMatingWindowClosedWithoutOvulationEvent(
                mother="mother",
                mating_contact_count=1,
                ovulation={
                    "ovulation_induced": False,
                },
            )


if __name__ == "__main__":
    unittest.main()
