import unittest

from meeting_place.bar_counter import (
    BarCounter,
)
from meeting_place.bartender import (
    Bartender,
)
from meeting_place.bartender_chronicle_state import (
    BartenderObservedEventEntry,
    BartenderShiftChronicle,
)
from meeting_place.bartender_event_state import (
    BartenderShiftAlreadyActiveResult,
    BartenderLearnedRequestedDrinkEvent,
    BartenderLeftForLemonEvent,
    BartenderRefusedBetEvent,
    BartenderReturnedWithLemonEvent,
    BartenderShiftStartedEvent,
)


class BartenderEventObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.counter = BarCounter()

        self.bartender = Bartender(
            self.counter.hidden_story_book
        )

    def assert_not_mapping(
        self,
        state,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
        ):
            self.assertFalse(
                hasattr(
                    state,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = state[
                key
            ]

    def test_fixed_bartender_events_are_objects_in_memory(
        self
    ):
        started = (
            self.bartender.begin_shift(
                bar_day=1,
                shift_start_tick=2,
            )
        )

        refused = (
            self.bartender.refuse_bet(
                "serpent"
            )
        )

        learned = (
            self.bartender
            .learn_requested_drink(
                guest_name="lilith",
                drink_name=(
                    "vodka_with_lemon"
                ),
            )
        )

        left = (
            self.bartender
            .leave_for_lemon(
                "lilith"
            )
        )

        returned = (
            self.bartender
            .return_with_lemon(
                "lilith"
            )
        )

        self.assertIs(
            started,
            self.bartender.event_memory[0],
        )
        self.assertIs(
            refused,
            self.bartender.event_memory[1],
        )

        expected_types = (
            BartenderShiftStartedEvent,
            BartenderRefusedBetEvent,
            BartenderLearnedRequestedDrinkEvent,
            BartenderLeftForLemonEvent,
            BartenderReturnedWithLemonEvent,
        )

        for index, returned_event in (
            (0, started),
            (1, refused),
            (2, learned),
            (3, left),
            (4, returned),
        ):
            self.assertIsInstance(
                returned_event,
                expected_types[index],
            )
            self.assertIs(
                returned_event,
                self.bartender.event_memory[index],
            )

        self.assertEqual(
            len(
                self.bartender
                .event_memory
            ),
            len(expected_types),
        )

        for event, expected_type in zip(
            self.bartender.event_memory,
            expected_types,
        ):
            self.assertIsInstance(
                event,
                expected_type,
            )

            self.assert_not_mapping(
                event,
                "name",
            )

        self.assertEqual(
            self.bartender
            .event_memory[1]
            .guest,
            "serpent",
        )

        self.assertFalse(
            self.bartender
            .event_memory[1]
            .accepted
        )

        self.assertEqual(
            self.bartender
            .event_memory[2]
            .drink,
            "vodka_with_lemon",
        )

        self.assertEqual(
            self.bartender
            .event_memory[3]
            .destination,
            "bar_yard",
        )

        self.assertEqual(
            self.bartender
            .event_memory[4]
            .ingredient,
            "lemon",
        )

    def test_second_shift_start_returns_object(
        self
    ):
        self.bartender.begin_shift(
            bar_day=3,
            shift_start_tick=72,
        )

        first_event = (
            self.bartender
            .event_memory[0]
        )

        result = (
            self.bartender.begin_shift(
                bar_day=99,
                shift_start_tick=999,
            )
        )

        self.assertIsInstance(
            result,
            BartenderShiftAlreadyActiveResult,
        )

        self.assertEqual(result.bar_day, 3)
        self.assertEqual(result.shift_start_tick, 72)
        self.assert_not_mapping(result, "bar_day")

        self.assertEqual(
            result.to_dict(),
            {
                "name": "bartender_shift_already_active",
                "bar_day": 3,
                "shift_start_tick": 72,
            },
        )

        self.assertEqual(
            len(
                self.bartender
                .event_memory
            ),
            1,
        )

        self.assertIs(
            self.bartender
            .event_memory[0],
            first_event,
        )

    def test_empty_shift_returns_no_chronicle(self):
        result = self.bartender.end_shift()

        self.assertEqual(result, [])
        self.assertEqual(
            len(
                self.counter.hidden_story_book.read_entries()
            ),
            0,
        )

    def test_shift_boundary_serializes_nested_bartender_event(
        self
    ):
        self.bartender.begin_shift(
            bar_day=1,
            shift_start_tick=0,
        )

        boundary = (
            self.bartender.end_shift(
                bar_day=1,
                shift_start_tick=0,
                shift_end_tick=24,
            )[0]
        )

        chronicle = (
            self.counter
            .hidden_story_book
            .read_entries()[0]
        )

        self.assertIsInstance(
            chronicle,
            BartenderShiftChronicle,
        )

        observed = (
            chronicle.events[0]
        )

        self.assertIsInstance(
            observed,
            BartenderObservedEventEntry,
        )

        self.assertIsInstance(
            observed.observed_event,
            BartenderShiftStartedEvent,
        )

        self.assertIs(boundary, chronicle)
        self.assert_not_mapping(boundary, "events")

        exported = boundary.to_dict()

        self.assertEqual(
            exported["events"][0],
            {
                "kind": "ordinary",
                "observed_event": {
                    "name":
                        "bartender_shift_started",
                    "bar_day": 1,
                    "shift_start_tick": 0,
                },
            },
        )

        self.assertIsInstance(
            chronicle
            .events[0]
            .observed_event,
            BartenderShiftStartedEvent,
        )

        exported["events"][0]["observed_event"][
            "bar_day"
        ] = 999

        self.assertEqual(
            chronicle.events[0].observed_event.bar_day,
            1,
        )

        self.assertEqual(
            chronicle.to_dict()["events"][0][
                "observed_event"
            ]["bar_day"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
