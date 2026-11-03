from dataclasses import FrozenInstanceError, replace

import pytest

from idea_universe import IdeaUniverse
from idea_universe.primordial_nebula import PrimordialNebula
from idea_universe.primordial_creation_history import (
    PrimordialCreationHistory,
    PrimordialNebulaPhysicsEvent,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


def layer(create=True):
    universe = Universe(universe_id="atomic_boundary_regression")
    universe.universe_registry = UniverseRegistry()
    result = IdeaUniverse(universe)
    result.stellar_epoch_started = True
    if create:
        result.run_primordial_stellar_epoch(star_count=1)
    return result


def test_invalid_size_is_atomic():
    source = layer()
    nebula = source.primordial_nebula
    history = source.primordial_creation_history

    with pytest.raises(TypeError):
        nebula.size = True

    with pytest.raises(ValueError):
        nebula.size = float("nan")

    assert nebula.size == 0.0
    assert source.primordial_creation_history is history


def test_owned_state_cannot_be_modified_directly():
    source = layer()
    nebula = source.primordial_nebula
    history = source.primordial_creation_history

    with pytest.raises(TypeError):
        nebula.elemental_potentials["carbon"] = 99.0

    with pytest.raises(RuntimeError):
        nebula.tick_count = 7

    with pytest.raises(RuntimeError):
        nebula.current_liquid_hydrocarbon_level = 99.0

    snapshot = nebula.state
    snapshot.size = 50.0
    snapshot.elemental_potentials["carbon"] = 99.0

    nebula.source_remnants[0].elemental_potentials[
        "carbon"
    ] = 99.0

    assert nebula.size == 0.0
    assert nebula.tick_count == 0
    assert nebula.elemental_potentials["carbon"] == 1.0
    assert source.primordial_creation_history is history


def test_elemental_changes_are_replayed():
    source = layer()
    nebula = source.primordial_nebula

    nebula.set_elemental_potential("carbon", 4.0)
    nebula.set_elemental_potential("hydrogen", 5.0)

    assert nebula.form_hydrocarbons() == 4.0

    history = source.primordial_creation_history
    events = [
        event for event in history.events
        if isinstance(event, PrimordialNebulaPhysicsEvent)
    ]

    assert [e.operation for e in events] == [
        "set_elemental_potential",
        "set_elemental_potential",
        "form_hydrocarbons",
    ]

    with pytest.raises(FrozenInstanceError):
        events[0].element = "forged"

    target = layer(create=False)
    _, restored = target.replay_primordial_creation_history(
        history
    )

    assert dict(restored.elemental_potentials) == dict(
        nebula.elemental_potentials
    )

    restored.set_elemental_potential("carbon", 3.0)

    assert len(target.primordial_creation_history.events) == (
        len(history.events) + 1
    )


def test_failed_recorder_preserves_state():
    source = layer()
    nebula = source.primordial_nebula

    nebula.size = 100.0
    nebula.form_hydrocarbons()
    nebula.form_liquid_hydrocarbons()
    nebula.record_liquid_hydrocarbon_level(100.0)
    nebula.record_liquid_hydrocarbon_level(130.0)

    state = nebula.public_state
    history = source.primordial_creation_history
    recorder = nebula._physics_recorder

    def fail(*args):
        raise RuntimeError("Injected recorder failure")

    nebula._physics_recorder = fail

    try:
        actions = (
            lambda: setattr(nebula, "size", 150.0),
            nebula.form_hydrocarbons,
            nebula.form_liquid_hydrocarbons,
            lambda: nebula.record_liquid_hydrocarbon_level(140.0),
            lambda: nebula.mine_liquid_hydrocarbons(3.0),
            nebula.tick,
            lambda: nebula.set_elemental_potential("carbon", 9.0),
        )

        for action in actions:
            with pytest.raises(RuntimeError, match="Injected"):
                action()

            assert nebula.public_state == state
            assert source.primordial_creation_history is history
    finally:
        nebula._physics_recorder = recorder


def test_invalid_elemental_input_is_atomic():
    source = layer()
    nebula = source.primordial_nebula
    history = source.primordial_creation_history

    with pytest.raises(TypeError):
        nebula.set_elemental_potential("carbon", True)

    with pytest.raises(ValueError):
        nebula.set_elemental_potential("", 4.0)

    with pytest.raises(ValueError):
        nebula.set_elemental_potential("carbon", float("nan"))

    assert nebula.elemental_potentials["carbon"] == 1.0
    assert source.primordial_creation_history is history


def test_forged_elemental_result_is_rejected():
    source = layer()
    source.primordial_nebula.set_elemental_potential(
        "carbon", 4.0
    )

    history = source.primordial_creation_history
    events = history.events[:-1] + (
        replace(history.events[-1], result=999.0),
    )

    forged = PrimordialCreationHistory(
        scope=history.scope,
        events=events,
    )

    target = layer(create=False)

    with pytest.raises(ValueError, match="result mismatch"):
        target.replay_primordial_creation_history(forged)

    assert target.primordial_nebula is None
    assert target.starry_sky == []
    assert target.primordial_creation_history.events == ()


def test_unowned_nebula_remains_compatible():
    nebula = PrimordialNebula()

    assert nebula.state is nebula.primordial_nebula_state

    nebula.elemental_potentials["carbon"] = 9.0
    nebula.tick_count = 7

    assert nebula.elemental_potentials["carbon"] == 9.0
    assert nebula.tick_count == 7
