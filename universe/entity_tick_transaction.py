import random
from dataclasses import fields, is_dataclass

from universe.cronenberg_encounter_batch_transaction import (
    CronenbergEncounterBatchTransaction,
)


class EntityRuntimeSnapshot:
    """Capture supported in-memory entity object state."""

    # Bounded traversal with identity-based cycle detection.
    MAX_DEPTH = 32

    def __init__(self, universe):
        self.universe = universe
        self.records = []
        self.seen = set()

        for entity in tuple(universe.entities):
            self._capture(entity, 0)

    def _capture(self, value, depth):
        if depth > self.MAX_DEPTH:
            return

        if value is self.universe or value is None:
            return

        if isinstance(
            value, (str, bytes, int, float, bool, complex)
        ):
            return

        if callable(value):
            return

        identity = id(value)

        if identity in self.seen:
            return

        # Independent RNGs carry state outside __dict__.
        if isinstance(value, random.Random):
            self.seen.add(identity)
            self.records.append(
                ("rng", value, value.getstate())
            )
            return

        # Immutable containers can contain mutable objects.
        # Traverse their members without replacing the tuple
        # or frozenset itself.
        if isinstance(value, (tuple, frozenset)):
            self.seen.add(identity)

            for item in value:
                self._capture(item, depth + 1)

            return

        if isinstance(value, list):
            self.seen.add(identity)
            previous = tuple(value)
            self.records.append(
                ("list", value, previous)
            )

            for item in previous:
                self._capture(item, depth + 1)

            return

        if isinstance(value, dict):
            self.seen.add(identity)
            previous = tuple(value.items())
            self.records.append(
                ("dict", value, previous)
            )

            for key, item in previous:
                self._capture(key, depth + 1)
                self._capture(item, depth + 1)

            return

        if isinstance(value, set):
            self.seen.add(identity)
            previous = frozenset(value)
            self.records.append(
                ("set", value, previous)
            )

            for item in previous:
                self._capture(item, depth + 1)

            return

        try:
            attributes = vars(value)
        except TypeError:
            attributes = None

        if isinstance(attributes, dict):
            self.seen.add(identity)
            previous = tuple(attributes.items())

            self.records.append(
                ("object", attributes, previous)
            )

            for name, item in previous:
                if name in (
                    "universe",
                    "_universe",
                ):
                    continue

                self._capture(item, depth + 1)

        if attributes is None and is_dataclass(value) and not isinstance(
            value, type
        ):
            self.seen.add(identity)
            previous = tuple(
                (field.name, getattr(value, field.name))
                for field in fields(value)
            )

            self.records.append(
                ("dataclass", value, previous)
            )

            for _, item in previous:
                self._capture(item, depth + 1)

            return

        # Ordinary __slots__ objects, including inherited
        # slots and objects also defining __dict__.
        slot_names = []

        for cls in type(value).__mro__:
            declared = cls.__dict__.get("__slots__", ())

            if isinstance(declared, str):
                declared = (declared,)

            for name in declared:
                if name in ("__dict__", "__weakref__"):
                    continue

                if name.startswith("__") and not name.endswith("__"):
                    name = (
                        "_" + cls.__name__.lstrip("_") + name
                    )

                if name not in slot_names:
                    slot_names.append(name)

        if slot_names:
            self.seen.add(identity)
            previous = []

            for name in slot_names:
                try:
                    item = object.__getattribute__(
                        value, name
                    )
                except AttributeError:
                    previous.append((name, False, None))
                else:
                    previous.append((name, True, item))

            previous = tuple(previous)
            self.records.append(
                ("slots", value, previous)
            )

            for name, existed, item in previous:
                if existed and name not in (
                    "universe", "_universe"
                ):
                    self._capture(item, depth + 1)

    def restore(self):
        # Restore nested records before their owners.
        for kind, target, previous in reversed(
            self.records
        ):
            if kind == "list":
                list.__setitem__(
                    target, slice(None), previous
                )

            elif kind == "dict":
                dict.clear(target)
                dict.update(target, previous)

            elif kind == "set":
                set.clear(target)
                set.update(target, previous)

            elif kind == "object":
                dict.clear(target)
                dict.update(target, previous)

            elif kind == "dataclass":
                for name, value in previous:
                    object.__setattr__(
                        target, name, value
                    )

            elif kind == "slots":
                for name, existed, value in previous:
                    if existed:
                        object.__setattr__(
                            target, name, value
                        )
                    else:
                        try:
                            object.__delattr__(
                                target, name
                            )
                        except AttributeError:
                            pass

            elif kind == "rng":
                target.setstate(previous)


class EntityTickTransaction:
    """Rollback one failed entity tick, not the entire batch."""

    PRIOR_PHASE_ROOTS = (
        "layers",
        "idea_universe",
        "spacetime",
        "physics",
        "life_cycle_system",
        "cats_layer",
        "world",
        "entity_memory",
        "conflict_history",
        "symbolic_replay_outbox",
    )

    COMMITTED_SCALARS = (
        "universe_tick",
        "entropy",
        "pressure",
        "energy_pool",
        "classical_entropy_total",
        "last_classical_entropy_delta",
        "last_energy_gain",
        "last_pressure_cost",
        "last_energy_delta",
        "conflict_pressure",
        "physical_universe_started",
    )

    @staticmethod
    def execute(universe, entity, operation):
        snapshot = EntityRuntimeSnapshot(universe)

        # Earlier successful scheduler phases are committed.
        # Capture their mutable runtime roots before this
        # entity is allowed to modify them.
        prior_roots = tuple(
            (
                name,
                name in universe.__dict__,
                universe.__dict__.get(name),
            )
            for name in EntityTickTransaction.PRIOR_PHASE_ROOTS
        )

        for _, existed, root in prior_roots:
            if existed:
                snapshot._capture(root, 0)

        committed_scalars = tuple(
            (
                name,
                name in universe.__dict__,
                universe.__dict__.get(name),
            )
            for name in EntityTickTransaction.COMMITTED_SCALARS
        )

        attributes = getattr(entity, "__dict__", None)
        ticks_before = None

        if isinstance(attributes, dict):
            value = attributes.get("ticks")

            if type(value) is int:
                ticks_before = value

        try:
            # Reuse the established universe-wide rollback
            # for events, registries, RNG and quantum state.
            return CronenbergEncounterBatchTransaction.execute(
                universe,
                operation,
            )

        except BaseException:
            ticks_after = None

            attributes = getattr(entity, "__dict__", None)

            if isinstance(attributes, dict):
                value = attributes.get("ticks")

                if type(value) is int:
                    ticks_after = value

            # Roll back arbitrary direct entity mutations
            # and supported nested mutable components.
            snapshot.restore()

            # Restore original root references as well as
            # their nested in-memory contents.
            for name, existed, root in prior_roots:
                if existed:
                    object.__setattr__(
                        universe, name, root
                    )
                else:
                    universe.__dict__.pop(name, None)

            # Preserve values committed by earlier phases,
            # not partial mutations from this failed entity.
            for name, existed, value in committed_scalars:
                if existed:
                    object.__setattr__(
                        universe, name, value
                    )
                else:
                    universe.__dict__.pop(name, None)

            # Preserve the legacy attempt counter.
            # Simulation state remains rolled back.
            if (
                ticks_before is not None
                and ticks_after == ticks_before + 1
            ):
                entity.__dict__["ticks"] = ticks_after

            raise
