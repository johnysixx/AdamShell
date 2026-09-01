import unittest
from types import SimpleNamespace

from core.entity.quantum_box import (
    QuantumBox,
    QuantumBoxCatTransferState,
    QuantumBoxCollapseState,
    QuantumBoxContentState,
    QuantumBoxCounterpartState,
    QuantumBoxEnergyState,
)


class QuantumBoxObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key
    ):
        for mapping_method in (
            'get',
            'keys',
            'items',
            'values',
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[key]

    def test_state_components_have_no_mapping_api(
        self
    ):
        box = QuantumBox()

        for value, key, expected_type in (
            (
                box.quantum_counterpart,
                'paired',
                QuantumBoxCounterpartState,
            ),
            (
                box.cat_transfer,
                'active',
                QuantumBoxCatTransferState,
            ),
            (
                box.energy,
                'available',
                QuantumBoxEnergyState,
            ),
            (
                box.content,
                'possibilities',
                QuantumBoxContentState,
            ),
            (
                box.collapse,
                'collapsed',
                QuantumBoxCollapseState,
            ),
        ):
            self.assertIsInstance(
                value,
                expected_type
            )
            self._assert_object_only(
                value,
                key
            )

    def test_pairing_mutates_same_objects(
        self
    ):
        source = QuantumBox()
        target = QuantumBox()
        source_state = (
            source.quantum_counterpart
        )
        target_state = (
            target.quantum_counterpart
        )

        event = source.pair_with(target)

        self.assertIs(
            source.quantum_counterpart,
            source_state
        )
        self.assertIs(
            target.quantum_counterpart,
            target_state
        )
        self.assertTrue(source_state.paired)
        self.assertEqual(
            source_state.box_id,
            target.id
        )
        self.assertTrue(event['paired'])

        previous = source.clear_counterpart()
        self.assertTrue(previous['paired'])
        previous['box_id'] = 'changed'

        self.assertFalse(source_state.paired)
        self.assertIsNone(source_state.box_id)
        self.assertTrue(target_state.paired)

    def test_cat_transfer_is_object_state(
        self
    ):
        source = QuantumBox()
        target = QuantumBox()
        source.pair_with(target)
        cat = SimpleNamespace(
            name='traveller',
            type='cat',
        )

        snapshot = source.begin_cat_transfer(
            cat=cat,
            target_box=target,
            tick=7,
        )

        self.assertTrue(
            source.cat_transfer.active
        )
        self.assertTrue(
            target.cat_transfer.active
        )
        self.assertEqual(
            source.cat_transfer.cat_name,
            'traveller'
        )
        self.assertEqual(
            source.cat_transfer.started_tick,
            7
        )
        self.assertIsInstance(
            snapshot,
            dict
        )
        snapshot['cat_name'] = 'changed'
        self.assertEqual(
            source.cat_transfer.cat_name,
            'traveller'
        )

    def test_transfer_completion_preserves_source_anchor(
        self
    ):
        transfer = QuantumBoxCatTransferState()
        transfer.begin(
            cat_name='traveller',
            source_box_id='source',
            target_box_id='target',
            source_layer='meeting_place',
            target_layer='quantum_layer',
            started_tick=7,
        )

        transfer.complete(
            clear_source=False
        )

        self.assertFalse(transfer.active)
        self.assertEqual(
            transfer.state,
            'completed'
        )
        self.assertEqual(
            transfer.source_box_id,
            'source'
        )
        self.assertEqual(
            transfer.source_layer,
            'meeting_place'
        )
        self.assertEqual(
            transfer.started_tick,
            7
        )
        self.assertIsNone(
            transfer.target_box_id
        )

    def test_energy_consumption_is_object_state(
        self
    ):
        box = QuantumBox()
        energy = box.energy

        snapshot = (
            box.consume_for_cat_transfer()
        )

        self.assertIs(box.energy, energy)
        self.assertFalse(energy.available)
        self.assertTrue(energy.consumed)
        self.assertEqual(
            energy.purpose,
            'cat_layer_transfer'
        )
        snapshot['available'] = True
        self.assertFalse(energy.available)

    def test_collapse_mutates_content_and_collapse_objects(
        self
    ):
        box = QuantumBox()
        content = box.content
        collapse = box.collapse

        event = box.resolve_state(
            result='cat',
            cause='observation',
            observer='pazuzu',
            tick=9,
        )

        self.assertIs(box.content, content)
        self.assertIs(box.collapse, collapse)
        self.assertEqual(
            content.resolved,
            'cat'
        )
        self.assertTrue(collapse.collapsed)
        self.assertEqual(
            collapse.cause,
            'observation'
        )
        self.assertEqual(
            collapse.observer,
            'pazuzu'
        )
        self.assertEqual(collapse.tick, 9)
        self.assertEqual(
            event['result'],
            'cat'
        )

    def test_public_state_is_detached_dict(
        self
    ):
        source = QuantumBox()
        target = QuantumBox()
        source.pair_with(target)

        snapshot = source.public_state
        snapshot['position']['x'] = 99.0
        snapshot['quantum_counterpart'][
            'paired'
        ] = False
        snapshot['cat_transfer'][
            'active'
        ] = True
        snapshot['energy'][
            'available'
        ] = False

        self.assertNotEqual(
            source.position['x'],
            99.0
        )
        self.assertTrue(
            source.quantum_counterpart.paired
        )
        self.assertFalse(
            source.cat_transfer.active
        )
        self.assertTrue(
            source.energy.available
        )


if __name__ == '__main__':
    unittest.main()
