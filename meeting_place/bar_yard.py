from .bar_objects import LemonTree
from .lemon_tree_state import LemonTreeState
from .bar_yard_event_state import (
    LemonNotFoundResult,
    LemonPickedResult,
    LemonTreeBeginsFloweringEvent,
    LemonTreeMonthPassedResult,
    LemonTreeNewCropEvent,
)


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
            new_fruit_after_months=6,
        )

    def pick_lemon(
        self,
        picker,
    ):
        tree = self.lemon_tree

        if (
            not tree.has_lemons
            or tree.lemons <= 0
        ):
            return LemonNotFoundResult(
                picker=picker,
            )

        tree.lemons -= 1

        if tree.lemons <= 0:
            tree.lemons = 0
            tree.has_lemons = False

            tree.state = (
                LemonTreeState.STRIPPED
            )

            tree.months_since_stripped = 0

        return LemonPickedResult(
            picker=picker,
            lemons_remaining=(
                tree.lemons
            ),
        )

    def advance_month(
        self
    ):
        tree = self.lemon_tree

        if (
            tree.months_since_stripped
            is None
        ):
            return (
                LemonTreeMonthPassedResult(
                    state=tree.state,
                    changed=False,
                )
            )

        tree.months_since_stripped += 1

        month = (
            tree.months_since_stripped
        )

        events = []

        if (
            month
            == tree.flowering_after_months
        ):
            tree.state = (
                LemonTreeState.FLOWERING
            )

            tree.flowers = 12

            events.append(
                LemonTreeBeginsFloweringEvent(
                    month=month,
                    flowers=tree.flowers,
                )
            )

        if (
            month
            >= tree.new_fruit_after_months
        ):
            tree.lemons = 7
            tree.has_lemons = True

            tree.state = (
                LemonTreeState.FRUITING
            )

            tree.flowers = 0

            tree.months_since_stripped = (
                None
            )

            events.append(
                LemonTreeNewCropEvent(
                    lemons=tree.lemons,
                )
            )

        return LemonTreeMonthPassedResult(
            month=month,
            state=tree.state,
            changed=bool(events),
            events=tuple(events),
        )
