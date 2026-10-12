import unittest

from meeting_place.bar_counter import BarCounter
from meeting_place.bar_incident_state import (
    BarIncidentState,
)
from meeting_place.bartender import Bartender
from meeting_place.bartender_chronicle_state import (
    BartenderCreatedCocktailEntry,
    BartenderInterestingGuestEntry,
    BartenderLearnedCocktailEntry,
    BartenderNewDrinkEntry,
    BartenderObservedEjectionEntry,
    BartenderObservedEventEntry,
    BartenderShiftChronicle,
)
from meeting_place.how_to_mix_drinks import (
    HowToMixDrinks,
)


class BartenderShiftChronicleTests(
    unittest.TestCase
):

    def _ejection(
        self,
        offender,
    ):
        incident = BarIncidentState(
            category='access_violation',
            reason='unauthorized_area',
            offender=offender,
        )

        incident.resolve(
            'ejected_and_blacklisted'
        )

        return incident

    def test_ejection_incident_is_written_only_at_shift_end(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.observe_event(
            self._ejection(
                'guest_1'
            )
        )

        self.assertEqual(
            len(
                bar_counter
                .hidden_story_book
                .read_entries()
            ),
            0,
        )

        bartender.end_shift()

        chronicle = (
            bar_counter
            .hidden_story_book
            .read_entries()[0]
        )

        self.assertIsInstance(
            chronicle,
            BartenderShiftChronicle,
        )

        self.assertEqual(
            chronicle.type,
            'bartender_shift_chronicle',
        )

        self.assertEqual(
            chronicle.observer,
            'bartender',
        )

        self.assertEqual(
            chronicle.perspective,
            'subjective',
        )

        event = chronicle.events[0]

        self.assertIsInstance(
            event,
            BartenderObservedEjectionEntry,
        )

        self.assertEqual(
            event.subject,
            'guest_1',
        )

        self.assertEqual(
            event.observed_reason,
            'unauthorized_area',
        )

        self.assertEqual(
            event.observed_outcome,
            'ejected',
        )

    def test_ordinary_observed_event_is_written_at_shift_end(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        observed = (
            'guest_1 ordered raspberry_rum'
        )

        bartender.observe_event(
            observed
        )

        bartender.end_shift()

        chronicle = (
            bar_counter
            .hidden_story_book
            .read_entries()[0]
        )

        event = chronicle.events[0]

        self.assertIsInstance(
            event,
            BartenderObservedEventEntry,
        )

        self.assertEqual(
            event.observed_event,
            observed,
        )

    def test_shift_writes_one_chronicle_with_multiple_events(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.observe_event(
            'guest_1 ordered raspberry_rum'
        )

        bartender.observe_event(
            self._ejection(
                'guest_2'
            )
        )

        bartender.end_shift()

        chronicle = (
            bar_counter
            .hidden_story_book
            .read_entries()[0]
        )

        self.assertEqual(
            len(
                chronicle.events
            ),
            2,
        )

        self.assertIsInstance(
            chronicle.events[0],
            BartenderObservedEventEntry,
        )

        self.assertIsInstance(
            chronicle.events[1],
            BartenderObservedEjectionEntry,
        )

        self.assertEqual(
            chronicle.events[1].subject,
            'guest_2',
        )

    def test_learned_cocktail_is_written_to_shift_chronicle(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.learn_cocktail(
            drink='event_horizon',
            teacher='newton',
            ingredients=[
                'raspberry_rum',
                'dark_energy',
            ],
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24,
        )

        chronicle = (
            bar_counter
            .hidden_story_book
            .read_entries()[0]
        )

        event = chronicle.events[0]

        self.assertIsInstance(
            event,
            BartenderLearnedCocktailEntry,
        )

        self.assertEqual(
            event.drink,
            'event_horizon',
        )

        self.assertEqual(
            event.teacher,
            'newton',
        )

        self.assertEqual(
            event.ingredients,
            (
                'raspberry_rum',
                'dark_energy',
            ),
        )

    def test_created_cocktail_is_written_to_shift_chronicle(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.create_cocktail(
            drink='singularity',
            ingredients=[
                'raspberry_rum',
                'lemonade',
            ],
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24,
        )

        event = (
            bar_counter
            .hidden_story_book
            .read_entries()[0]
            .events[0]
        )

        self.assertIsInstance(
            event,
            BartenderCreatedCocktailEntry,
        )

        self.assertEqual(
            event.drink,
            'singularity',
        )

    def test_new_drink_is_written_to_shift_chronicle(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.note_new_drink(
            drink='absinthe',
            source='new_bottle',
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24,
        )

        event = (
            bar_counter
            .hidden_story_book
            .read_entries()[0]
            .events[0]
        )

        self.assertIsInstance(
            event,
            BartenderNewDrinkEntry,
        )

        self.assertEqual(
            event.drink,
            'absinthe',
        )

        self.assertEqual(
            event.source,
            'new_bottle',
        )

    def test_interesting_guest_is_written_to_shift_chronicle(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.note_interesting_guest(
            guest='newton',
            reason='talked about gravity',
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24,
        )

        event = (
            bar_counter
            .hidden_story_book
            .read_entries()[0]
            .events[0]
        )

        self.assertIsInstance(
            event,
            BartenderInterestingGuestEntry,
        )

        self.assertEqual(
            event.guest,
            'newton',
        )

        self.assertEqual(
            event.reason,
            'talked about gravity',
        )

    def test_created_cocktail_is_noted_in_bartender_chronicle_memory(
        self
    ):
        bar_counter = BarCounter()
        mix_book = HowToMixDrinks()

        bartender = Bartender(
            bar_counter.hidden_story_book,
            mix_book=mix_book,
        )

        bartender.create_cocktail(
            drink='singularity',
            ingredients=[
                'raspberry_rum',
                'lemonade',
            ],
        )

        entry = (
            bartender
            .chronicle_memory[-1]
        )

        self.assertIsInstance(
            entry,
            BartenderCreatedCocktailEntry,
        )

        self.assertEqual(
            entry.drink,
            'singularity',
        )

        recipe = mix_book.recipes[
            'singularity'
        ]

        self.assertEqual(
            recipe.ingredients,
            [
                'raspberry_rum',
                'lemonade',
            ],
        )

    def test_chronicle_state_has_no_mapping_api(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        bartender.note_new_drink(
            drink='absinthe',
            source='new_bottle',
        )

        entry = (
            bartender
            .chronicle_memory[-1]
        )

        bartender.end_shift(
            bar_day=1,
            shift_start_tick=0,
            shift_end_tick=24,
        )

        chronicle = (
            bar_counter
            .hidden_story_book
            .read_entries()[0]
        )

        for state in (
            entry,
            chronicle,
            chronicle.events[0],
        ):
            for mapping_method in (
                'get',
                'keys',
                'items',
                'values',
                'setdefault',
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
                    'kind'
                ]


if __name__ == '__main__':
    unittest.main()
