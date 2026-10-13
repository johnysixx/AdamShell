import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from meeting_place.bar_objects import (
    CatD20GarfieldTargetPreparedEvent,
)
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import Day0FirstBarShift

class Day0GarfieldArrivalTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)
        self.scene = Day0FirstBarShift(universe=self.universe, meeting_place=self.bar, library=Library(self.universe), gods=Gods(self.universe), idea_entities=IdeaEntities(self.universe))

    def _name(self, cat):
        if isinstance(cat, dict):
            return getattr(cat, 'name', None)
        return getattr(cat, 'name', None)

    def test_all_three_competitors_accept_panel(self):
        result = self.scene.advance_to_garfield_arrival()
        self.assertEqual(result.accepted.accepted_by, ('lilith', 'god', 'serpent'))

    def test_bartender_suggests_inviting_bouncer(self):
        result = self.scene.advance_to_garfield_arrival()
        self.assertEqual(result.invite.invite, 'bouncer')
        self.assertFalse(result.invite.bouncer_entered)

    def test_everyone_present_scratches_cat_d20(self):
        result = self.scene.advance_to_garfield_arrival()
        scratchers = [event.scratched_by for event in result.scratches]
        self.assertEqual(scratchers, [
                'serpent',
                'lilith',
                'god',
                'bartender'
            ])

    def test_cat_d20_sets_garfield_target(self):
        result = self.scene.advance_to_garfield_arrival()

        self.assertEqual(
            result.prepared.target_name,
            'garfield'
        )

        self.assertEqual(
            self.scene
            .cat_d20
            .cat_d20
            .last_manifested_target,
            'garfield'
        )

        history_event = next(
            event
            for event
            in self.scene.history
            if isinstance(
                event,
                CatD20GarfieldTargetPreparedEvent,
            )
        )

        secret_event = next(
            event
            for event
            in self.bar.cat_d20_secret_history
            if isinstance(
                event,
                CatD20GarfieldTargetPreparedEvent,
            )
        )

        quantum_event = next(
            event
            for event
            in self.universe.quantum_events
            if isinstance(
                event,
                CatD20GarfieldTargetPreparedEvent,
            )
        )

        for event in (
            history_event,
            secret_event,
            quantum_event,
        ):
            self.assertEqual(
                event.target_name,
                'garfield'
            )

            self.assertTrue(
                event.pending
            )

            self.assertEqual(
                event.profile.color,
                'orange'
            )

            for mapping_method in (
                'get',
                'keys',
                'items',
                'values',
            ):
                self.assertFalse(
                    hasattr(
                        event,
                        mapping_method,
                    )
                )

            with self.assertRaises(
                TypeError
            ):
                _ = event['target_name']

        self.assertIsNot(
            history_event,
            secret_event,
        )

        self.assertIsNot(
            secret_event,
            quantum_event,
        )

        returned_event = result.prepared

        returned_event.profile.color = (
            'changed'
        )

        self.assertEqual(
            history_event.profile.color,
            'orange'
        )

        self.assertIsNot(
            returned_event,
            history_event,
        )

    def test_garfield_arrives(self):
        result = self.scene.advance_to_garfield_arrival()
        garfield = result.garfield.garfield
        self.assertEqual(self._name(garfield), 'garfield')
        self.assertIs(self.scene.garfield, garfield)
        self.assertIn(garfield, self.bar.entities)

    def test_garfield_uses_real_garfield_profile(self):
        result = self.scene.advance_to_garfield_arrival()
        prepared = result.prepared.profile
        manifested = result.garfield.profile
        self.assertEqual(prepared, manifested)

    def test_scratching_precedes_garfield_setting_and_arrival(self):
        self.scene.advance_to_garfield_arrival()
        names = [
            (
                event['name']
                if isinstance(
                    event,
                    dict,
                )
                else event.name
            )
            for event
            in self.scene.history
        ]
        last_scratch = max((index for index, name in enumerate(names) if name == 'cat_d20_scratched'))
        prepared = names.index('cat_d20_sets_next_birth_to_garfield')
        arrival = names.index('garfield_arrives_at_bar')
        self.assertLess(last_scratch, prepared)
        self.assertLess(prepared, arrival)
if __name__ == '__main__':
    unittest.main()
