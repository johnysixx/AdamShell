from core.entity.social_entity import SocialEntity
import unittest
from meeting_place.bar_counter import BarCounter
from meeting_place.bartender import Bartender

class BartenderKnownGuestTests(unittest.TestCase):

    def test_remember_guest_keeps_reference_to_life_history(self):
        bar_counter = BarCounter()
        bartender = Bartender(bar_counter.hidden_story_book)
        life_history = [{'event': 'born', 'place': 'earth'}]
        guest = SocialEntity.from_mapping({'name': 'newton', 'type': 'guest', 'life_history': life_history})
        bartender.remember_guest(guest)
        self.assertTrue(bartender.knows_guest('newton'))
        self.assertIs(bartender.known_histories['newton'], life_history)
        life_history.append({'event': 'entered_bar'})
        self.assertEqual(bartender.known_histories['newton'][-1]['event'], 'entered_bar')
if __name__ == '__main__':
    unittest.main()
