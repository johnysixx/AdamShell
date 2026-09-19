import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import (
    MeetingPlace,
)
from meeting_place.cat_invited_guest_state import (
    CatInvitedGuestState,
)
from cats.cats import Cats
from cats.cat_human_bond_system import (
    CatHumanBondSystem,
)
from cats.cat_meow_invitation_system import (
    CatMeowInvitationSystem,
)
from cats.cat_bar_guidance_system import (
    CatBarGuidanceSystem,
)


class Human:

    def __init__(
        self,
        name,
    ):
        self.name = name
        self.type = 'human'
        self.current_layer = (
            'physical_world'
        )
        self.location = 'outside_bar'


class CatInvitedGuestObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.meeting = MeetingPlace(
            self.universe
        )

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='guest_state_cat',
            color='black',
            fur_length='short',
        )

        self.human = Human(
            'guest_state_human'
        )

        bonds = CatHumanBondSystem(
            self.cats
        )

        for _ in range(8):
            bonds.remember_interaction(
                self.cat,
                self.human,
                positive=True,
                significance=0.15,
            )

        self.invitations = (
            CatMeowInvitationSystem(
                self.cats
            )
        )

        self.offered = (
            self.invitations.offer(
                self.cat,
                self.human,
            )
        )

        self.assertTrue(
            self.offered.offered
        )

        self.invitations.interpret(
            self.offered.id,
            self.human,
            understood=True,
        )

        self.guidance = (
            CatBarGuidanceSystem(
                self.invitations,
                self.meeting,
            )
        )

    def _guide(
        self,
    ):
        return self.guidance.guide(
            self.cat,
            self.human,
            self.offered.id,
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatInvitedGuestState(
            human=self.human.name,
            inviting_cat=self.cat.name,
            invitation_id=self.offered.id,
        )

        self.assertFalse(
            hasattr(
                state,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                'setdefault',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                '__getitem__',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                '__setitem__',
            )
        )

    def test_entry_stores_object_record(
        self
    ):
        result = self._guide()

        self.assertTrue(
            result['guided']
        )

        record = (
            self.meeting
            .cat_invited_guests[
                self.human.name
            ]
        )

        self.assertIsInstance(
            record,
            CatInvitedGuestState,
        )

        self.assertEqual(
            record.human,
            self.human.name,
        )

        self.assertEqual(
            record.inviting_cat,
            self.cat.name,
        )

        self.assertEqual(
            record.invitation_id,
            self.offered.id,
        )

    def test_entry_flags_are_object_state(
        self
    ):
        self._guide()

        record = (
            self.meeting
            .cat_invited_guests[
                self.human.name
            ]
        )

        self.assertTrue(
            record.cat_present
        )

        self.assertTrue(
            record.entered_together
        )

        self.assertFalse(
            record.permanent_access
        )

    def test_incident_reads_object_record(
        self
    ):
        self._guide()

        incident = (
            self.meeting
            .record_cat_guest_incident(
                self.human,
                category='guest_misbehavior',
                cooldown_ticks=24,
            )
        )

        self.assertTrue(
            incident.cat_responsibility
        )

        self.assertEqual(
            incident.inviting_cat,
            self.cat.name,
        )

        self.assertEqual(
            incident.invitation_id,
            self.offered.id,
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        self.meeting.cat_invited_guests = {
            self.human.name: {
                'human':
                    self.human.name,
                'inviting_cat':
                    self.cat.name,
                'invitation_id':
                    self.offered.id,
                'cat_present':
                    True,
                'entered_together':
                    True,
                'permanent_access':
                    False,
            }
        }

        with self.assertRaises(
            TypeError
        ):
            (
                self.meeting
                .record_cat_guest_incident(
                    self.human,
                    category=(
                        'guest_misbehavior'
                    ),
                )
            )


if __name__ == '__main__':
    unittest.main()
