from universe.logger import UniverseLogger


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

            return {
                "type": "quantum_error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "cronenberg": cronenberg
            }
