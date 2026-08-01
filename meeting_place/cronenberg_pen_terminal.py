from universe.logger import UniverseLogger


class CronenbergPenTerminal:

    def __init__(self):
        self.name = "cronenberg_pen_terminal"
        self.type = "back_room_terminal"
        self.location = "back_room"

        UniverseLogger.boot(
            "CRONENBERG PEN TERMINAL CREATED IN BACK ROOM"
        )

    def read_status(self, meeting_place):
        pen = getattr(
            meeting_place,
            "cronenberg_pen",
            None
        )

        area = getattr(
            meeting_place,
            "cronenberg_area",
            {}
        )

        if pen is None:
            status = {
                "area_state": area.get(
                    "state",
                    "clearing"
                ),
                "pen_exists": False,
                "count": 0,
                "capacity": 5,
                "projected_lemonade": 0.0,
                "total_lemonade_produced": getattr(
                    meeting_place,
                    "cronenberg_lemonade_total",
                    0.0
                ),
                "processing_count": getattr(
                    meeting_place,
                    "cronenberg_processing_count",
                    0
                ),
                "tree": area.get("tree", True),
                "bench": area.get("bench", True),
                "cronenbergs": []
            }

            UniverseLogger.event(
                "CRONENBERG PEN TERMINAL: "
                "NO PEN; TREE AND BENCH PRESENT"
            )

            return status

        pen_status = pen.get_status()

        status = {
            "area_state": area.get(
                "state",
                "cronenberg_pen"
            ),
            "pen_exists": True,
            "count": pen_status["count"],
            "capacity": pen_status["capacity"],
            "projected_lemonade": (
                pen_status["projected_lemonade"]
            ),
            "total_lemonade_produced": (
                pen_status["total_lemonade_produced"]
            ),
            "processing_count": (
                pen_status["processing_count"]
            ),
            "tree": area.get("tree", False),
            "bench": area.get("bench", False),
            "cronenbergs": pen_status["cronenbergs"]
        }

        UniverseLogger.event(
            f"CRONENBERG PEN TERMINAL: "
            f"{status['count']} / {status['capacity']} "
            f"PROJECTED LEMONADE="
            f"{status['projected_lemonade']:.2f}"
        )

        return status

    def display(self, meeting_place):
        status = self.read_status(meeting_place)

        print()
        print("--- CRONENBERG PEN TERMINAL ---")
        print(
            f"Area state: {status['area_state']}"
        )
        print(
            f"Pen exists: {status['pen_exists']}"
        )
        print(
            f"Cronenbergs: "
            f"{status['count']} / {status['capacity']}"
        )
        print(
            f"Projected lemonade: "
            f"{status['projected_lemonade']:.2f} litres"
        )
        print(
            f"Total lemonade produced: "
            f"{status['total_lemonade_produced']:.2f} litres"
        )
        print(
            f"Processed batches: "
            f"{status['processing_count']}"
        )

        if not status["pen_exists"]:
            print(
                f"Tree: {status['tree']}"
            )
            print(
                f"Bench: {status['bench']}"
            )

        for cronenberg in status["cronenbergs"]:
            print()
            print(cronenberg["name"])
            print(
                f"  age: {cronenberg['age']}"
            )
            print(
                f"  size: {cronenberg['size']:.2f}"
            )
            print(
                f"  state: {cronenberg['state']}"
            )

        return status
