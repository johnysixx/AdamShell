import unittest

from cats import Cats
from cats.cat_reproduction_state import CatReproductionState
from cats.development_resolver import CatDevelopmentResolver
from cats.reproduction import CatReproduction
from universe.universe import Universe


class CatReproductionObjectStateTests(unittest.TestCase):

    def test_state_is_object_only(self):
        state = CatReproductionState("female")

        self.assertFalse(hasattr(state, "get"))
        self.assertFalse(hasattr(state, "keys"))
        self.assertFalse(hasattr(state, "update"))

        with self.assertRaises(TypeError):
            _ = state["pregnant"]

    def test_slots_reject_unknown_state(self):
        state = CatReproductionState("female")

        with self.assertRaises(AttributeError):
            state.unknown_reproductive_state = True

    def test_initial_female_state_is_preserved(self):
        state = CatReproductionState("female")

        self.assertEqual(state.sex, "female")
        self.assertFalse(state.neutered)
        self.assertTrue(state.fertile)
        self.assertFalse(state.reproductive_maturity)
        self.assertEqual(state.estrous_phase, "inactive")
        self.assertFalse(state.estrus_active)
        self.assertFalse(state.pregnant)
        self.assertEqual(state.embryos, [])
        self.assertEqual(state.litters, [])
        self.assertEqual(state.father_names, [])

    def test_neutered_state_is_not_fertile(self):
        state = CatReproductionState(
            "male",
            neutered=True,
        )

        self.assertTrue(state.neutered)
        self.assertFalse(state.fertile)

    def test_invalid_sex_is_rejected(self):
        with self.assertRaises(ValueError):
            CatReproductionState("unknown")

    def test_factory_returns_state_object(self):
        state = CatReproduction.create_state(
            sex="female",
            neutered=False,
        )

        self.assertIsInstance(
            state,
            CatReproductionState,
        )

    def test_mutable_collections_are_not_shared(self):
        first = CatReproductionState("female")
        second = CatReproductionState("female")

        first.potential_fathers.append("tom")
        first.embryos.append("embryo")
        first.litters.append("litter")

        self.assertEqual(second.potential_fathers, [])
        self.assertEqual(second.embryos, [])
        self.assertEqual(second.litters, [])

    def test_to_dict_returns_detached_boundary(self):
        state = CatReproductionState("female")
        state.potential_fathers.append("tom")
        state.mating_contacts.append({
            "male": "tom",
            "successful": True,
        })

        snapshot = state.to_dict()

        self.assertIsInstance(snapshot, dict)

        snapshot["potential_fathers"].append("garfield")
        snapshot["mating_contacts"][0]["successful"] = False

        self.assertEqual(
            state.potential_fathers,
            ["tom"],
        )
        self.assertTrue(
            state.mating_contacts[0]["successful"]
        )

    def test_cats_layer_creates_object_state(self):
        universe = Universe()
        cats = Cats(universe)

        cat = cats.create_cat(
            name="reproductive_state_cat",
            color="black",
            fur_length="short",
            sex="female",
        )

        self.assertIsInstance(
            cat.reproduction,
            CatReproductionState,
        )

    def test_development_mutates_same_state_object(self):
        universe = Universe()
        cats = Cats(universe)

        kitten = cats.create_cat(
            name="reproductive_state_kitten",
            color="black",
            fur_length="short",
            sex="female",
        )

        state = kitten.reproduction

        CatDevelopmentResolver(
            universe
        ).initialize_newborn(
            kitten,
            birth_day=0,
        )

        self.assertIs(kitten.reproduction, state)
        self.assertEqual(
            state.developmental_stage,
            "newborn",
        )
        self.assertFalse(state.reproductive_maturity)
        self.assertFalse(state.fertile)


if __name__ == "__main__":
    unittest.main()
