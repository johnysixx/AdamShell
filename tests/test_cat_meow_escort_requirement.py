import unittest
from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace
from cats.cats import Cats
from cats.cat_human_bond_system import CatHumanBondSystem
from cats.cat_meow_invitation_system import CatMeowInvitationSystem
from cats.cat_bar_guidance_system import CatBarGuidanceSystem

class Human:

    def __init__(self, name):
        self.name = name
        self.type = 'human'
        self.current_layer = 'physical_world'
        self.location = 'outside_bar'

class CatMEOWEscortRequirementTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.meeting = MeetingPlace(self.universe)
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(name='escort_cat', color='black', fur_length='short')
        self.wrong_cat = self.cats.create_cat(name='wrong_cat', color='white', fur_length='short')
        self.human = Human('chosen_human')
        bonds = CatHumanBondSystem(self.cats)
        for _ in range(8):
            bonds.remember_interaction(self.cat, self.human, positive=True, significance=0.15)
        self.invitations = CatMeowInvitationSystem(self.cats)
        self.offered = self.invitations.offer(self.cat, self.human)
        self.assertTrue(self.offered['offered'])
        self.invitations.interpret(self.offered['id'], self.human, understood=True)
        self.human.meow_bar_invitation = {'source': 'cat_MEOW_invitation', 'inviting_cat': self.cat.name, 'invitation_id': self.offered['id'], 'permanent': False}
        self.meeting.bouncer.register_meow_invitation_system(self.invitations)

    def test_valid_MEOW_without_cat_does_not_admit(self):
        result = self.meeting.add_cat_invited_human(self.human, None, self.invitations)
        self.assertFalse(result['entered'])
        self.assertEqual(result['reason'], 'inviting_cat_not_present')
        self.assertNotIn(self.human, self.meeting.entities)

    def test_wrong_cat_cannot_escort(self):
        result = self.meeting.bouncer.can_enter_with_cat(self.human, self.wrong_cat)
        self.assertFalse(result['authorized'])
        self.assertEqual(result['reason'], 'MEOW_wrong_cat')

    def test_real_inviting_cat_can_escort(self):
        result = self.meeting.bouncer.can_enter_with_cat(self.human, self.cat)
        self.assertTrue(result['authorized'])

    def test_guidance_brings_cat_and_human_together(self):
        guidance = CatBarGuidanceSystem(self.invitations, self.meeting)
        result = guidance.guide(self.cat, self.human, self.offered['id'])
        self.assertTrue(result['guided'])
        self.assertIn(self.cat, self.meeting.entities)
        self.assertIn(self.human, self.meeting.entities)
        self.assertEqual(self.cat.current_layer, 'meeting_place')
        self.assertEqual(self.human.current_layer, 'meeting_place')
        guest = self.meeting.cat_invited_guests[self.human.name]
        self.assertTrue(guest["cat_present"])
        self.assertTrue(guest["entered_together"])
        self.assertEqual(guest["inviting_cat"], self.cat.name)

    def test_invitation_becomes_used_only_after_entry(self):
        guidance = CatBarGuidanceSystem(self.invitations, self.meeting)
        before = self.invitations.get(self.offered['id'])
        self.assertFalse(before['used'])
        result = guidance.guide(self.cat, self.human, self.offered['id'])
        self.assertTrue(result['guided'])
        after = self.invitations.get(self.offered['id'])
        self.assertTrue(after['used'])
if __name__ == '__main__':
    unittest.main()
