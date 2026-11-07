"""Caller-supplied, immutable symbolic replay receipt evidence.

An instance binds receipt IDs to one universe and batch.
It does not authenticate its source or prove freshness.

The caller must obtain its contents from an independent
trusted authority, not from possibly rolled-back files.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SymbolicReplayReceiptWitness:
    universe_id: str
    batch_sha256: str
    receipt_ids: tuple[str, ...]

    def __post_init__(self):
        if (
            type(self.universe_id) is not str
            or not self.universe_id
        ):
            raise ValueError(
                "Receipt witness requires universe ID."
            )

        if (
            type(self.batch_sha256) is not str
            or len(self.batch_sha256) != 64
            or any(
                char not in "0123456789abcdef"
                for char in self.batch_sha256
            )
        ):
            raise ValueError(
                "Invalid receipt witness batch digest."
            )

        if type(self.receipt_ids) is not tuple:
            raise TypeError(
                "Receipt witness IDs must be a tuple."
            )

        if any(
            type(identity) is not str or not identity
            for identity in self.receipt_ids
        ):
            raise ValueError(
                "Invalid receipt witness event identity."
            )

        if len(set(self.receipt_ids)) != len(
            self.receipt_ids
        ):
            raise ValueError(
                "Duplicate receipt witness event identity."
            )
