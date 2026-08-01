import random

from universe.logger import UniverseLogger


class D20Registry:

    def __init__(self):
        self.name = "d20_registry"
        self.artifacts = []
        self.rotation_history = []

        UniverseLogger.boot(
            "D20 REGISTRY CREATED"
        )

    def register(self, artifact):
        if artifact in self.artifacts:
            return False

        if not self._can_rotate(artifact):
            raise TypeError(
                "Registered d20 artifact must provide "
                "roll_secretly() or rotate_secretly()."
            )

        self.artifacts.append(artifact)

        return True

    def unregister(self, artifact):
        if artifact not in self.artifacts:
            return False

        self.artifacts.remove(artifact)
        return True

    def rotate_random(self, rng=None):
        rng = rng or random

        if not self.artifacts:
            return {
                "scope": "random",
                "rotated_count": 0,
                "results": []
            }

        artifact = rng.choice(
            self.artifacts
        )

        result = self._rotate(
            artifact
        )

        event = {
            "scope": "random",
            "rotated_count": 1,
            "artifact_names": [
                self._artifact_name(artifact)
            ],
            "results": [result]
        }

        self.rotation_history.append(event)

        return event

    def rotate_all(self):
        results = []
        artifact_names = []

        for artifact in list(self.artifacts):
            artifact_names.append(
                self._artifact_name(artifact)
            )

            results.append(
                self._rotate(artifact)
            )

        event = {
            "scope": "all",
            "rotated_count": len(results),
            "artifact_names": artifact_names,
            "results": results
        }

        self.rotation_history.append(event)

        return event

    def rotate_layer(
        self,
        layer
    ):
        matches = [
            artifact
            for artifact in self.artifacts
            if getattr(
                artifact,
                "location",
                None
            ) == layer
            or getattr(
                artifact,
                "layer",
                None
            ) == layer
        ]

        results = [
            self._rotate(artifact)
            for artifact in matches
        ]

        event = {
            "scope": "layer",
            "layer": layer,
            "rotated_count": len(results),
            "artifact_names": [
                self._artifact_name(artifact)
                for artifact in matches
            ],
            "results": results
        }

        self.rotation_history.append(event)

        return event

    def _rotate(self, artifact):
        rotate = getattr(
            artifact,
            "rotate_secretly",
            None
        )

        if callable(rotate):
            return rotate()

        roll = getattr(
            artifact,
            "roll_secretly",
            None
        )

        if callable(roll):
            return roll()

        raise TypeError(
            "Artifact lost its d20 rotation method."
        )

    def _can_rotate(self, artifact):
        return (
            callable(
                getattr(
                    artifact,
                    "rotate_secretly",
                    None
                )
            )
            or callable(
                getattr(
                    artifact,
                    "roll_secretly",
                    None
                )
            )
        )

    def _artifact_name(self, artifact):
        return getattr(
            artifact,
            "name",
            artifact.__class__.__name__
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "artifact_count": len(
                self.artifacts
            ),
            "artifact_names": [
                self._artifact_name(artifact)
                for artifact in self.artifacts
            ],
            "rotation_count": len(
                self.rotation_history
            )
        }
