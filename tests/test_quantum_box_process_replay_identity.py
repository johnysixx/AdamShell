import io
import json
import random
import subprocess
import sys
import tempfile
import unittest

from contextlib import redirect_stdout
from pathlib import Path

from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.universe import Universe


CHILD_SOURCE = r"""
import io
import json
import sys

from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from core.entity.components import SpatialVector3
from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)
from universe.quantum_box_disappearance_state import (
    QuantumBoxDisappearedEvent,
)
from universe.quantum_tick_advanced_state import (
    UniverseQuantumTickAdvancedEvent,
)
from universe.universe import Universe


data = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

box_events = []

for item in data["box_events"]:
    name = item["name"]

    if name == "quantum_box_created":
        event = QuantumBoxCreatedEvent(
            box_id=item["box_id"],
            position=SpatialVector3(
                **item["position"]
            ),
            layer=item["layer"],
            tick=item["tick"],
        )

    elif name == "quantum_box_collapsed":
        event = QuantumBoxCollapsedEvent(
            quantum_box_id=item["quantum_box_id"],
            result=item["result"],
            cause=item["cause"],
            observer=item["observer"],
            tick=item["tick"],
        )

    elif name == "quantum_box_disappeared":
        event = QuantumBoxDisappearedEvent(
            box_id=item["box_id"],
            cause=item["cause"],
            tick=item["tick"],
        )

    else:
        raise AssertionError(
            f"Unsupported box event: {name}"
        )

    box_events.append(event)

clock_events = [
    UniverseQuantumTickAdvancedEvent(
        tick=item["tick"],
        observer=item["observer"],
    )
    for item in data["clock_events"]
]

with redirect_stdout(io.StringIO()):
    target = Universe(
        universe_id=data["universe_id"]
    )
    target.enable_quantum_layer()

    with (
        patch(
            "core.entity.quantum_box.uuid.uuid4",
            side_effect=AssertionError(
                "Replay generated a UUID."
            ),
        ),
        patch(
            "core.entity.quantum_box.random.uniform",
            side_effect=AssertionError(
                "Replay used random coordinates."
            ),
        ),
    ):
        target.replay_quantum_history(
            box_events=box_events,
            clock_events=clock_events,
            preserve_history=True,
        )

assert len(target.quantum_events) == len(box_events)
assert len(target.quantum_clock_events) == len(clock_events)

result = {
    "boxes": [
        {
            "id": box.id,
            "age": box.age_ticks,
            "state": box.public_state,
        }
        for box in target.quantum_boxes
    ],
    "clock": target.quantum_state.tick_count,
    "statistics": {
        "created": (
            target.statistics.total_quantum_boxes_created
        ),
        "collapsed": (
            target.statistics.total_quantum_collapses
        ),
        "disappeared": (
            target.statistics.total_quantum_boxes_disappeared
        ),
    },
    "timeline": [
        [event.name, event.tick]
        for event in target.quantum_lifecycle_timeline()
    ],
    "box_history_count": len(target.quantum_events),
    "clock_history_count": len(
        target.quantum_clock_events
    ),
}

print(json.dumps(result, sort_keys=True))
"""


class FixedEmptyChoice:

    def choice(self, possibilities):
        if "empty" not in possibilities:
            raise AssertionError(
                "Empty collapse possibility missing."
            )
        return "empty"


def export_event(event):
    if isinstance(event, QuantumBoxCollapsedEvent):
        return {
            "name": event.name,
            "quantum_box_id": event.quantum_box_id,
            "result": event.result,
            "cause": event.cause,
            "observer": event.observer,
            "tick": event.tick,
        }

    return event.to_dict()


class QuantumBoxProcessReplayIdentityTests(
    unittest.TestCase
):

    def test_reused_identity_and_chronology_across_processes(self):
        with redirect_stdout(io.StringIO()):
            source = Universe(
                universe_id="a37_quantum_replay"
            )
            source.enable_quantum_layer()
            source.should_collapse_quantum_box = (
                lambda _box: False
            )

            # Two boxes begin at tick zero.
            source.create_quantum_box(
                box_id="reused",
                rng=random.Random(17),
            )
            source.create_quantum_box(
                box_id="survivor",
                rng=random.Random(18),
                layer="meeting_place",
            )

            # The first box disappears at tick one.
            source.tick_quantum_unprotected()
            source.open_quantum_box(
                "reused",
                rng=FixedEmptyChoice(),
                observer="a37_observer",
            )

            # A new lifecycle reuses the same logical ID.
            source.create_quantum_box(
                box_id="reused",
                rng=random.Random(19),
            )

            source.tick_quantum_unprotected()

        self.assertEqual(
            [event.name for event in source.quantum_events],
            [
                "quantum_box_created",
                "quantum_box_created",
                "quantum_box_collapsed",
                "quantum_box_disappeared",
                "quantum_box_created",
            ],
        )

        self.assertEqual(
            [box.id for box in source.quantum_boxes],
            ["survivor", "reused"],
        )

        self.assertEqual(
            [box.age_ticks for box in source.quantum_boxes],
            [2, 1],
        )

        original_timeline = [
            [event.name, event.tick]
            for event in source.quantum_lifecycle_timeline()
        ]

        self.assertEqual(
            [item[1] for item in original_timeline],
            [0, 0, 1, 1, 1, 1, 2],
        )

        expected = {
            "boxes": [
                {
                    "id": box.id,
                    "age": box.age_ticks,
                    "state": box.public_state,
                }
                for box in source.quantum_boxes
            ],
            "clock": source.quantum_state.tick_count,
            "statistics": {
                "created": (
                    source.statistics.total_quantum_boxes_created
                ),
                "collapsed": (
                    source.statistics.total_quantum_collapses
                ),
                "disappeared": (
                    source.statistics.total_quantum_boxes_disappeared
                ),
            },
            "timeline": original_timeline,
            "box_history_count": len(source.quantum_events),
            "clock_history_count": len(
                source.quantum_clock_events
            ),
        }

        document = {
            "universe_id": source.id,
            "box_events": [
                export_event(event)
                for event in source.quantum_events
            ],
            "clock_events": [
                event.to_dict()
                for event in source.quantum_clock_events
            ],
        }

        before_boxes = tuple(source.quantum_events)
        before_clocks = tuple(source.quantum_clock_events)

        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "a37_history.json"

            path.write_text(
                json.dumps(document, sort_keys=True),
                encoding="utf-8",
            )

            results = []

            # Each replay runs in a fresh Python process.
            for attempt in range(2):
                with self.subTest(process=attempt):
                    run = subprocess.run(
                        [
                            sys.executable,
                            "-B",
                            "-c",
                            CHILD_SOURCE,
                            str(path),
                        ],
                        cwd=str(
                            Path(__file__).resolve().parents[1]
                        ),
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    self.assertEqual(
                        run.returncode,
                        0,
                        msg=(
                            f"stdout={run.stdout!r}\n"
                            f"stderr={run.stderr!r}"
                        ),
                    )

                    result = json.loads(run.stdout)

                    self.assertEqual(result, expected)
                    results.append(result)

            self.assertEqual(results[0], results[1])

        # Reading and replaying the exported history
        # must never mutate the original source.
        self.assertEqual(
            tuple(source.quantum_events),
            before_boxes,
        )
        self.assertEqual(
            tuple(source.quantum_clock_events),
            before_clocks,
        )


if __name__ == "__main__":
    unittest.main()
