import random
from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType

from universe.logger import UniverseLogger


def _freeze_rotation_payload(value):
    if isinstance(value, dict):
        return MappingProxyType({
            key: _freeze_rotation_payload(item)
            for key, item in value.items()
        })

    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):
        return tuple(
            _freeze_rotation_payload(item)
            for item in value
        )

    if isinstance(value, set):
        return frozenset(
            _freeze_rotation_payload(item)
            for item in value
        )

    return deepcopy(value)


def _thaw_rotation_payload(value):
    if isinstance(
        value,
        MappingProxyType,
    ):
        return {
            key: _thaw_rotation_payload(item)
            for key, item in value.items()
        }

    if isinstance(value, tuple):
        return [
            _thaw_rotation_payload(item)
            for item in value
        ]

    if isinstance(value, frozenset):
        return [
            _thaw_rotation_payload(item)
            for item in value
        ]

    return deepcopy(value)


@dataclass(slots=True, frozen=True)
class D20RotationEvent:

    scope: str
    rotated_count: int
    artifact_names: tuple[str, ...]
    results: tuple[object, ...]
    layer: str | None = None

    def __post_init__(self):
        scope = str(
            self.scope
        )

        if scope not in {
            "random",
            "all",
            "layer",
        }:
            raise ValueError(
                "Unsupported d20 rotation scope."
            )

        object.__setattr__(
            self,
            "scope",
            scope,
        )

        object.__setattr__(
            self,
            "rotated_count",
            int(
                self.rotated_count
            ),
        )

        object.__setattr__(
            self,
            "artifact_names",
            tuple(
                str(name)
                for name
                in self.artifact_names
            ),
        )

        object.__setattr__(
            self,
            "results",
            tuple(
                _freeze_rotation_payload(
                    result
                )
                for result
                in self.results
            ),
        )

        if self.layer is not None:
            object.__setattr__(
                self,
                "layer",
                str(self.layer),
            )

        if (
            self.rotated_count
            != len(self.results)
        ):
            raise ValueError(
                "D20 rotation count must match "
                "the result count."
            )

        if (
            self.rotated_count
            != len(
                self.artifact_names
            )
        ):
            raise ValueError(
                "D20 rotation count must match "
                "the artifact name count."
            )

    def to_dict(self):
        snapshot = {
            "scope": self.scope,
            "rotated_count": (
                self.rotated_count
            ),
            "artifact_names": list(
                self.artifact_names
            ),
            "results": [
                _thaw_rotation_payload(
                    result
                )
                for result
                in self.results
            ],
        }

        if self.layer is not None:
            snapshot[
                "layer"
            ] = self.layer

        return snapshot


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
                "roll()."
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
            artifact,
            rng=rng
        )

        event = D20RotationEvent(
            scope="random",
            rotated_count=1,
            artifact_names=(
                self._artifact_name(
                    artifact
                ),
            ),
            results=(
                result,
            ),
        )

        self.record_rotation(
            event
        )

        return event.to_dict()

    def rotate_all(self, rng=None):
        results = []
        artifact_names = []

        for artifact in list(self.artifacts):
            artifact_names.append(
                self._artifact_name(artifact)
            )

            results.append(
                self._rotate(
                    artifact,
                    rng=rng
                )
            )

        event = D20RotationEvent(
            scope="all",
            rotated_count=len(
                results
            ),
            artifact_names=tuple(
                artifact_names
            ),
            results=tuple(
                results
            ),
        )

        self.record_rotation(
            event
        )

        return event.to_dict()

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

        event = D20RotationEvent(
            scope="layer",
            layer=layer,
            rotated_count=len(
                results
            ),
            artifact_names=tuple(
                self._artifact_name(
                    artifact
                )
                for artifact
                in matches
            ),
            results=tuple(
                results
            ),
        )

        self.record_rotation(
            event
        )

        return event.to_dict()

    def record_rotation(
        self,
        event,
    ):
        if not isinstance(
            event,
            D20RotationEvent,
        ):
            raise TypeError(
                "D20 rotation history requires "
                "a D20RotationEvent object."
            )

        self.rotation_history.append(
            event
        )

        return event

    def _rotate(self, artifact, rng=None):
        roll = getattr(
            artifact,
            "roll",
            None
        )

        if callable(roll):
            return roll(rng=rng)

        raise TypeError(
            "Artifact lost its d20 roll method."
        )

    def _can_rotate(self, artifact):
        return callable(
            getattr(
                artifact,
                "roll",
                None
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
