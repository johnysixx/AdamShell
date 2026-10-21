import unittest

from cats.cat_components import CatTerritories
from cats.cat_social_objects import CatTerritoryClaim
from cats.cat_territory_system import CatTerritorySystem
from cats.cat_territory_result_state import (
    CatTerritoryClaimedEvent,
    CatTerritoryScentMarkedEvent,
)
from cats.cats import Cats
from core.entity.domain_object import DomainObject
from universe.universe import Universe


class CatTerritoriesObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(
            name="territory_cat",
            color="black",
            fur_length="short",
        )
        self.cat.current_layer = "meeting_place"
        self.cat.location = "window"
        self.system = CatTerritorySystem(
            self.cats
        )

    def test_new_cat_has_object_territory_registry(self):
        self.assertIsInstance(
            self.cat.territories,
            CatTerritories,
        )
        self.assertEqual(
            self.cat.territories.owner,
            self.cat.name,
        )

        self.assertTrue(
            self.cat.territories.is_empty
        )

        self.assertEqual(
            self.cat.territories.count,
            0,
        )

        self.assertEqual(
            self.cat.territories.records(),
            (),
        )

        self.assertIsInstance(
            self.cat.territories,
            DomainObject,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "pop",
            "setdefault",
            "clear",
            "__getitem__",
            "__setitem__",
            "__contains__",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    self.cat.territories,
                    mapping_method,
                )
            )

    def test_claim_is_stored_in_object_registry(self):
        claim = self.system.claim(
            self.cat,
            strength=0.7,
        )
        stored = (
            self.cat.territories.record(
                "meeting_place",
                "window",
            )
        )

        self.assertIsInstance(
            stored,
            CatTerritoryClaim,
        )

        self.assertEqual(
            claim,
            stored,
        )

        self.assertEqual(
            stored.owner,
            self.cat.name,
        )

    def test_registry_rejects_invalid_claims(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            self.cat.territories.store(
                {
                    "owner": self.cat.name,
                }
            )

        with self.assertRaises(
            ValueError
        ):
            self.cat.territories.store(
                CatTerritoryClaim(
                    owner="other_cat",
                    layer="meeting_place",
                    location="window",
                )
            )

    def test_territory_events_are_object_state(
        self
    ):
        self.system.claim(
            self.cat,
            strength=0.7,
        )

        claimed = (
            self.cat
            .social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            claimed,
            CatTerritoryClaimedEvent,
        )

        self.assertEqual(
            claimed.territory,
            "meeting_place::window",
        )

        self.system.scent_mark(
            self.cat
        )

        marked = (
            self.cat
            .social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            marked,
            CatTerritoryScentMarkedEvent,
        )

        for event in (
            claimed,
            marked,
        ):
            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
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
                _ = event[
                    "name"
                ]

    def test_scent_mark_updates_registered_claim(self):
        self.system.claim(
            self.cat,
            strength=0.6,
        )
        self.system.scent_mark(
            self.cat
        )

        claim = self.cat.territories.record(
            "meeting_place",
            "window",
        )

        self.assertEqual(
            claim.scent_marks,
            2,
        )
        self.assertGreater(
            claim.strength,
            0.6,
        )


if __name__ == "__main__":
    unittest.main()
