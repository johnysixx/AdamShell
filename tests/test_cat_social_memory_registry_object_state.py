from core.entity.components import SpatialVector3
import unittest

from cats.cat_components import CatSocialMemories
from cats.cat_social_objects import CatSocialMemory
from cats.cat_social_system import CatSocialSystem
from cats.cats import Cats
from universe.universe import Universe


class CatSocialMemoryRegistryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.first = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short",
        )
        self.second = self.cats.create_cat(
            name="second",
            color="white",
            fur_length="short",
        )
        self.first.position = SpatialVector3(x=0.0, y=0.0, z=0.0)
        self.second.position = self.first.position
        self.system = CatSocialSystem(
            self.cats
        )

    def test_new_cat_has_object_memory_registry(self):
        self.assertIsInstance(
            self.first.social_memory,
            CatSocialMemories,
        )
        self.assertEqual(
            self.first.social_memory.records,
            {},
        )

    def test_meeting_stores_memory_in_registry(self):
        self.system.meet(
            self.first,
            self.second,
        )

        records = (
            self.first.social_memory.records
        )

        self.assertIn(
            self.second.name,
            records,
        )
        self.assertIsInstance(
            records[self.second.name],
            CatSocialMemory,
        )

    def test_cats_own_separate_memory_registries(self):
        self.assertIsNot(
            self.first.social_memory,
            self.second.social_memory,
        )
        self.assertIsNot(
            self.first.social_memory.records,
            self.second.social_memory.records,
        )


if __name__ == "__main__":
    unittest.main()
