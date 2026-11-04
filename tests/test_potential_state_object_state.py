import unittest
from types import SimpleNamespace

from core.actualization.possibility import Possibility
from core.actualization.potential import Potential
from core.actualization.potential_state import (
    PotentialState,
)
from core.existence.history import (
    History,
    HistoryRecord,
)
from core.actualization.cycle import ActualizationCycle
from core.actualization.cycle_state import (
    ActualizationCycleState,
)
from core.actualization.potential_blueprint import (
    PotentialBlueprint,
)


class PotentialStateObjectStateTests(
    unittest.TestCase
):

    def make_potential(self):
        return Potential(
            possibility=Possibility(
                name="test_potential",
                probability=1.0,
                mandatory=True,
            ),
            cycle_id="cycle_test",
        )

    def test_potential_starts_open_as_enum(self):
        potential = self.make_potential()

        self.assertIs(
            potential.state,
            PotentialState.OPEN,
        )
        self.assertTrue(
            potential.is_open
        )
        self.assertEqual(
            potential.public_state["state"],
            "open",
        )

    def test_potential_captures_nested_context(self):
        external_context = {
            "nested": {
                "values": ["original"],
            },
        }

        potential = Potential(
            possibility=Possibility(
                name="capture_test",
                probability=1.0,
            ),
            cycle_id="cycle_test",
            context=external_context,
        )

        external_context["nested"]["values"].append(
            "external_change"
        )

        self.assertEqual(
            potential.context["nested"]["values"],
            ["original"],
        )

        self.assertIsNot(
            potential.context,
            external_context,
        )

        self.assertIsNot(
            potential.context["nested"],
            external_context["nested"],
        )

    def test_potentials_do_not_share_input_context(self):
        shared_context = {
            "nested": {
                "values": ["original"],
            },
        }

        first = Potential(
            possibility=Possibility(
                name="first",
                probability=1.0,
            ),
            cycle_id="cycle_test",
            context=shared_context,
        )

        second = Potential(
            possibility=Possibility(
                name="second",
                probability=1.0,
            ),
            cycle_id="cycle_test",
            context=shared_context,
        )

        first.context["nested"]["values"].append(
            "first_only"
        )

        self.assertEqual(
            first.context["nested"]["values"],
            ["original", "first_only"],
        )

        self.assertEqual(
            second.context["nested"]["values"],
            ["original"],
        )

        self.assertEqual(
            shared_context["nested"]["values"],
            ["original"],
        )

        self.assertIsNot(
            first.context["nested"],
            second.context["nested"],
        )

    def test_history_uses_potential_owned_context(self):
        external_context = {
            "nested": {
                "count": 1,
            },
        }

        potential = Potential(
            possibility=Possibility(
                name="owned_history",
                probability=1.0,
                mandatory=True,
            ),
            cycle_id="cycle_test",
            context=external_context,
        )

        external_context["nested"]["count"] = 99

        potential.mark_actualized()

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[],
            potentials=[potential],
        )

        self.assertEqual(
            potential.context["nested"]["count"],
            1,
        )

        self.assertEqual(
            record.actualized[0]["context"][
                "nested"
            ]["count"],
            1,
        )

        self.assertEqual(
            record.potential_blueprints[0].context[
                "nested"
            ]["count"],
            1,
        )

        self.assertEqual(
            record.public_state["actualized"][0][
                "context"
            ]["nested"]["count"],
            1,
        )

    def test_potential_public_state_detaches_nested_context(self):
        potential = Potential(
            possibility=Possibility(
                name="snapshot_test",
                probability=1.0,
                mandatory=True,
            ),
            cycle_id="cycle_test",
            context={
                "nested": {
                    "values": ["original"],
                },
            },
        )

        first = potential.public_state
        second = potential.public_state

        first["context"]["nested"]["values"].append(
            "snapshot_only"
        )

        self.assertEqual(
            potential.context["nested"]["values"],
            ["original"],
        )

        self.assertEqual(
            second["context"]["nested"]["values"],
            ["original"],
        )

        self.assertEqual(
            potential.public_state["context"]["nested"]["values"],
            ["original"],
        )

    def test_actualized_history_detaches_live_context(self):
        potential = Potential(
            possibility=Possibility(
                name="history_snapshot_test",
                probability=1.0,
                mandatory=True,
            ),
            cycle_id="cycle_test",
            context={
                "nested": {
                    "count": 1,
                },
            },
        )

        potential.mark_actualized()

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[],
            potentials=[potential],
        )

        potential.context["nested"]["count"] = 99

        self.assertEqual(
            record.actualized[0]["context"][
                "nested"
            ]["count"],
            1,
        )

        self.assertEqual(
            potential.context["nested"]["count"],
            99,
        )

    def test_mark_actualized_sets_enum(self):
        potential = self.make_potential()

        self.assertTrue(
            potential.mark_actualized()
        )
        self.assertIs(
            potential.state,
            PotentialState.ACTUALIZED,
        )
        self.assertFalse(
            potential.is_open
        )
        self.assertEqual(
            potential.public_state["state"],
            "actualized",
        )

    def test_mark_unrealized_sets_enum(self):
        potential = self.make_potential()

        self.assertTrue(
            potential.mark_unrealized()
        )
        self.assertIs(
            potential.state,
            PotentialState.UNREALIZED,
        )
        self.assertFalse(
            potential.is_open
        )
        self.assertEqual(
            potential.public_state["state"],
            "unrealized",
        )

    def test_string_state_is_rejected(self):
        potential = self.make_potential()

        with self.assertRaises(TypeError):
            potential.state = "actualized"

    def test_blueprint_captures_nested_context(self):
        original_context = {
            "nested": {
                "values": ["original"],
            },
        }

        blueprint = PotentialBlueprint(
            name="capture_test",
            probability=1.0,
            action=None,
            mandatory=True,
            available=True,
            context=original_context,
        )

        original_context["nested"]["values"].append(
            "changed"
        )

        self.assertEqual(
            blueprint.context["nested"]["values"],
            ["original"],
        )

        self.assertEqual(
            blueprint.public_state["context"][
                "nested"
            ]["values"],
            ["original"],
        )

    def test_history_blueprint_ignores_live_context_changes(self):
        potential = Potential(
            possibility=Possibility(
                name="history_capture",
                probability=1.0,
                mandatory=True,
            ),
            cycle_id="cycle_test",
            context={
                "nested": {
                    "count": 1,
                },
            },
        )

        potential.mark_actualized()

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[],
            potentials=[potential],
        )

        potential.context["nested"]["count"] = 99

        blueprint = record.potential_blueprints[0]

        self.assertEqual(
            blueprint.context["nested"]["count"],
            1,
        )

        self.assertEqual(
            record.public_state[
                "potential_blueprints"
            ][0]["context"]["nested"]["count"],
            1,
        )

        restored = blueprint.create_potential(
            cycle_id="cycle_replay",
        )

        self.assertEqual(
            restored.context["nested"]["count"],
            1,
        )

    def test_restored_potentials_have_independent_context(self):
        blueprint = PotentialBlueprint(
            name="replay_test",
            probability=1.0,
            action=None,
            mandatory=True,
            available=True,
            context={
                "nested": {
                    "values": ["original"],
                },
            },
        )

        first = blueprint.create_potential(
            cycle_id="cycle_a",
        )

        second = blueprint.create_potential(
            cycle_id="cycle_b",
        )

        first.context["nested"]["values"].append(
            "changed"
        )

        self.assertEqual(
            first.context["nested"]["values"],
            ["original", "changed"],
        )

        self.assertEqual(
            second.context["nested"]["values"],
            ["original"],
        )

        self.assertEqual(
            blueprint.context["nested"]["values"],
            ["original"],
        )

        self.assertIsNot(
            first.context["nested"],
            second.context["nested"],
        )

    def test_blueprint_public_state_detaches_nested_context(self):
        blueprint = PotentialBlueprint(
            name="test",
            probability=1.0,
            action=None,
            mandatory=False,
            available=True,
            context={
                "nested": {
                    "count": 1,
                },
            },
        )

        first = blueprint.public_state
        second = blueprint.public_state

        first["context"]["nested"]["count"] = 99

        self.assertEqual(
            blueprint.context["nested"]["count"],
            1,
        )

        self.assertEqual(
            second["context"]["nested"]["count"],
            1,
        )

        self.assertEqual(
            blueprint.public_state["context"]["nested"]["count"],
            1,
        )

    def test_history_blueprint_snapshot_is_detached(self):
        potential = Potential(
            possibility=Possibility(
                name="history_test",
                probability=1.0,
                mandatory=True,
            ),
            cycle_id="cycle_test",
            context={
                "nested": {
                    "count": 1,
                },
            },
        )

        potential.mark_actualized()

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[],
            potentials=[potential],
        )

        snapshot = record.public_state

        snapshot["potential_blueprints"][0][
            "context"
        ]["nested"]["count"] = 99

        self.assertEqual(
            record.potential_blueprints[0].context[
                "nested"
            ]["count"],
            1,
        )

        self.assertEqual(
            record.public_state["potential_blueprints"][0][
                "context"
            ]["nested"]["count"],
            1,
        )

    def test_history_capture_ignores_source_event_mutation(self):
        event = SimpleNamespace(
            name="captured_event",
            details={
                "nested": {
                    "count": 1,
                },
            },
        )

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[event],
            potentials=[],
        )

        event.details["nested"]["count"] = 99

        self.assertIs(
            record.events[0],
            event,
        )

        self.assertEqual(
            record.events[0].details[
                "nested"
            ]["count"],
            99,
        )

        snapshot = record.public_state

        self.assertEqual(
            snapshot["events"][0].details[
                "nested"
            ]["count"],
            1,
        )

        snapshot["events"][0].details[
            "nested"
        ]["count"] = 200

        self.assertEqual(
            record.public_state["events"][0].details[
                "nested"
            ]["count"],
            1,
        )

    def test_history_capture_preserves_event_aliases(self):
        event = SimpleNamespace(
            name="shared_event",
            details={
                "values": ["original"],
            },
        )

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[event, event],
            potentials=[],
        )

        event.details["values"].append(
            "live_change"
        )

        snapshot = record.public_state

        self.assertIs(
            record.events[0],
            event,
        )

        self.assertIs(
            record.events[1],
            event,
        )

        self.assertIs(
            snapshot["events"][0],
            snapshot["events"][1],
        )

        self.assertIsNot(
            snapshot["events"][0],
            event,
        )

        self.assertEqual(
            snapshot["events"][0].details["values"],
            ["original"],
        )

        snapshot["events"][0].details[
            "values"
        ].append("snapshot_only")

        self.assertEqual(
            snapshot["events"][1].details["values"],
            ["original", "snapshot_only"],
        )

        self.assertEqual(
            record.public_state["events"][0].details[
                "values"
            ],
            ["original"],
        )

    def test_history_collection_captures_event_at_record_time(self):
        event = SimpleNamespace(
            name="collection_event",
            details={
                "numbers": [1],
            },
        )

        cycle = ActualizationCycle(
            cycle_id="cycle_test",
        )

        cycle.state = ActualizationCycleState.RESOLVED

        history = History()

        record = history.record_cycle(
            cycle=cycle,
            events=[event],
        )

        event.details["numbers"].append(2)

        self.assertIs(
            history.latest,
            record,
        )

        self.assertIs(
            record.events[0],
            event,
        )

        self.assertEqual(
            record.events[0].details["numbers"],
            [1, 2],
        )

        self.assertEqual(
            history.public_state["records"][0][
                "events"
            ][0].details["numbers"],
            [1],
        )

    def test_history_event_snapshot_is_detached(self):
        event = SimpleNamespace(
            name="test_event",
            details={
                "nested": {
                    "count": 1,
                },
            },
        )

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[event],
            potentials=[],
        )

        first = record.public_state
        second = record.public_state

        first["events"][0].details[
            "nested"
        ]["count"] = 99

        self.assertIs(record.events[0], event)

        self.assertIsNot(
            first["events"][0],
            event,
        )

        self.assertEqual(
            event.details["nested"]["count"],
            1,
        )

        self.assertEqual(
            second["events"][0].details[
                "nested"
            ]["count"],
            1,
        )

    def test_history_collection_event_snapshot_is_detached(self):
        event = SimpleNamespace(
            name="collection_event",
            details={
                "observations": ["original"],
            },
        )

        cycle = ActualizationCycle(
            cycle_id="cycle_test",
        )

        cycle.state = ActualizationCycleState.RESOLVED

        history = History()

        record = history.record_cycle(
            cycle=cycle,
            events=[event],
        )

        snapshot = history.public_state

        snapshot["records"][0]["events"][0].details[
            "observations"
        ].append("snapshot_only")

        self.assertIs(history.latest, record)
        self.assertIs(record.events[0], event)

        self.assertEqual(
            event.details["observations"],
            ["original"],
        )

        self.assertEqual(
            history.public_state["records"][0][
                "events"
            ][0].details["observations"],
            ["original"],
        )

    def test_history_event_snapshot_preserves_aliases(self):
        event = SimpleNamespace(
            name="shared_event",
            details={
                "values": [],
            },
        )

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[event, event],
            potentials=[],
        )

        snapshot = record.public_state

        self.assertIs(
            record.events[0],
            event,
        )

        self.assertIs(
            record.events[1],
            event,
        )

        self.assertIs(
            snapshot["events"][0],
            snapshot["events"][1],
        )

        self.assertIsNot(
            snapshot["events"][0],
            event,
        )

        snapshot["events"][0].details[
            "values"
        ].append("snapshot_only")

        self.assertEqual(
            snapshot["events"][1].details[
                "values"
            ],
            ["snapshot_only"],
        )

        self.assertEqual(
            event.details["values"],
            [],
        )

    def test_actualized_record_snapshot_is_independent(self):
        potential = Potential(
            possibility=Possibility(
                name="actualized_snapshot",
                probability=1.0,
                mandatory=True,
            ),
            cycle_id="cycle_test",
            context={
                "nested": {
                    "values": ["original"],
                },
            },
        )

        potential.mark_actualized()

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[],
            potentials=[potential],
        )

        first = record.public_state
        second = record.public_state

        first["actualized"][0]["context"][
            "nested"
        ]["values"].append("snapshot_only")

        self.assertEqual(
            record.actualized[0]["context"][
                "nested"
            ]["values"],
            ["original"],
        )

        self.assertEqual(
            second["actualized"][0]["context"][
                "nested"
            ]["values"],
            ["original"],
        )

    def test_unrealized_record_snapshot_is_independent(self):
        potential = Potential(
            possibility=Possibility(
                name="unrealized_snapshot",
                probability=0.0,
            ),
            cycle_id="cycle_test",
            context={
                "nested": {
                    "count": 1,
                },
            },
        )

        potential.mark_unrealized()

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[],
            potentials=[potential],
        )

        snapshot = record.public_state

        snapshot["unrealized"][0]["context"][
            "nested"
        ]["count"] = 99

        self.assertEqual(
            record.unrealized[0]["context"][
                "nested"
            ]["count"],
            1,
        )

        self.assertEqual(
            record.public_state["unrealized"][0][
                "context"
            ]["nested"]["count"],
            1,
        )

    def test_history_public_state_preserves_record(self):
        potential = Potential(
            possibility=Possibility(
                name="history_snapshot",
                probability=1.0,
                mandatory=True,
            ),
            cycle_id="cycle_test",
            context={
                "nested": {
                    "count": 1,
                },
            },
        )

        cycle = ActualizationCycle(
            cycle_id="cycle_test",
        )

        cycle.add_potential(potential)
        potential.mark_actualized()

        cycle.state = ActualizationCycleState.RESOLVED

        history = History()

        record = history.record_cycle(
            cycle=cycle,
            events=[],
        )

        snapshot = history.public_state

        snapshot["records"][0]["actualized"][0][
            "context"
        ]["nested"]["count"] = 99

        self.assertEqual(
            record.actualized[0]["context"][
                "nested"
            ]["count"],
            1,
        )

        self.assertEqual(
            history.public_state["records"][0][
                "actualized"
            ][0]["context"]["nested"]["count"],
            1,
        )

        self.assertIs(
            history.latest,
            record,
        )

    def test_history_record_classifies_enum_states(
        self
    ):
        actualized = self.make_potential()
        unrealized = self.make_potential()

        actualized.mark_actualized()
        unrealized.mark_unrealized()

        record = HistoryRecord(
            cycle_id="cycle_test",
            events=[],
            potentials=[
                actualized,
                unrealized,
            ],
        )

        self.assertEqual(
            [
                state["state"]
                for state in record.actualized
            ],
            [
                "actualized",
            ],
        )

        self.assertEqual(
            [
                state["state"]
                for state in record.unrealized
            ],
            [
                "unrealized",
            ],
        )

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in PotentialState
            },
            {
                "open",
                "actualized",
                "unrealized",
            },
        )


if __name__ == "__main__":
    unittest.main()
