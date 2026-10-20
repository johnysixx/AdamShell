from core.entity.components import SpatialVector3
import unittest

from cats.cat_components import CatSocialMemories
from cats.cat_social_objects import CatSocialMemory
from cats.cat_social_system import CatSocialSystem
from cats.cats import Cats
from core.entity.domain_object import DomainObject
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

    def test_new_cat_has_object_memory_registry(
        self
    ):
        registry = (
            self.first.social_memory
        )

        self.assertIsInstance(
            registry,
            CatSocialMemories,
        )

        self.assertIsInstance(
            registry,
            DomainObject,
        )

        self.assertTrue(
            registry.is_empty
        )

        self.assertEqual(
            registry.count,
            0,
        )

        self.assertEqual(
            registry.records(),
            (),
        )

        self.assertFalse(
            hasattr(
                registry,
                "to_dict",
            )
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "pop",
            "setdefault",
            "__getitem__",
            "__setitem__",
            "__contains__",
        ):
            self.assertFalse(
                hasattr(
                    registry,
                    mapping_method,
                )
            )

    def test_meeting_stores_memory_in_registry(
        self
    ):
        self.system.meet(
            self.first,
            self.second,
        )

        registry = (
            self.first.social_memory
        )

        memory = registry.record(
            self.second.name
        )

        self.assertEqual(
            registry.count,
            1,
        )

        self.assertIsInstance(
            memory,
            CatSocialMemory,
        )

        self.assertEqual(
            memory.other_cat,
            self.second.name,
        )

        with self.assertRaises(
            TypeError
        ):
            registry.store({
                "other_cat": self.second.name,
            })

    def test_cats_own_separate_memory_registries(
        self
    ):
        self.assertIsNot(
            self.first.social_memory,
            self.second.social_memory,
        )

        self.system.meet(
            self.first,
            self.second,
        )

        self.assertEqual(
            self.first.social_memory.count,
            1,
        )

        self.assertEqual(
            self.second.social_memory.count,
            1,
        )

        self.assertIsNot(
            self.first.social_memory.record(
                self.second.name
            ),
            self.second.social_memory.record(
                self.first.name
            ),
        )


if __name__ == "__main__":
    unittest.main()
