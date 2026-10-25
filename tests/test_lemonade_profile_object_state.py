import unittest
from types import SimpleNamespace

from meeting_place.meeting_place import MeetingPlace
from multiverse import UniverseRegistry
from universe.universe import Universe

from meeting_place.lemonade_profile import (
    LemonadeAddedEvent,
    LemonadeBatchProfile,
    LemonadeBatchRecord,
    LemonadeEntangledPair,
    LemonadeProfile,
    LemonadeServedEvent,
    LemonadeTraitProfile,
)
from meeting_place.lemonade_reservoir import (
    LemonadeReservoir,
)


class LemonadeProfileObjectStateTests(
    unittest.TestCase
):

    def _profile(
        self,
        *,
        acidity,
        sweetness=1.0,
        source_mass=1.0,
        source_names=("cronenberg",),
        strength=0.0,
        pairs=(),
    ):
        return LemonadeProfile(
            traits=LemonadeTraitProfile(
                acidity=acidity,
                sweetness=sweetness,
            ),
            source_mass=source_mass,
            source_cronenbergs=tuple(
                source_names
            ),
            entanglement_strength=strength,
            entangled_pairs=tuple(pairs),
            dominant_trait=(
                "acidity"
                if acidity >= sweetness
                else "sweetness"
            ),
        )

    def _assert_no_mapping_api(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                callable(
                    getattr(
                        value,
                        mapping_method,
                        None,
                    )
                )
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def test_builder_returns_object_profile(
        self
    ):
        profile = (
            LemonadeBatchProfile()
            .empty_profile()
        )

        self.assertIsInstance(
            profile,
            LemonadeProfile,
        )
        self.assertIsInstance(
            profile.traits,
            LemonadeTraitProfile,
        )
        self._assert_no_mapping_api(
            profile,
            "traits",
        )
        self._assert_no_mapping_api(
            profile.traits,
            "acidity",
        )

    def test_entangled_pair_is_object_state(
        self
    ):
        pair = LemonadeEntangledPair(
            cronenberg_ids=("one", "two"),
            strength=0.75,
            link_types=("quantum",),
        )

        self._assert_no_mapping_api(
            pair,
            "strength",
        )
        self.assertEqual(
            pair.strength,
            0.75,
        )

    def test_reservoir_requires_profile_object(
        self
    ):
        reservoir = LemonadeReservoir()

        with self.assertRaises(TypeError):
            reservoir.add_lemonade(
                amount_litres=1.0,
                profile={
                    "traits": {
                        "acidity": 1.0,
                    }
                },
            )

        self.assertEqual(
            reservoir.amount_litres,
            0.0,
        )
        self.assertEqual(
            reservoir.batch_history,
            [],
        )

    def test_reservoir_keeps_object_batch_state(
        self
    ):
        reservoir = LemonadeReservoir()
        profile = self._profile(
            acidity=1.5,
            source_names=("first",),
        )

        reservoir.add_lemonade(
            amount_litres=2.0,
            source="test_batch",
            profile=profile,
        )

        self.assertIsInstance(
            reservoir.current_profile,
            LemonadeProfile,
        )
        self.assertIsInstance(
            reservoir.batch_history[0],
            LemonadeBatchRecord,
        )
        self.assertIs(
            reservoir.batch_history[0].profile,
            profile,
        )

    def test_reservoir_events_are_object_state(
        self
    ):
        reservoir = LemonadeReservoir()

        profile = self._profile(
            acidity=1.0,
            source_names=("first",),
        )

        added = reservoir.add_lemonade(
            amount_litres=1.0,
            source="test_batch",
            profile=profile,
        )

        added_event = reservoir.events[0]

        self.assertIsInstance(
            added_event,
            LemonadeAddedEvent,
        )

        self._assert_no_mapping_api(
            added_event,
            "source",
        )

        self.assertIs(added, added_event)
        self.assertEqual(added.source, "test_batch")
        self._assert_no_mapping_api(added, "source")

        served = reservoir.serve(
            drinker_name="guest",
            location="bar",
        )

        served_event = reservoir.events[1]

        self.assertIsInstance(
            served_event,
            LemonadeServedEvent,
        )

        self._assert_no_mapping_api(
            served_event,
            "drinker",
        )

        self.assertIs(
            served_event.lemonade_profile,
            profile,
        )

        self.assertIs(served, served_event)
        self._assert_no_mapping_api(served, "drinker")

        snapshot = served.to_dict()
        snapshot["lemonade_profile"][
            "traits"
        ]["acidity"] = 99.0

        self.assertEqual(
            served_event
            .lemonade_profile
            .traits.acidity,
            1.0,
        )

    def test_reservoir_mixes_profiles_through_attributes(
        self
    ):
        reservoir = LemonadeReservoir()
        first = self._profile(
            acidity=1.0,
            sweetness=1.0,
            source_mass=1.0,
            source_names=("first",),
        )
        second = self._profile(
            acidity=2.0,
            sweetness=1.0,
            source_mass=3.0,
            source_names=("second",),
        )

        reservoir.add_lemonade(
            amount_litres=1.0,
            profile=first,
        )
        reservoir.add_lemonade(
            amount_litres=3.0,
            profile=second,
        )

        mixed = reservoir.current_profile

        self.assertIsInstance(
            mixed,
            LemonadeProfile,
        )
        self.assertEqual(
            mixed.traits.acidity,
            1.75,
        )
        self.assertEqual(
            mixed.source_mass,
            4.0,
        )
        self.assertEqual(
            mixed.source_cronenbergs,
            ("first", "second"),
        )

    def test_meeting_place_service_returns_event_object(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        bar = MeetingPlace(universe)

        added = bar.lemonade_reservoir.add_lemonade(
            amount_litres=1.0,
        )

        self.assertIsInstance(
            added,
            LemonadeAddedEvent,
        )
        self.assertIs(
            added,
            bar.lemonade_reservoir.events[0],
        )

        guest = SimpleNamespace(
            name="guest",
            type="human",
            location="at_bar",
        )

        served = bar.serve_lemonade(
            guest,
            location="at_bar",
        )

        self.assertIsInstance(
            served,
            LemonadeServedEvent,
        )
        self.assertIs(
            served,
            bar.lemonade_reservoir.events[-1],
        )
        self.assertEqual(served.drinker, "guest")
        self.assertEqual(served.location, "at_bar")
        self.assertEqual(served.remaining_litres, 0.5)

        self._assert_no_mapping_api(
            served,
            "drinker",
        )

        exported = served.to_dict()
        self.assertIsInstance(exported, dict)
        self.assertEqual(
            exported["name"],
            "free_lemonade_served",
        )

    def test_boundary_serialization_is_detached(
        self
    ):
        reservoir = LemonadeReservoir()
        profile = self._profile(
            acidity=1.25,
            source_names=("first",),
        )
        reservoir.add_lemonade(
            amount_litres=1.0,
            profile=profile,
        )

        public_state = reservoir.public_state
        public_state["current_profile"][
            "traits"
        ]["acidity"] = 99.0

        self.assertEqual(
            reservoir.current_profile
            .traits.acidity,
            1.25,
        )

        served = reservoir.serve(
            drinker_name="guest",
            location="bar",
        )
        snapshot = served.to_dict()
        snapshot["lemonade_profile"][
            "traits"
        ]["acidity"] = 77.0

        self.assertEqual(
            reservoir.current_profile
            .traits.acidity,
            1.25,
        )


if __name__ == "__main__":
    unittest.main()
