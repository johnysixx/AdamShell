import unittest

from universe.universe import Universe
from gods.gods import Gods


class GodMaskTests(unittest.TestCase):

    def test_director_is_mask_of_existing_god(
        self
    ):
        universe = Universe()

        gods = Gods(
            universe
        )

        god = gods.create_god(
            name="god",
            role="creator_entity"
        )

        director = gods.assume_mask(
            god=god,
            mask_name="director",
            role="quantum_director"
        )

        self.assertIs(
            director["mask_of"],
            god
        )

        self.assertEqual(
            director["name"],
            "director"
        )

        self.assertEqual(
            director["role"],
            "quantum_director"
        )

        self.assertIs(
            director["knowledge"],
            god["knowledge"]
        )

        self.assertIs(
            director["research_book"],
            god["research_book"]
        )

        self.assertEqual(
            god["name"],
            "god"
        )



    def test_quantum_director_wraps_god_director_mask(
        self
    ):
        from quantum.director import QuantumDirector

        universe = Universe()

        gods = Gods(
            universe
        )

        god = gods.create_god(
            name="god",
            role="creator_entity"
        )

        director = QuantumDirector(
            universe=universe,
            god=god,
            gods=gods
        )

        self.assertIs(
            director.god,
            god
        )

        self.assertIs(
            director.mask["mask_of"],
            god
        )

        self.assertEqual(
            director.mask["name"],
            "director"
        )

        self.assertIs(
            director.knowledge,
            god["knowledge"]
        )

        self.assertIs(
            director.research_book,
            god["research_book"]
        )



    def test_god_can_release_marduk_mask_without_losing_memory(
        self
    ):
        universe = Universe()

        gods = Gods(
            universe
        )

        god = gods.create_god(
            name="god",
            role="creator_entity"
        )

        marduk = gods.assume_mask(
            god=god,
            mask_name="marduk",
            role="divine_champion"
        )

        god["knowledge"].add(
            "tiamat_defeated"
        )

        god["research_book"].append(
            {
                "event": "cosmos_ordered"
            }
        )

        knowledge = god["knowledge"]
        research_book = god["research_book"]

        released = gods.release_mask(
            god=god,
            mask_name="marduk"
        )

        self.assertEqual(
            released["released_mask"],
            "marduk"
        )

        self.assertIsNone(
            god["active_mask"]
        )

        self.assertIs(
            god["knowledge"],
            knowledge
        )

        self.assertIs(
            god["research_book"],
            research_book
        )

        self.assertIn(
            "tiamat_defeated",
            god["knowledge"]
        )

        self.assertEqual(
            god["research_book"][0]["event"],
            "cosmos_ordered"
        )

        self.assertEqual(
            god["name"],
            "god"
        )

        self.assertFalse(
            marduk.get(
                "active",
                False
            )
        )



    def test_god_can_switch_from_marduk_to_director_without_losing_memory(
        self
    ):
        universe = Universe()

        gods = Gods(
            universe
        )

        god = gods.create_god(
            name="god",
            role="creator_entity"
        )

        marduk = gods.assume_mask(
            god=god,
            mask_name="marduk",
            role="divine_champion"
        )

        god["knowledge"].add(
            "cosmos_ordered"
        )

        god["research_book"].append(
            {
                "event": "tiamat_defeated"
            }
        )

        knowledge = god["knowledge"]
        research_book = god["research_book"]

        gods.release_mask(
            god=god,
            mask_name="marduk"
        )

        director = gods.assume_mask(
            god=god,
            mask_name="director",
            role="quantum_director"
        )

        self.assertFalse(
            marduk["active"]
        )

        self.assertTrue(
            director["active"]
        )

        self.assertEqual(
            god["active_mask"],
            "director"
        )

        self.assertIs(
            director["knowledge"],
            knowledge
        )

        self.assertIs(
            director["research_book"],
            research_book
        )

        self.assertIn(
            "cosmos_ordered",
            director["knowledge"]
        )

        self.assertEqual(
            director["research_book"][0]["event"],
            "tiamat_defeated"
        )


if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()



