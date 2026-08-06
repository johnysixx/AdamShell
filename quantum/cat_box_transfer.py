from copy import deepcopy
import math

from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J,
    DarkSector
)


class CatQuantumBoxTransfer:

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

        if not hasattr(
            universe,
            "quantum_cat_trails"
        ):
            universe.quantum_cat_trails = []

        if not hasattr(
            universe,
            "stable_cat_box_pairs"
        ):
            universe.stable_cat_box_pairs = []

        if not hasattr(
            universe,
            "layer_energy"
        ):
            universe.layer_energy = {}

        if not hasattr(
            universe,
            "dark_sector"
        ):
            universe.dark_sector = DarkSector()

    def pair_boxes(
        self,
        source_box,
        target_box
    ):
        if (
            source_box.current_layer
            == target_box.current_layer
        ):
            raise ValueError(
                "Quantum counterparts must exist "
                "in different layers."
            )

        event = source_box.pair_with(
            target_box
        )

        self._record(
            event
        )

        return event

    def create_exploration_pair(
        self,
        cat,
        destination_layer,
        destination_position,
        source_position=None
    ):
        """
        Ko?ka vytvo?? za vlastn? energii
        stabiln? dvojici krabic pro pr?zkum.

        P?r mohou vyu??vat i jin? ko?ky.
        """
        if not isinstance(
            cat,
            dict
        ):
            return self._failure(
                cat,
                "invalid_cat"
            )

        source_layer = cat.get(
            "current_layer",
            "quantum_layer"
        )

        destination_layer = str(
            destination_layer
        )

        if destination_layer == source_layer:
            return self._failure(
                cat,
                "destination_layer_matches_source"
            )

        energy_cost = (
            QUANTUM_BOX_ENERGY_COST_J
            * 2.0
        )

        available_energy = float(
            cat.get(
                "idea_energy",
                0.0
            )
        )

        if available_energy < energy_cost:
            return self._failure(
                cat,
                "insufficient_cat_energy"
            )

        cat["idea_energy"] = (
            available_energy
            - energy_cost
        )

        source_box = (
            self.universe
            .create_quantum_box(
                layer=source_layer
            )
        )

        target_box = (
            self.universe
            .create_quantum_box(
                layer=destination_layer
            )
        )

        source_box.position = dict(
            source_position
            or cat.get(
                "position",
                {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            )
        )

        target_box.position = dict(
            destination_position
        )

        self.pair_boxes(
            source_box,
            target_box
        )

        pair_number = (
            len(
                self.universe
                .stable_cat_box_pairs
            )
            + 1
        )

        pair_id = (
            f"stable_cat_box_pair_"
            f"{pair_number:04d}"
        )

        pair = {
            "pair_id": pair_id,
            "pair_kind": (
                "cat_created_exploration_pair"
            ),
            "stable": True,
            "active": True,
            "creator_cat": cat.get("name"),
            "creator_departed": False,
            "creator_returned": False,
            "anchor_box_id": source_box.id,
            "remote_box_id": target_box.id,
            "anchor_layer": source_layer,
            "remote_layer": destination_layer,
            "creation_energy_j": energy_cost,
            "remaining_energy_j": energy_cost,
            "currently_in_use": False,
            "current_user": None,
            "use_count": 0,
            "used_by": [],
            "created_tick": (
                self.universe
                .quantum_state[
                    "tick_count"
                ]
            )
        }

        self.universe.stable_cat_box_pairs.append(
            pair
        )

        source_box.exploration_pair_id = (
            pair_id
        )

        target_box.exploration_pair_id = (
            pair_id
        )

        event = {
            "name": (
                "cat_created_stable_"
                "exploration_box_pair"
            ),
            "cat": cat.get("name"),
            "pair_id": pair_id,
            "source_box_id": source_box.id,
            "target_box_id": target_box.id,
            "source_layer": source_layer,
            "target_layer": destination_layer,
            "energy_cost_j": energy_cost,
            "remaining_cat_energy": (
                cat["idea_energy"]
            ),
            "available_to_other_cats": True,
            "stable": True,
            "created": True
        }

        self._record(
            event
        )

        return {
            **event,
            "source_box": source_box,
            "target_box": target_box,
            "pair": deepcopy(pair)
        }

    def _find_stable_pair(
        self,
        source_box_id,
        target_box_id
    ):
        expected_boxes = {
            source_box_id,
            target_box_id
        }

        for pair in (
            self.universe
            .stable_cat_box_pairs
        ):
            if not pair.get(
                "active",
                False
            ):
                continue

            pair_boxes = {
                pair.get(
                    "anchor_box_id"
                ),
                pair.get(
                    "remote_box_id"
                )
            }

            if pair_boxes == expected_boxes:
                return pair

        return None

    def _transfer_through_stable_pair(
        self,
        cat,
        source_box,
        target_box,
        transfer,
        pair
    ):
        """
        Provede p?enos stabiln?m p?rem.

        Ani jedna krabice se p?i b??n?m
        pou?it? nespot?ebuje.
        """
        cat_name = cat.get(
            "name"
        )

        pair["currently_in_use"] = True
        pair["current_user"] = cat_name
        pair["use_count"] += 1

        if cat_name not in pair["used_by"]:
            pair["used_by"].append(
                cat_name
            )

        target_position = dict(
            target_box.position
        )

        target_layer = (
            target_box.current_layer
        )

        cat["position"] = (
            target_position
        )

        cat["current_layer"] = (
            target_layer
        )

        cat["state"] = (
            "materialized_through_"
            "stable_exploration_pair"
        )

        cat["quantum_transfer"].update({
            "active": False,
            "state": "collapsed",
            "cat_is_here": True,
            "cat_is_not_here": False,
            "resolved_layer": target_layer,
            "resolved_position": (
                target_position
            ),
            "target_box_consumed": False,
            "stable_pair_id": pair[
                "pair_id"
            ]
        })

        for box in (
            source_box,
            target_box
        ):
            box.state = "superposition"

            box.cat_transfer.update({
                "active": False,
                "state": "completed",
                "cat_name": None,
                "source_box_id": None,
                "target_box_id": None,
                "source_layer": None,
                "target_layer": None,
                "started_tick": None
            })

        creator_returned = False

        if cat_name == pair["creator_cat"]:
            leaving_anchor = (
                source_box.id
                == pair["anchor_box_id"]
            )

            returning_to_anchor = (
                target_box.id
                == pair["anchor_box_id"]
            )

            if (
                leaving_anchor
                and not pair[
                    "creator_departed"
                ]
            ):
                pair[
                    "creator_departed"
                ] = True

            elif (
                pair["creator_departed"]
                and returning_to_anchor
            ):
                pair[
                    "creator_returned"
                ] = True

                creator_returned = True

        pair["currently_in_use"] = False
        pair["current_user"] = None

        trail = self._create_trail(
            cat=cat,
            source_box=source_box,
            target_box=target_box
        )

        memory = cat.get(
            "memory"
        )

        remembered = None

        if memory is not None:
            remembered = memory.remember(
                event_type=(
                    "stable_quantum_box_"
                    "layer_transfer"
                ),
                universe_tick=(
                    self.universe
                    .universe_tick
                ),
                location=target_position,
                participants=[
                    source_box.id,
                    target_box.id
                ],
                details={
                    "pair_id": pair[
                        "pair_id"
                    ],
                    "source_layer": (
                        transfer[
                            "source_layer"
                        ]
                    ),
                    "target_layer": (
                        target_layer
                    ),
                    "target_box_consumed": (
                        False
                    ),
                    "trail_id": trail[
                        "trail_id"
                    ]
                }
            )

        event = {
            "name": (
                "cat_used_stable_"
                "exploration_box_pair"
            ),
            "cat": cat_name,
            "pair_id": pair["pair_id"],
            "source_box_id": source_box.id,
            "target_box_id": target_box.id,
            "source_layer": transfer[
                "source_layer"
            ],
            "target_layer": target_layer,
            "target_box_consumed": False,
            "source_box_survived": True,
            "target_box_survived": True,
            "pair_remains_stable": (
                not creator_returned
            ),
            "creator_returned": (
                creator_returned
            ),
            "use_count": pair[
                "use_count"
            ],
            "trail": trail,
            "memory": remembered,
            "transferred": True
        }

        if creator_returned:
            dissolution = (
                self._dissolve_stable_pair(
                    pair=pair,
                    returning_cat=cat
                )
            )

            event[
                "pair_dissolution"
            ] = dissolution

            event[
                "pair_remains_stable"
            ] = False

        self._record(
            event
        )

        return event

    def _credit_layer_energy(
        self,
        layer_name,
        amount
    ):
        layer_name = str(
            layer_name
        )

        current = float(
            self.universe.layer_energy.get(
                layer_name,
                0.0
            )
        )

        self.universe.layer_energy[
            layer_name
        ] = (
            current
            + float(amount)
        )

        return self.universe.layer_energy[
            layer_name
        ]

    def _dissolve_stable_pair(
        self,
        pair,
        returning_cat
    ):
        """
        Rozpust? stabiln? pr?zkumn? p?r
        p?i n?vratu jeho tv?rce.

        20 % vytvo?? Cronenberga.
        30 % se vr?t? do energy_pool.
        20 % se vr?t? vrstv? kotvy A.
        20 % p?ejde do temn? energie.
        10 % se vr?t? vzd?len? vrstv?.

        Pokud je vzd?lenou vrstvou Quantum
        Layer, posledn?ch 10 % se p?i?te
        tak? k temn? energii.
        """
        total_energy = float(
            pair.get(
                "remaining_energy_j",
                0.0
            )
        )

        cronenberg_energy = (
            total_energy * 0.20
        )

        pool_energy = (
            total_energy * 0.30
        )

        anchor_layer_energy = (
            total_energy * 0.20
        )

        if (
            pair["remote_layer"]
            == "quantum_layer"
        ):
            remote_layer_energy = 0.0

        else:
            remote_layer_energy = (
                total_energy * 0.10
            )

        # Temn? energie je dopo??tan? zbytek.
        # Sou?et v?ech ??st? je proto v?dy
        # p?esn? roven p?vodn? energii p?ru.
        dark_energy = (
            total_energy
            - cronenberg_energy
            - pool_energy
            - anchor_layer_energy
            - remote_layer_energy
        )

        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Stabiln? ko?i?? kvantov? "
                    "p?r se p?i n?vratu tv?rce "
                    "rozpadl."
                ),
                source_component=(
                    "cat_quantum_box_pair"
                ),
                source_operation=(
                    "stable_pair_return_collapse"
                )
            )
        )

        cronenberg.manifestation_energy_j = (
            cronenberg_energy
        )

        self.universe.energy_pool += (
            pool_energy
        )

        self._credit_layer_energy(
            pair["anchor_layer"],
            anchor_layer_energy
        )

        if remote_layer_energy > 0.0:
            self._credit_layer_energy(
                pair["remote_layer"],
                remote_layer_energy
            )

        dark_sector = (
            self.universe.dark_sector
        )

        dark_sector.dark_energy_j += (
            dark_energy
        )

        dark_event = {
            "name": (
                "stable_box_pair_dark_"
                "energy_received"
            ),
            "pair_id": pair["pair_id"],
            "energy_j": dark_energy,
            "dark_energy_total_j": (
                dark_sector.dark_energy_j
            )
        }

        dark_sector.events.append(
            dark_event
        )

        removed_boxes = []

        for box_id in (
            pair["anchor_box_id"],
            pair["remote_box_id"]
        ):
            box = self._find_box(
                box_id
            )

            if box is None:
                continue

            box.clear_counterpart()

            if box in self.universe.quantum_boxes:
                self.universe.quantum_boxes.remove(
                    box
                )

                self.universe.statistics                    .record_quantum_box_disappeared()

                removed_boxes.append(
                    box.id
                )

        pair["active"] = False
        pair["stable"] = False
        pair["dissolved"] = True
        pair["remaining_energy_j"] = 0.0
        pair["dissolved_by_return_of"] = (
            returning_cat.get("name")
        )

        distributed_energy = (
            cronenberg_energy
            + pool_energy
            + anchor_layer_energy
            + dark_energy
            + remote_layer_energy
        )

        event = {
            "name": (
                "stable_cat_box_pair_dissolved"
            ),
            "pair_id": pair["pair_id"],
            "creator_cat": pair[
                "creator_cat"
            ],
            "returning_cat": (
                returning_cat.get("name")
            ),
            "removed_boxes": removed_boxes,
            "energy_total_j": total_energy,
            "energy_distributed_j": (
                distributed_energy
            ),
            "energy_conserved": (
                math.isclose(
                    total_energy,
                    distributed_energy,
                    rel_tol=1e-12,
                    abs_tol=1e-15
                )
            ),
            "energy_difference_j": (
                total_energy
                - distributed_energy
            ),
            "cronenberg": {
                "id": cronenberg.id,
                "energy_j": cronenberg_energy
            },
            "global_pool_energy_j": (
                pool_energy
            ),
            "anchor_layer": pair[
                "anchor_layer"
            ],
            "anchor_layer_energy_j": (
                anchor_layer_energy
            ),
            "remote_layer": pair[
                "remote_layer"
            ],
            "remote_layer_energy_j": (
                remote_layer_energy
            ),
            "quantum_dark_energy_j": (
                dark_energy
            ),
            "dissolved": True
        }

        self._record(
            event
        )

        return event

    def transfer_cat(
        self,
        cat,
        source_box_id,
        target_box_id
    ):
        source_box = self._find_box(
            source_box_id
        )

        target_box = self._find_box(
            target_box_id
        )

        if source_box is None:
            return self._failure(
                cat,
                "source_box_not_found"
            )

        if target_box is None:
            return self._failure(
                cat,
                "target_box_not_found"
            )

        if cat.get(
            "current_layer",
            "quantum_layer"
        ) != source_box.current_layer:
            return self._failure(
                cat,
                "cat_not_in_source_layer"
            )

        if not self._cat_can_recognize_pair(
            cat,
            source_box
        ):
            return self._failure(
                cat,
                "cat_cannot_recognize_quantum_pair"
            )

        transfer = source_box.begin_cat_transfer(
            cat=cat,
            target_box=target_box,
            tick=self.universe.quantum_state[
                "tick_count"
            ]
        )

        cat["quantum_transfer"] = {
            **deepcopy(transfer),
            "cat_is_here": True,
            "cat_is_not_here": True
        }

        cat["state"] = (
            "quantum_box_transfer_superposition"
        )

        target_position = dict(
            target_box.position
        )

        target_layer = (
            target_box.current_layer
        )

        stable_pair = (
            self._find_stable_pair(
                source_box_id=source_box.id,
                target_box_id=target_box.id
            )
        )

        if stable_pair is not None:
            return (
                self._transfer_through_stable_pair(
                    cat=cat,
                    source_box=source_box,
                    target_box=target_box,
                    transfer=transfer,
                    pair=stable_pair
                )
            )

        target_box.consume_for_cat_transfer()

        # Energie cílové krabice se spotřebovala
        # přímo na přenos a nejde do dark sectoru.
        consumed_energy = (
            QUANTUM_BOX_ENERGY_COST_J
        )

        if target_box in self.universe.quantum_boxes:
            self.universe.quantum_boxes.remove(
                target_box
            )

            self.universe.statistics\
                .record_quantum_box_disappeared()

        source_box.clear_counterpart()

        source_box.state = "superposition"
        source_box.cat_transfer.update({
            "active": False,
            "state": "completed",
            "cat_name": None,
            "target_box_id": None,
            "target_layer": None
        })

        cat["position"] = target_position
        cat["current_layer"] = target_layer
        cat["state"] = (
            "materialized_at_consumed_"
            "target_box"
        )

        cat["quantum_transfer"].update({
            "active": False,
            "state": "collapsed",
            "cat_is_here": True,
            "cat_is_not_here": False,
            "resolved_layer": target_layer,
            "resolved_position": target_position,
            "target_box_consumed": True
        })

        trail = self._create_trail(
            cat=cat,
            source_box=source_box,
            target_box=target_box
        )

        memory = cat.get(
            "memory"
        )

        remembered = None

        if memory is not None:
            remembered = memory.remember(
                event_type=(
                    "quantum_box_layer_transfer"
                ),
                universe_tick=(
                    self.universe.universe_tick
                ),
                location=target_position,
                participants=[
                    source_box.id,
                    target_box.id
                ],
                details={
                    "source_layer": (
                        transfer["source_layer"]
                    ),
                    "target_layer": target_layer,
                    "target_box_consumed": True,
                    "energy_j": consumed_energy,
                    "trail_id": trail["trail_id"]
                }
            )

        event = {
            "name": (
                "cat_quantum_box_transfer_completed"
            ),
            "cat": cat.get("name"),
            "source_box_id": source_box.id,
            "target_box_id": target_box.id,
            "source_layer": transfer[
                "source_layer"
            ],
            "target_layer": target_layer,
            "source_box_survived": True,
            "target_box_consumed": True,
            "target_box_energy_used": True,
            "energy_use": "cat_layer_transfer",
            "energy_j": consumed_energy,
            "energy_conserved": True,
            "cat_state": cat["state"],
            "trail": trail,
            "memory": remembered,
            "transferred": True
        }

        self._record(
            event
        )

        return event

    def create_return_counterpart(
        self,
        cat,
        source_box_id,
        position=None
    ):
        source_box = self._find_box(
            source_box_id
        )

        if source_box is None:
            return self._failure(
                cat,
                "source_box_not_found"
            )

        energy_cost = (
            QUANTUM_BOX_ENERGY_COST_J
        )

        cat_energy = float(
            cat.get(
                "idea_energy",
                0.0
            )
        )

        if cat_energy < energy_cost:
            return self._failure(
                cat,
                "insufficient_cat_energy"
            )

        cat["idea_energy"] = (
            cat_energy - energy_cost
        )

        counterpart = (
            self.universe.create_quantum_box()
        )

        counterpart.current_layer = cat.get(
            "current_layer",
            "quantum_layer"
        )

        counterpart.position = dict(
            position
            or cat.get(
                "position",
                {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            )
        )

        pair_event = self.pair_boxes(
            source_box,
            counterpart
        )

        event = {
            "name": (
                "cat_created_return_box_counterpart"
            ),
            "cat": cat.get("name"),
            "source_box_id": source_box.id,
            "counterpart_box_id": counterpart.id,
            "source_layer": (
                source_box.current_layer
            ),
            "counterpart_layer": (
                counterpart.current_layer
            ),
            "position": dict(
                counterpart.position
            ),
            "energy_cost": energy_cost,
            "remaining_cat_energy": (
                cat["idea_energy"]
            ),
            "pair_event": pair_event,
            "created": True
        }

        self._record(
            event
        )

        return {
            **event,
            "counterpart": counterpart
        }

    def stabilize_direct_trail(
        self,
        cat,
        destination
    ):
        start = dict(
            cat.get(
                "position",
                {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            )
        )

        end = dict(
            destination
        )

        distance = math.dist(
            (
                start.get("x", 0.0),
                start.get("y", 0.0),
                start.get("z", 0.0)
            ),
            (
                end.get("x", 0.0),
                end.get("y", 0.0),
                end.get("z", 0.0)
            )
        )

        event = {
            "name": (
                "cat_stabilized_direct_quantum_path"
            ),
            "cat": cat.get("name"),
            "start": start,
            "destination": end,
            "distance": distance,
            "path_kind": "most_direct_possible",
            "stability": 1.0,
            "stabilized": True
        }

        self._record(
            event
        )

        return event

    def reinforce_trail(
        self,
        trail_id,
        amount=0.05
    ):
        trail = next(
            (
                item
                for item
                in self.universe.quantum_cat_trails
                if item["trail_id"] == trail_id
            ),
            None
        )

        if trail is None:
            return None

        trail["uses"] += 1
        trail["stability"] = min(
            1.0,
            trail["stability"] + float(amount)
        )

        return deepcopy(
            trail
        )

    def _create_trail(
        self,
        cat,
        source_box,
        target_box
    ):
        trail_number = len(
            self.universe.quantum_cat_trails
        ) + 1

        trail = {
            "trail_id": (
                f"quantum_cat_trail_"
                f"{trail_number:04d}"
            ),
            "cat": cat.get("name"),
            "from_box": source_box.id,
            "to_box": target_box.id,
            "from_layer": (
                source_box.current_layer
            ),
            "to_layer": (
                target_box.current_layer
            ),
            "start_position": dict(
                source_box.position
            ),
            "end_position": dict(
                target_box.position
            ),
            "stability": 0.50,
            "uses": 1,
            "age_ticks": 0
        }

        self.universe.quantum_cat_trails.append(
            trail
        )

        return deepcopy(
            trail
        )

    def _cat_can_recognize_pair(
        self,
        cat,
        box
    ):
        if not box.quantum_counterpart[
            "paired"
        ]:
            return False

        access = cat.get(
            "access",
            {}
        )

        return bool(
            access.get(
                "can_access_anywhere",
                False
            )
            and "boxes" in access.get(
                "access_via",
                []
            )
        )

    def _find_box(
        self,
        box_id
    ):
        return next(
            (
                box
                for box
                in self.universe.quantum_boxes
                if box.id == box_id
            ),
            None
        )

    def _failure(
        self,
        cat,
        reason
    ):
        event = {
            "name": (
                "cat_quantum_box_transfer_failed"
            ),
            "cat": (
                cat.get("name")
                if isinstance(cat, dict)
                else None
            ),
            "reason": reason,
            "transferred": False
        }

        self._record(
            event
        )

        return event

    def _record(
        self,
        event
    ):
        self.history.append(
            deepcopy(event)
        )

        self.universe.quantum_events.append(
            deepcopy(event)
        )

        return event