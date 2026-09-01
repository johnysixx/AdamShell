from dataclasses import dataclass


@dataclass(slots=True)
class CronenbergOrigin:

    layer: str
    source_component: object
    source_operation: object
    quantum_tick: int | None
    error_type: str
    error_message: str
    recombined_from: tuple[str, ...] | None = None
    merged_from: tuple[str, ...] | None = None
    former_pair_id: str | None = None
    consumption_location: str | None = None
    merge_location: str | None = None
    released_energy: float | None = None
    dark_energy_created: float | None = None
    counterpart_of: str | None = None
    pair_id: str | None = None
    spin_relation: str | None = None
    manifested_in: str | None = None

    @classmethod
    def from_error(
        cls,
        error,
        source_component,
        source_operation,
        quantum_tick=None,
    ):
        return cls(
            layer="quantum_layer",
            source_component=source_component,
            source_operation=source_operation,
            quantum_tick=quantum_tick,
            error_type=type(error).__name__,
            error_message=str(error),
        )

    def mark_recombined(
        self,
        source_ids,
        former_pair_id,
        consumption_location,
        released_energy,
        dark_energy_created,
    ):
        self.recombined_from = tuple(
            str(source_id)
            for source_id in source_ids
        )
        self.former_pair_id = former_pair_id
        self.consumption_location = (
            consumption_location
        )
        self.released_energy = float(
            released_energy
        )
        self.dark_energy_created = float(
            dark_energy_created
        )

    def mark_merged(
        self,
        source_ids,
        former_pair_id,
        merge_location,
    ):
        self.merged_from = tuple(
            str(source_id)
            for source_id in source_ids
        )
        self.former_pair_id = former_pair_id
        self.merge_location = merge_location

    def mark_counterpart(
        self,
        counterpart_of,
        pair_id,
        spin_relation="opposite",
        manifested_in="quantum_layer",
    ):
        self.counterpart_of = str(
            counterpart_of
        )
        self.pair_id = str(pair_id)
        self.spin_relation = str(
            spin_relation
        )
        self.manifested_in = str(
            manifested_in
        )

    def to_dict(self):
        result = {
            "layer": self.layer,
            "source_component": (
                self.source_component
            ),
            "source_operation": (
                self.source_operation
            ),
            "quantum_tick": self.quantum_tick,
            "error_type": self.error_type,
            "error_message": self.error_message,
        }

        if self.recombined_from is not None:
            result["recombined_from"] = list(
                self.recombined_from
            )
            result["former_pair_id"] = (
                self.former_pair_id
            )
            result["consumption_location"] = (
                self.consumption_location
            )
            result["released_energy"] = (
                self.released_energy
            )
            result["dark_energy_created"] = (
                self.dark_energy_created
            )

        if self.merged_from is not None:
            result["merged_from"] = list(
                self.merged_from
            )
            result["former_pair_id"] = (
                self.former_pair_id
            )
            result["merge_location"] = (
                self.merge_location
            )

        if self.counterpart_of is not None:
            result["counterpart_of"] = (
                self.counterpart_of
            )
            result["pair_id"] = self.pair_id
            result["spin_relation"] = (
                self.spin_relation
            )
            result["manifested_in"] = (
                self.manifested_in
            )

        return result
