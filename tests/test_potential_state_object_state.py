import unittest

from core.actualization.possibility import Possibility
from core.actualization.potential import Potential
from core.actualization.potential_state import (
    PotentialState,
)
from core.existence.history import HistoryRecord
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
