from core.entity.components import SpatialVector3
import unittest
from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import UniverseBootstrap
from universe.bootstraps.entity_bootstrap import EntityBootstrap
from cats.kitten_growth_state import (
    KittenGrowthAppliedEvent,
    KittenGrowthState,
)
from meeting_place.cat_bar_lifecycle_state import (
    CatBartenderMeowExchangeEvent,
    CatDrankMilkAtBarEvent,
    CatMilkServiceFailedEvent,
)
from meeting_place.cat_meow_event_state import (
    BartenderCatMeowEvent,
    BartenderMeowReplyEvent,
    BouncerCatAllowedEvent,
    BouncerCatMeowEvent,
    BouncerCatMeowRecognitionEvent,
)

class QuantumBoxCatBarMeowTests(unittest.TestCase):

    def setUp(self):
        registry = UniverseRegistry()
        self.universe = Universe()
        root_transition, self.layers, idea_universe = UniverseBootstrap(registry, self.universe).run()
        EntityBootstrap(self.universe, idea_universe, root_transition).run()
        self.bar = self.layers.get('meeting')
        manifestation = self.universe.manifest_cat(name='quantum_kitten', source='quantum_box_opened', position=SpatialVector3(x=10.0, y=5.0, z=-2.0))
        self.cat = manifestation.cat

    def test_cat_meows_at_bouncer_before_entry(self):
        self.bar.add_entity(
            self.cat
        )

        history = (
            self.bar
            .bouncer
            .cat_meow_history
        )

        names = [
            event.name
            for event
            in history
        ]

        self.assertIn(
            'cat_meowed_at_bouncer',
            names,
        )

        self.assertIn(
            'bouncer_recognized_cat_meow',
            names,
        )

        self.assertIn(
            'bouncer_allowed_cat',
            names,
        )

        self.assertIsInstance(
            history[0],
            BouncerCatMeowEvent,
        )

        self.assertIsInstance(
            history[1],
            BouncerCatMeowRecognitionEvent,
        )

        self.assertIsInstance(
            history[2],
            BouncerCatAllowedEvent,
        )

        recognition = next(
            event
            for event
            in history
            if (
                event.name
                == 'bouncer_recognized_cat_meow'
            )
        )

        self.assertTrue(
            recognition.recognized
        )

        for event, key in (
            (
                history[0],
                'cat',
            ),
            (
                recognition,
                'recognized',
            ),
            (
                history[2],
                'allowed',
            ),
        ):
            for mapping_method in (
                'get',
                'keys',
                'items',
                'values',
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
                _ = event[key]

        self.assertIn(
            self.cat,
            self.bar.entities,
        )

    def test_bartender_replies_meow_and_serves_milk(self):
        self.bar.add_entity(
            self.cat
        )

        history = (
            self.bar
            .bartender
            .cat_meow_history
        )

        names = [
            event.name
            for event
            in history
        ]

        self.assertIn(
            'cat_meowed_at_bartender',
            names,
        )

        self.assertIn(
            'bartender_replied_meow',
            names,
        )

        self.assertIsInstance(
            history[0],
            BartenderCatMeowEvent,
        )

        self.assertIsInstance(
            history[1],
            BartenderMeowReplyEvent,
        )

        self.assertTrue(
            history[0].understood
        )

        self.assertTrue(
            history[1].reply
        )

        for event, key in (
            (
                history[0],
                'understood',
            ),
            (
                history[1],
                'reply',
            ),
        ):
            for mapping_method in (
                'get',
                'keys',
                'items',
                'values',
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
                _ = event[key]

        self.assertEqual(
            self.bar
            .bar_counter
            .milk_bowl
            .contains,
            'milk',
        )

        exchange = next(
            event
            for event
            in self.bar.events
            if isinstance(
                event,
                CatBartenderMeowExchangeEvent,
            )
        )

        self.assertEqual(
            exchange.cat,
            self.cat.name,
        )

        self.assertIsInstance(
            exchange.cat_meow,
            BartenderCatMeowEvent,
        )

        self.assertIsInstance(
            exchange.bartender_meow,
            BartenderMeowReplyEvent,
        )

        self.assertFalse(
            hasattr(
                exchange,
                'get',
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = exchange[
                'cat'
            ]

    def test_bar_milk_makes_quantum_kitten_grow(self):
        size_before = self.cat.size
        strength_before = self.cat.strength
        self.bar.add_entity(self.cat)
        self.assertGreater(self.cat.size, size_before)
        self.assertGreater(self.cat.strength, strength_before)
        growth = self.cat.growth
        self.assertIsInstance(
            growth,
            KittenGrowthState,
        )
        self.assertEqual(
            growth.milk_feedings,
            1,
        )
        milk_event = next(
            event
            for event
            in self.bar.events
            if isinstance(
                event,
                CatDrankMilkAtBarEvent,
            )
        )

        self.assertTrue(
            milk_event.served
        )

        self.assertIsInstance(
            milk_event.growth,
            KittenGrowthAppliedEvent,
        )

        self.assertTrue(
            milk_event.growth.grew
        )

        self.assertFalse(
            hasattr(
                milk_event,
                'get',
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = milk_event[
                'served'
            ]
    def test_missing_milk_uses_object_event(
        self
    ):
        self.bar.fridge.items.pop(
            "milk"
        )

        result = (
            self.bar
            .serve_cat_milk(
                self.cat
            )
        )

        self.assertIsInstance(
            result,
            CatMilkServiceFailedEvent,
        )

        self.assertFalse(
            result.served
        )

        self.assertEqual(
            result.reason,
            "milk_missing",
        )

        event = (
            self.bar.events[-1]
        )

        self.assertIs(
            result,
            event,
        )

        self.assertEqual(
            event.cat,
            self.cat.name,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
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
                "reason"
            ]


if __name__ == '__main__':
    unittest.main()
