import unittest
from types import SimpleNamespace

from cats.cat_reproduction_state import (
    CatReproductionState,
)

from cats.mating_contact import (
    CatMatingContact,
)


class CatReproductionMatingContactsStateTests(
    unittest.TestCase
):

    def _contact(self):
        male = SimpleNamespace(
            name="father"
        )

        return CatMatingContact(
            contact_number=1,
            female="mother",
            male="father",
            successful=True,
            day=12,
            male_ref=male,
        )

    def test_dead_singular_mating_contact_is_absent(
        self
    ):
        state = (
            CatReproductionState(
                sex="female"
            )
        )

        self.assertFalse(
            hasattr(
                state,
                "mating_contact",
            )
        )

        boundary = (
            state.to_dict()
        )

        self.assertNotIn(
            "mating_contact",
            boundary,
        )

        self.assertIn(
            "mating_contacts",
            boundary,
        )

    def test_mating_contacts_is_canonical_object_state(
        self
    ):
        state = (
            CatReproductionState(
                sex="female"
            )
        )

        contact = self._contact()

        state.mating_contacts.append(
            contact
        )

        self.assertIs(
            state.mating_contacts[0],
            contact,
        )

        self.assertIsInstance(
            state.mating_contacts[0],
            CatMatingContact,
        )

        self.assertEqual(
            state.mating_contacts[0].male,
            "father",
        )

    def test_boundary_serializes_contact_without_mutating_domain(
        self
    ):
        state = (
            CatReproductionState(
                sex="female"
            )
        )

        contact = self._contact()

        state.mating_contacts.append(
            contact
        )

        boundary = (
            state.to_dict()
        )

        self.assertIsInstance(
            boundary[
                "mating_contacts"
            ][0],
            dict,
        )

        boundary[
            "mating_contacts"
        ][0][
            "male"
        ] = "changed"

        self.assertEqual(
            contact.male,
            "father",
        )

        self.assertEqual(
            state.mating_contacts[0].male,
            "father",
        )


if __name__ == "__main__":
    unittest.main()
