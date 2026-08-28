from core.entity.social_entity import SocialEntity
import unittest
from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace
from quantum.director import QuantumDirector
from gods.gods import Gods

class DirectorBarArrivalTests(unittest.TestCase):

    def test_director_arrives_at_bar_with_liquid_hydrocarbon_sample_and_meets_serpent(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        meeting_place = MeetingPlace(universe)
        universe.meeting_place = meeting_place
        gods = Gods(universe)
        god = gods.create_god(name='god', role='creator_entity')
        director = QuantumDirector(universe=universe, god=god, gods=gods)
        serpent = SocialEntity.from_mapping({'name': 'serpent', 'type': 'idea_entity', 'role': 'primordial_serpent'})
        meeting_place.entities.append(serpent)
        result = director.arrive_at_bar(meeting_place=meeting_place, sample={'material': 'liquid_hydrocarbons', 'amount': 3.0})
        self.assertIn(director, meeting_place.entities)
        self.assertEqual(result['sample']['material'], 'liquid_hydrocarbons')
        self.assertEqual(result['sample']['amount'], 3.0)
        self.assertIs(result['met'], serpent)
        self.assertEqual(result['event'], 'director_arrived_at_bar')
if __name__ == '__main__':
    unittest.main()
