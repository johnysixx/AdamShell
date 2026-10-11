from dataclasses import dataclass, field

from universe.logger import UniverseLogger


@dataclass(slots=True, frozen=True)
class QuantumErrorResult:
    error_type: str
    error_message: str
    cronenberg: object
    type: str = field(
        default="quantum_error",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "error_type",
            str(self.error_type),
        )

        object.__setattr__(
            self,
            "error_message",
            str(self.error_message),
        )

    def to_dict(self):
        return {
            "type": self.type,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "cronenberg": self.cronenberg,
        }


class QuantumErrorBoundary:

    def __init__(
            self,
            cronenberg_factory
    ):
        self.cronenberg_factory = (
            cronenberg_factory
        )

    def execute(
            self,
            operation,
            source_component,
            source_operation
    ):
        try:
            return operation()

        except Exception as error:
            UniverseLogger.event(
                "QUANTUM LAYER ERROR: "
                f"{type(error).__name__}: "
                f"{error}"
            )

            cronenberg = (
                self.cronenberg_factory(
                    error=error,
                    source_component=source_component,
                    source_operation=source_operation
                )
            )

            return QuantumErrorResult(
                error_type=(
                    type(error).__name__
                ),
                error_message=str(error),
                cronenberg=cronenberg,
            )
