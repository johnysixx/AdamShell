from universe.chemical_objects import Isotope
from universe.isotope_state import (
    IsotopeFormationState,
)
from universe.periodic_table import PeriodicTable


class Isotopes:

    def __init__(self, universe):
        self.universe = universe
        self.name = "isotopes"
        self.type = "isotope_layer"
        self.state = "ready"

        self.periodic_table = PeriodicTable(universe)
        self.isotopes = {}

        self.isotope_state = IsotopeFormationState()

        self.public_state = self._build_public_state()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "isotopes": {
                name: isotope.to_dict()
                for name, isotope in self.isotopes.items()
            },
            "isotope_state": (
                self.isotope_state.to_dict()
            ),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def form_reference_isotopes(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=(
                    self._form_reference_isotopes_unprotected
                ),
                source_component="isotopes",
                source_operation="form_reference_isotopes",
            )
        )

    def _form_reference_isotopes_unprotected(self):
        self.ensure_periodic_table()

        self.create_isotope(1, 1, "stable", ["atoms", "water"])
        self.create_isotope(1, 2, "stable", ["atoms", "heavy_water"])
        self.create_isotope(2, 4, "stable", ["atoms", "helium_gas"])

        self.create_isotope(6, 14, "radioactive", ["radiocarbon_dating"])
        self.create_isotope(19, 40, "radioactive", ["geological_time"])
        self.create_isotope(55, 133, "stable", ["atomic_time"])
        self.create_isotope(90, 232, "radioactive", ["geological_time"])
        self.create_isotope(92, 238, "radioactive", ["geological_time"])

        self.state = "formed"

        self.isotope_state.reference_isotopes_available = True
        (
            self.isotope_state
            .radioactive_isotopes_available
        ) = True
        (
            self.isotope_state
            .atomic_time_isotope_available
        ) = True
        self.isotope_state.isotope_count = len(
            self.isotopes
        )

        self.record_history()
        self.write_to_world()

        print("REFERENCE ISOTOPES FORMED")
        print("HYDROGEN-1 FORMED")
        print("DEUTERIUM FORMED")
        print("HELIUM-4 FORMED")
        print("CARBON-14 FORMED")
        print("CAESIUM-133 FORMED")
        print("RADIOACTIVE TIMEKEEPERS FORMED")

        return self.public_state

    def ensure_periodic_table(self):
        if not self.universe.world.get("elements_by_atomic_number"):
            self.periodic_table.build_known_table()

        self.isotope_state.periodic_table_available = True

    def create_isotope(self, atomic_number, mass_number, stability, future_use):
        element = self.periodic_table.get_element(atomic_number)

        isotope = Isotope(
            element=element,
            mass_number=mass_number,
            stability=stability,
            future_use=tuple(future_use),
        )

        self.isotopes[isotope.name] = isotope

        return isotope

    def record_history(self):
        history = self.universe.world.setdefault("cosmic_history", [])

        history.append({
            "name": "reference_isotopes_formed",
            "description": "Reference isotopes form when element nuclei contain specific numbers of neutrons."
        })

    def write_to_world(self):
        self._refresh_public_state()
        self.universe.world["isotopes"] = self.public_state
        self.universe.world["known_isotopes"] = self.isotopes
        self.universe.world["isotope_state"] = self.isotope_state
