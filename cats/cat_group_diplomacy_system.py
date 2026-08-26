from copy import deepcopy

from cats.cat_group_memory_system import (
    CatGroupMemorySystem
)


class CatGroupDiplomacySystem:

    def __init__(
        self,
        group_system
    ):
        self.group_system = group_system

        self.memory = (
            CatGroupMemorySystem(
                group_system
            )
        )

    def evaluate(
        self,
        group_id,
        other_group_id
    ):
        group = self.group_system._group(
            group_id
        )

        memory = (
            self.memory.relation_memory(
                group_id,
                other_group_id
            )
        )

        score = (
            memory[
                "peaceful_encounters"
            ] * 0.08
            + memory[
                "cooperations"
            ] * 0.18
            - memory[
                "conflicts"
            ] * 0.10
            - memory[
                "betrayals"
            ] * 0.40
            - memory[
                "defeats"
            ] * 0.04
        )

        score = max(
            -1.0,
            min(
                1.0,
                score
            )
        )

        if (
            other_group_id
            in group[
                "alliances"
            ]
        ):
            status = "allied"

        elif score >= 0.60:
            status = "friendly"

        elif score >= 0.25:
            status = "tolerant"

        elif score > -0.25:
            status = "neutral"

        elif score > -0.60:
            status = "rival"

        else:
            status = "hostile"

        result = {
            "group_id": group_id,
            "other_group_id": other_group_id,
            "score": round(
                score,
                4
            ),
            "status": status,
            "memory": deepcopy(
                memory
            )
        }

        group[
            "diplomacy"
        ][
            other_group_id
        ] = deepcopy(
            result
        )

        return result

    def mutual_relation(
        self,
        first_group_id,
        second_group_id
    ):
        first = self.evaluate(
            first_group_id,
            second_group_id
        )

        second = self.evaluate(
            second_group_id,
            first_group_id
        )

        return {
            "first": first,
            "second": second,
            "mutual_score": round(
                (
                    first[
                        "score"
                    ]
                    + second[
                        "score"
                    ]
                ) / 2.0,
                4
            )
        }
