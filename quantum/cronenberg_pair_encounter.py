from copy import deepcopy


class CronenbergPairEncounter:

    def __init__(self):
        self.name = "cronenberg_pair_encounter"
        self.history = []

    def detect(
        self,
        first,
        second,
        universe_tick=None
    ):
        if first is second:
            return self._not_encountered(
                reason="same_object"
            )

        if getattr(first, "type", None) != "cronenberg":
            return self._not_encountered(
                reason="first_not_cronenberg"
            )

        if getattr(second, "type", None) != "cronenberg":
            return self._not_encountered(
                reason="second_not_cronenberg"
            )

        if not first.is_alive or not second.is_alive:
            return self._not_encountered(
                reason="dead_member"
            )

        first_state = getattr(
            first,
            "quantum_state",
            {}
        )

        second_state = getattr(
            second,
            "quantum_state",
            {}
        )

        first_pair_id = first_state.get(
            "pair_id"
        )

        second_pair_id = second_state.get(
            "pair_id"
        )

        if (
            first_pair_id is None
            or first_pair_id != second_pair_id
        ):
            return self._not_encountered(
                reason="different_quantum_pair"
            )

        if (
            first_state.get("counterpart_id")
            != second.id
            or second_state.get("counterpart_id")
            != first.id
        ):
            return self._not_encountered(
                reason="counterpart_mismatch"
            )

        if first.location != second.location:
            return self._not_encountered(
                reason="different_location"
            )

        event = {
            "name": "cronenberg_quantum_pair_encountered",
            "encountered": True,
            "pair_id": first_pair_id,
            "location": first.location,
            "participants": [
                first.id,
                second.id
            ],
            "spins": {
                first.id: first_state.get("spin"),
                second.id: second_state.get("spin")
            },
            "universe_tick": universe_tick,
            "resolution": None
        }

        self.history.append(
            event
        )

        return deepcopy(event)

    def _not_encountered(self, reason):
        return {
            "name": "cronenberg_quantum_pair_not_encountered",
            "encountered": False,
            "reason": reason
        }

    @property
    def public_state(self):
        return {
            "name": self.name,
            "encounter_count": len(
                self.history
            )
        }