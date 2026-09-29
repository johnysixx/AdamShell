from .bar_objects import LemonTree
from .lemon_tree_state import LemonTreeState

class BarYard:

    def __init__(
        self
    ):
        self.name = "bar_yard"
        self.type = "meeting_place_area"

        self.lemon_tree = LemonTree(
            name="lemon_tree",
            type="tree",
            location="bar_yard",
            fruit="lemon",
            lemons=7,
            has_lemons=True,
            state=LemonTreeState.FRUITING,
            months_since_stripped=None,
            flowers=0,
            flowering_after_months=1,
            new_fruit_after_months=6
        )

    def pick_lemon(
        self,
        picker
    ):
        tree = self.lemon_tree

        if (
            not tree.has_lemons
            or tree.lemons <= 0
        ):
            return {
                "name": "lemon_not_found",
                "picker": picker,
                "picked": False,
                "lemons_remaining": 0
            }

        tree.lemons -= 1

        if tree.lemons <= 0:
            tree.lemons = 0

            tree.has_lemons = False

            tree.state = LemonTreeState.STRIPPED

            tree.months_since_stripped = 0

        return {
            "name": "lemon_picked",
            "picker": picker,
            "fruit": "lemon",
            "source": "lemon_tree",
            "picked": True,
            "lemons_remaining": tree.lemons
        }

    def advance_month(
        self
    ):
        tree = self.lemon_tree

        if tree.months_since_stripped is None:
            return {
                "name": "lemon_tree_month_passed",
                "state": tree.state.value,
                "changed": False
            }

        tree.months_since_stripped += 1

        month = tree.months_since_stripped

        events = []

        if (
            month
            == tree.flowering_after_months
        ):
            tree.state = LemonTreeState.FLOWERING

            tree.flowers = 12

            events.append({
                "name": "lemon_tree_begins_flowering",
                "month": month,
                "flowers": tree.flowers
            })

        if (
            month
            >= tree.new_fruit_after_months
        ):
            tree.lemons = 7

            tree.has_lemons = True

            tree.state = LemonTreeState.FRUITING

            tree.flowers = 0

            tree.months_since_stripped = None

            events.append({
                "name": "lemon_tree_new_crop",
                "lemons": 7
            })

        return {
            "name": "lemon_tree_month_passed",
            "month": month,
            "state": tree.state.value,
            "events": events
        }
