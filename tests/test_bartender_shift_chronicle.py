import unittest

from meeting_place.bar_counter import BarCounter
from meeting_place.bartender import Bartender
from meeting_place.how_to_mix_drinks import HowToMixDrinks


class BartenderShiftChronicleTests(unittest.TestCase):

    def test_ejection_incident_is_written_only_at_shift_end(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        incident = {
            "name": "bar_security_incident",
            "category": "access_violation",
            "reason": "unauthorized_area",
            "offender": "guest_1",
            "resolved": True,
            "resolution": "ejected_and_blacklisted"
        }

        bartender.observe_event(
            incident
        )

        self.assertEqual(
            len(
                bar_counter
                .hidden_story_book
                .read_entries()
            ),
            0
        )

        bartender.end_shift()

        entries = (
            bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        chronicle = entries[0]

        self.assertEqual(
            chronicle["type"],
            "bartender_shift_chronicle"
        )

        self.assertEqual(
            chronicle["observer"],
            "bartender"
        )

        self.assertEqual(
            chronicle["perspective"],
            "subjective"
        )

        self.assertEqual(
            len(
                chronicle["events"]
            ),
            1
        )

        event = (
            chronicle["events"][0]
        )

        self.assertEqual(
            event["kind"],
            "ejection"
        )

        self.assertEqual(
            event["subject"],
            "guest_1"
        )

        self.assertEqual(
            event["observed_reason"],
            "unauthorized_area"
        )

        self.assertEqual(
            event["observed_outcome"],
            "ejected"
        )


    def test_ordinary_observed_event_is_written_at_shift_end(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        observed = (
            "guest_1 ordered raspberry_rum"
        )

        bartender.observe_event(
            observed
        )

        self.assertEqual(
            len(
                bar_counter
                .hidden_story_book
                .read_entries()
            ),
            0
        )

        bartender.end_shift()

        entries = (
            bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        chronicle = entries[0]

        self.assertEqual(
            chronicle["type"],
            "bartender_shift_chronicle"
        )

        self.assertEqual(
            chronicle["observer"],
            "bartender"
        )

        self.assertEqual(
            chronicle["perspective"],
            "subjective"
        )

        self.assertEqual(
            len(
                chronicle["events"]
            ),
            1
        )

        event = (
            chronicle["events"][0]
        )

        self.assertEqual(
            event["kind"],
            "ordinary"
        )

        self.assertEqual(
            event["observed_event"],
            observed
        )


    def test_shift_writes_one_chronicle_with_multiple_events(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.observe_event(
            "guest_1 ordered raspberry_rum"
        )

        bartender.observe_event(
            {
                "name": "bar_security_incident",
                "category": "access_violation",
                "reason": "unauthorized_area",
                "offender": "guest_2",
                "resolved": True,
                "resolution": "ejected_and_blacklisted"
            }
        )

        bartender.end_shift()

        entries = (
            bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        chronicle = entries[0]

        self.assertEqual(
            chronicle["type"],
            "bartender_shift_chronicle"
        )

        self.assertEqual(
            len(
                chronicle["events"]
            ),
            2
        )

        self.assertEqual(
            chronicle["events"][0]["kind"],
            "ordinary"
        )

        self.assertEqual(
            chronicle["events"][1]["kind"],
            "ejection"
        )

        self.assertEqual(
            chronicle["events"][1]["subject"],
            "guest_2"
        )


    def test_learned_cocktail_is_written_to_shift_chronicle(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.learn_cocktail(
            drink="event_horizon",
            teacher="newton",
            ingredients=[
                "raspberry_rum",
                "dark_energy"
            ]
        )

        self.assertEqual(
            len(
                bar_counter
                .hidden_story_book
                .read_entries()
            ),
            0
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24
        )

        entries = (
            bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        chronicle = entries[0]

        self.assertEqual(
            chronicle["type"],
            "bartender_shift_chronicle"
        )

        self.assertEqual(
            len(chronicle["events"]),
            1
        )

        event = (
            chronicle["events"][0]
        )

        self.assertEqual(
            event["kind"],
            "learned_cocktail"
        )

        self.assertEqual(
            event["drink"],
            "event_horizon"
        )

        self.assertEqual(
            event["teacher"],
            "newton"
        )

        self.assertEqual(
            event["ingredients"],
            [
                "raspberry_rum",
                "dark_energy"
            ]
        )


    def test_created_cocktail_is_written_to_shift_chronicle(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24
        )

        entries = (
            bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        event = (
            entries[0]["events"][0]
        )

        self.assertEqual(
            event["kind"],
            "created_cocktail"
        )

        self.assertEqual(
            event["drink"],
            "singularity"
        )




    def test_new_drink_is_written_to_shift_chronicle(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.note_new_drink(
            drink="absinthe",
            source="new_bottle"
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24
        )

        entries = (
            bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        event = (
            entries[0]["events"][0]
        )

        self.assertEqual(
            event["kind"],
            "new_drink"
        )

        self.assertEqual(
            event["drink"],
            "absinthe"
        )

        self.assertEqual(
            event["source"],
            "new_bottle"
        )


    def test_new_drink_is_written_to_shift_chronicle(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.note_new_drink(
            drink="absinthe",
            source="new_bottle"
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24
        )

        entries = (
            bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        event = (
            entries[0]["events"][0]
        )

        self.assertEqual(
            event["kind"],
            "new_drink"
        )

        self.assertEqual(
            event["drink"],
            "absinthe"
        )

        self.assertEqual(
            event["source"],
            "new_bottle"
        )


    def test_interesting_guest_is_written_to_shift_chronicle(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.note_interesting_guest(
            guest="newton",
            reason="talked about gravity"
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24
        )

        entries = (
            bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        event = (
            entries[0]["events"][0]
        )

        self.assertEqual(
            event["kind"],
            "interesting_guest"
        )

        self.assertEqual(
            event["guest"],
            "newton"
        )

        self.assertEqual(
            event["reason"],
            "talked about gravity"
        )


    def test_created_cocktail_is_noted_in_bartender_chronicle_memory(
        self
    ):
        bar_counter = BarCounter()
        mix_book = HowToMixDrinks()

        bartender = Bartender(
            bar_counter.hidden_story_book,
            mix_book=mix_book
        )

        bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        self.assertIn(
            {
                "kind": "created_cocktail",
                "drink": "singularity"
            },
            bartender.chronicle_memory
        )

        recipe = mix_book.recipes[
            "singularity"
        ]

        self.assertEqual(
            recipe["ingredients"],
            [
                "raspberry_rum",
                "lemonade"
            ]
        )

if __name__ == "__main__":
    unittest.main()
