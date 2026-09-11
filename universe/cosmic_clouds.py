from copy import deepcopy

from universe.cosmic_cloud_state import (
    CosmicCloudFormationState,
)


class CosmicClouds:

    def __init__(self, universe):
        self.universe = universe
        self.name = "cosmic_clouds"
        self.type = "cosmic_structure_layer"
        self.state = "ready"

        self.clouds = []

        self.cosmic_cloud_state = (
            CosmicCloudFormationState()
        )

        self.public_state = self._build_public_state()

    def _build_public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "clouds": deepcopy(self.clouds),
            "cosmic_cloud_state": (
                self.cosmic_cloud_state.to_dict()
            ),
        }

    def _refresh_public_state(self):
        self.public_state = self._build_public_state()

    def form_germinal_clouds(self):
        return (
            self.universe
            .quantum_error_boundary.execute(
                operation=(
                    self._form_germinal_clouds_unprotected
                ),
                source_component="cosmic_clouds",
                source_operation="form_germinal_clouds",
            )
        )

    def _form_germinal_clouds_unprotected(self):
        primordial_elements = self.universe.world.get(
            "primordial_elements",
            {},
        )

        if "hydrogen" not in primordial_elements:
            self.state = "failed"

            print(
                "COSMIC CLOUD FORMATION FAILED: "
                "missing hydrogen or helium"
            )
            self.write_to_world()
            return self.public_state

        self.cosmic_cloud_state.hydrogen_available = True

        if "helium" not in primordial_elements:
            self.state = "failed"

            print(
                "COSMIC CLOUD FORMATION FAILED: "
                "missing hydrogen or helium"
            )
            self.write_to_world()
            return self.public_state

        self.cosmic_cloud_state.helium_available = True
        self.state = "formed"

        self.clouds.append({
            "name": "first_germinal_cloud",
            "type": "germinal_cloud",
            "state": "condensing",
            "composition": {
                "hydrogen": "dominant",
                "helium": "secondary",
                "trace_lithium": "trace",
            },
            "can_form_stars": True,
        })

        self.clouds.append({
            "name": "deep_germinal_cloud",
            "type": "germinal_cloud",
            "state": "quiet",
            "composition": {
                "hydrogen": "dominant",
                "helium": "secondary",
            },
            "can_form_stars": True,
        })

        self.cosmic_cloud_state.germinal_clouds_formed = (
            True
        )
        self.cosmic_cloud_state.star_formation_possible = (
            True
        )

        self.record_history()
        self.write_to_world()

        print("GERMINAL COSMIC CLOUDS FORMED")
        print("HYDROGEN AND HELIUM BEGIN TO GATHER")
        print("STAR FORMATION POTENTIAL CREATED")

        return self.public_state

    def record_history(self):
        history = self.universe.world.setdefault(
            "cosmic_history",
            [],
        )

        history.append({
            "name": "germinal_clouds_formed",
            "description": (
                "Hydrogen and helium gather into the first "
                "germinal clouds, preparing the universe for "
                "star formation."
            ),
        })

    def write_to_world(self):
        self._refresh_public_state()

        self.universe.world["cosmic_clouds"] = (
            self.public_state
        )
        self.universe.world["germinal_clouds"] = (
            self.clouds
        )
        self.universe.world["cosmic_cloud_state"] = (
            self.cosmic_cloud_state
        )
