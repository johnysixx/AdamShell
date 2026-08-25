import unittest

from meeting_place.bar_counter import BarCounter
from meeting_place.bartender import Bartender
from meeting_place.how_to_mix_drinks import (
    HowToMixDrinks
)


class HowToMixDrinksTests(unittest.TestCase):

    def test_bartender_created_cocktail_is_saved_as_recipe(
        self
    ):
        bar_counter = BarCounter()

        book = HowToMixDrinks()

        bartender = Bartender(
            bar_counter.hidden_story_book,
            mix_book=book
        )

        bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            recipe["name"],
            "singularity"
        )

        self.assertEqual(
            recipe["origin"],
            "created_by_bartender"
        )

        self.assertEqual(
            recipe["status"],
            "testing"
        )

        self.assertEqual(
            recipe["ingredients"],
            [
                "raspberry_rum",
                "lemonade"
            ]
        )

        self.assertEqual(
            recipe["tastings"],
            []
        )

        self.assertEqual(
            recipe["votes_for"],
            0
        )

        self.assertEqual(
            recipe["votes_against"],
            0
        )

        self.assertFalse(
            recipe["approved"]
        )

        self.assertEqual(
            bartender.chronicle_memory[-1],
            {
                "kind": "created_cocktail",
                "drink": "singularity"
            }
        )


    def test_tasting_records_guest_opinion_and_vote(
        self
    ):
        book = HowToMixDrinks()

        book.add_created_recipe(
            name="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        tasting = book.record_tasting(
            drink="singularity",
            guest="newton",
            liked=True,
            comment="needs more lemon"
        )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            tasting,
            {
                "guest": "newton",
                "liked": True,
                "comment": "needs more lemon"
            }
        )

        self.assertEqual(
            recipe["tastings"],
            [
                {
                    "guest": "newton",
                    "liked": True,
                    "comment": "needs more lemon"
                }
            ]
        )

        self.assertEqual(
            recipe["votes_for"],
            1
        )

        self.assertEqual(
            recipe["votes_against"],
            0
        )

        self.assertEqual(
            recipe["status"],
            "testing"
        )

        self.assertFalse(
            recipe["approved"]
        )


    def test_bartender_offers_testing_drink_only_to_regular_guest(
        self
    ):
        bar_counter = BarCounter()
        book = HowToMixDrinks()

        bartender = Bartender(
            bar_counter.hidden_story_book,
            mix_book=book
        )

        bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        self.assertFalse(
            bartender.offer_cocktail_tasting(
                guest="guest_1",
                drink="singularity"
            )
        )

        bartender.regular_guests.add(
            "newton"
        )

        self.assertTrue(
            bartender.offer_cocktail_tasting(
                guest="newton",
                drink="singularity"
            )
        )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            recipe["tastings"],
            []
        )

        self.assertEqual(
            recipe["votes_for"],
            0
        )

        self.assertEqual(
            recipe["votes_against"],
            0
        )


    def test_bartender_records_regular_guest_cocktail_tasting(
        self
    ):
        bar_counter = BarCounter()
        book = HowToMixDrinks()

        bartender = Bartender(
            bar_counter.hidden_story_book,
            mix_book=book
        )

        bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        bartender.regular_guests.add(
            "newton"
        )

        tasting = bartender.record_cocktail_tasting(
            guest="newton",
            drink="singularity",
            liked=True,
            comment="needs more lemon"
        )

        self.assertEqual(
            tasting,
            {
                "guest": "newton",
                "liked": True,
                "comment": "needs more lemon"
            }
        )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            recipe["votes_for"],
            1
        )

        self.assertEqual(
            recipe["votes_against"],
            0
        )

        self.assertEqual(
            recipe["tastings"][-1]["guest"],
            "newton"
        )

        self.assertEqual(
            recipe["tastings"][-1]["comment"],
            "needs more lemon"
        )


    def test_same_guest_cannot_vote_twice_on_same_cocktail(
        self
    ):
        bar_counter = BarCounter()
        book = HowToMixDrinks()

        bartender = Bartender(
            bar_counter.hidden_story_book,
            mix_book=book
        )

        bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        bartender.regular_guests.add(
            "newton"
        )

        bartender.record_cocktail_tasting(
            guest="newton",
            drink="singularity",
            liked=True,
            comment="good"
        )

        with self.assertRaises(
            ValueError
        ):
            bartender.record_cocktail_tasting(
                guest="newton",
                drink="singularity",
                liked=False,
                comment="changed my mind"
            )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            len(recipe["tastings"]),
            1
        )

        self.assertEqual(
            recipe["votes_for"],
            1
        )

        self.assertEqual(
            recipe["votes_against"],
            0
        )


    def test_cocktail_is_approved_with_four_of_five_votes(
        self
    ):
        bar_counter = BarCounter()
        book = HowToMixDrinks()

        bartender = Bartender(
            bar_counter.hidden_story_book,
            mix_book=book
        )

        bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        guests = [
            "newton",
            "tesla",
            "feynman",
            "curie",
            "archimedes"
        ]

        for guest in guests:
            bartender.regular_guests.add(
                guest
            )

        votes = [
            True,
            True,
            True,
            True,
            False
        ]

        for guest, liked in zip(
            guests,
            votes
        ):
            bartender.record_cocktail_tasting(
                guest=guest,
                drink="singularity",
                liked=liked,
                comment=None
            )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            len(recipe["tastings"]),
            5
        )

        self.assertEqual(
            recipe["votes_for"],
            4
        )

        self.assertEqual(
            recipe["votes_against"],
            1
        )

        self.assertTrue(
            recipe["approved"]
        )

        self.assertEqual(
            recipe["status"],
            "approved"
        )

        self.assertIn(
            {
                "kind": "cocktail_approved",
                "drink": "singularity",
                "votes_for": 4,
                "votes_against": 1
            },
            bartender.chronicle_memory
        )


    def test_cocktail_is_rejected_with_three_of_five_votes(
        self
    ):
        bar_counter = BarCounter()
        book = HowToMixDrinks()

        bartender = Bartender(
            bar_counter.hidden_story_book,
            mix_book=book
        )

        bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        guests = [
            "newton",
            "tesla",
            "feynman",
            "curie",
            "archimedes"
        ]

        for guest in guests:
            bartender.regular_guests.add(
                guest
            )

        votes = [
            True,
            True,
            True,
            False,
            False
        ]

        for guest, liked in zip(
            guests,
            votes
        ):
            bartender.record_cocktail_tasting(
                guest=guest,
                drink="singularity",
                liked=liked,
                comment=None
            )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            recipe["votes_for"],
            3
        )

        self.assertEqual(
            recipe["votes_against"],
            2
        )

        self.assertFalse(
            recipe["approved"]
        )

        self.assertEqual(
            recipe["status"],
            "rejected"
        )

        self.assertIn(
            {
                "kind": "cocktail_rejected",
                "drink": "singularity",
                "votes_for": 3,
                "votes_against": 2
            },
            bartender.chronicle_memory
        )


    def test_approved_cocktail_can_be_added_as_bar_new_drink(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        book = HowToMixDrinks()

        bartender = Bartender(
            meeting_place
            .bar_counter
            .hidden_story_book,
            mix_book=book
        )

        bartender.regular_guests.update(
            {
                "newton",
                "tesla",
                "feynman",
                "curie",
                "archimedes"
            }
        )

        bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        votes = [
            True,
            True,
            True,
            True,
            False
        ]

        guests = [
            "newton",
            "tesla",
            "feynman",
            "curie",
            "archimedes"
        ]

        for guest, liked in zip(
            guests,
            votes
        ):
            bartender.record_cocktail_tasting(
                guest=guest,
                drink="singularity",
                liked=liked
            )

        recipe = book.recipes[
            "singularity"
        ]

        meeting_place.add_approved_cocktail(
            recipe
        )

        self.assertIn(
            "singularity",
            meeting_place.new_drinks
        )

        self.assertIs(
            meeting_place.new_drinks[
                "singularity"
            ],
            recipe
        )


    def test_rejected_cocktail_cannot_be_added_as_bar_new_drink(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        recipe = {
            "name": "singularity",
            "status": "rejected",
            "approved": False,
            "ingredients": [
                "raspberry_rum",
                "lemonade"
            ]
        }

        with self.assertRaises(
            ValueError
        ):
            meeting_place.add_approved_cocktail(
                recipe
            )

        self.assertNotIn(
            "singularity",
            meeting_place.new_drinks
        )


    def test_approved_cocktail_is_added_to_new_drinks_automatically(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace
        from meeting_place.how_to_mix_drinks import HowToMixDrinks

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        book = HowToMixDrinks()

        meeting_place.bartender.mix_book = (
            book
        )

        meeting_place.bartender.regular_guests.update(
            {
                "newton",
                "tesla",
                "feynman",
                "curie",
                "archimedes"
            }
        )

        meeting_place.bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        guests = [
            "newton",
            "tesla",
            "feynman",
            "curie",
            "archimedes"
        ]

        votes = [
            True,
            True,
            True,
            True,
            False
        ]

        for guest, liked in zip(
            guests,
            votes
        ):
            meeting_place.bartender.record_cocktail_tasting(
                guest=guest,
                drink="singularity",
                liked=liked
            )

        self.assertIn(
            "singularity",
            meeting_place.new_drinks
        )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertIs(
            meeting_place.new_drinks[
                "singularity"
            ],
            recipe
        )


    def test_rejected_cocktail_is_not_added_to_new_drinks_automatically(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace
        from meeting_place.how_to_mix_drinks import HowToMixDrinks

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        book = HowToMixDrinks()

        meeting_place.bartender.mix_book = (
            book
        )

        meeting_place.bartender.regular_guests.update(
            {
                "newton",
                "tesla",
                "feynman",
                "curie",
                "archimedes"
            }
        )

        meeting_place.bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        guests = [
            "newton",
            "tesla",
            "feynman",
            "curie",
            "archimedes"
        ]

        votes = [
            True,
            True,
            True,
            False,
            False
        ]

        for guest, liked in zip(
            guests,
            votes
        ):
            meeting_place.bartender.record_cocktail_tasting(
                guest=guest,
                drink="singularity",
                liked=liked
            )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            recipe["status"],
            "rejected"
        )

        self.assertFalse(
            recipe["approved"]
        )

        self.assertNotIn(
            "singularity",
            meeting_place.new_drinks
        )


    def test_rejected_cocktail_is_not_added_to_new_drinks_automatically(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace
        from meeting_place.how_to_mix_drinks import HowToMixDrinks

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        book = HowToMixDrinks()

        meeting_place.bartender.mix_book = (
            book
        )

        meeting_place.bartender.regular_guests.update(
            {
                "newton",
                "tesla",
                "feynman",
                "curie",
                "archimedes"
            }
        )

        meeting_place.bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        guests = [
            "newton",
            "tesla",
            "feynman",
            "curie",
            "archimedes"
        ]

        votes = [
            True,
            True,
            True,
            False,
            False
        ]

        for guest, liked in zip(
            guests,
            votes
        ):
            meeting_place.bartender.record_cocktail_tasting(
                guest=guest,
                drink="singularity",
                liked=liked
            )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            recipe["status"],
            "rejected"
        )

        self.assertFalse(
            recipe["approved"]
        )

        self.assertNotIn(
            "singularity",
            meeting_place.new_drinks
        )


    def test_approved_cocktail_is_added_to_new_drinks_automatically(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace
        from meeting_place.how_to_mix_drinks import HowToMixDrinks

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        book = HowToMixDrinks()

        meeting_place.bartender.mix_book = (
            book
        )

        meeting_place.bartender.regular_guests.update(
            {
                "newton",
                "tesla",
                "feynman",
                "curie",
                "archimedes"
            }
        )

        meeting_place.bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        guests = [
            "newton",
            "tesla",
            "feynman",
            "curie",
            "archimedes"
        ]

        votes = [
            True,
            True,
            True,
            True,
            False
        ]

        for guest, liked in zip(
            guests,
            votes
        ):
            meeting_place.bartender.record_cocktail_tasting(
                guest=guest,
                drink="singularity",
                liked=liked
            )

        self.assertIn(
            "singularity",
            meeting_place.new_drinks
        )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertIs(
            meeting_place.new_drinks[
                "singularity"
            ],
            recipe
        )


    def test_rejected_cocktail_is_not_added_to_new_drinks_automatically(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace
        from meeting_place.how_to_mix_drinks import HowToMixDrinks

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        book = HowToMixDrinks()

        meeting_place.bartender.mix_book = (
            book
        )

        meeting_place.bartender.regular_guests.update(
            {
                "newton",
                "tesla",
                "feynman",
                "curie",
                "archimedes"
            }
        )

        meeting_place.bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        guests = [
            "newton",
            "tesla",
            "feynman",
            "curie",
            "archimedes"
        ]

        votes = [
            True,
            True,
            True,
            False,
            False
        ]

        for guest, liked in zip(
            guests,
            votes
        ):
            meeting_place.bartender.record_cocktail_tasting(
                guest=guest,
                drink="singularity",
                liked=liked
            )

        recipe = book.recipes[
            "singularity"
        ]

        self.assertEqual(
            recipe["status"],
            "rejected"
        )

        self.assertFalse(
            recipe["approved"]
        )

        self.assertNotIn(
            "singularity",
            meeting_place.new_drinks
        )


    def test_approved_cocktail_is_noted_as_new_menu_drink(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace
        from meeting_place.how_to_mix_drinks import HowToMixDrinks

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        book = HowToMixDrinks()

        meeting_place.bartender.mix_book = (
            book
        )

        meeting_place.bartender.regular_guests.update(
            {
                "newton",
                "tesla",
                "feynman",
                "curie",
                "archimedes"
            }
        )

        meeting_place.bartender.create_cocktail(
            drink="singularity",
            ingredients=[
                "raspberry_rum",
                "lemonade"
            ]
        )

        guests = [
            "newton",
            "tesla",
            "feynman",
            "curie",
            "archimedes"
        ]

        votes = [
            True,
            True,
            True,
            True,
            False
        ]

        for guest, liked in zip(
            guests,
            votes
        ):
            meeting_place.bartender.record_cocktail_tasting(
                guest=guest,
                drink="singularity",
                liked=liked
            )

        self.assertIn(
            {
                "kind": "new_menu_drink",
                "drink": "singularity"
            },
            meeting_place
            .bartender
            .chronicle_memory
        )


    def test_book_contains_basic_raspberry_rum_recipe(
        self
    ):
        book = HowToMixDrinks()

        self.assertIn(
            "raspberry_rum",
            book.recipes
        )

        recipe = book.recipes[
            "raspberry_rum"
        ]

        self.assertEqual(
            recipe["ingredients"],
            {
                "rum": {
                    "shots": 1,
                    "consumed": False
                },
                "liquid_hydrocarbons": {
                    "shots": 1,
                    "consumed": True
                }
            }
        )

        self.assertEqual(
            recipe["origin"],
            "basic_bar_recipe"
        )


if __name__ == "__main__":
    unittest.main()
















