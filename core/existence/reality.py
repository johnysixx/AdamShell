class Reality:

    def __init__(self):
        self.natural_processes = []

    def add_natural_process(
        self,
        process
    ):
        if process in self.natural_processes:
            return False

        self.natural_processes.append(
            process
        )

        return True

    def remove_natural_process(
        self,
        process
    ):
        if process not in self.natural_processes:
            return False

        self.natural_processes.remove(
            process
        )

        return True

    def collect_potentials(
        self,
        cycle_id
    ):
        potentials = []

        for process in self.natural_processes:
            generator = getattr(
                process,
                "generate_potentials",
                None
            )

            if generator is None:
                continue

            generated = generator(
                cycle_id
            )

            potentials.extend(
                generated
            )

        return potentials

    @property
    def public_state(self):
        return {
            "natural_process_count": len(
                self.natural_processes
            ),
            "natural_processes": [
                getattr(
                    process,
                    "public_state",
                    {
                        "type": type(
                            process
                        ).__name__
                    }
                )
                for process in self.natural_processes
            ]
        }
