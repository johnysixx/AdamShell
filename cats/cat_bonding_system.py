from copy import deepcopy

from cats.cat import Cat


class CatBondingSystem:

    def __init__(
        self,
        cats_layer=None
    ):
        self.cats_layer = cats_layer

    def evaluate(
        self,
        cat,
        other_cat
    ):
        self._require_cat(
            cat
        )

        self._require_cat(
            other_cat
        )

        relation = cat.relationships.get(
            other_cat.name,
            {}
        )

        memory = cat.social_memory.get(
            other_cat.name,
            {}
        )

        familiarity = self._number(
            relation.get(
                "familiarity",
                0.0
            )
        )

        trust = self._number(
            relation.get(
                "trust",
                0.5
            )
        )

        affiliation = self._number(
            relation.get(
                "affiliation",
                0.0
            )
        )

        shared_scent = self._number(
            relation.get(
                "shared_scent",
                0.0
            )
        )

        tension = self._number(
            relation.get(
                "tension",
                0.0
            )
        )

        friendly_count = int(
            memory.get(
                "friendly_count",
                0
            )
        )

        hostile_count = int(
            memory.get(
                "hostile_count",
                0
            )
        )

        eligible = bool(
            familiarity >= 0.70
            and trust >= 0.75
            and affiliation >= 0.65
            and shared_scent >= 0.30
            and tension <= 0.20
            and friendly_count >= 2
            and hostile_count
            <= friendly_count
        )

        strength = self._clamp(
            (
                familiarity
                + trust
                + affiliation
                + shared_scent
            ) / 4.0
            - tension * 0.25
        )

        return {
            "cat": cat.name,
            "other_cat": other_cat.name,
            "eligible": eligible,
            "strength": round(
                strength,
                4
            ),
            "familiarity": familiarity,
            "trust": trust,
            "affiliation": affiliation,
            "shared_scent": shared_scent,
            "tension": tension,
            "friendly_memories": (
                friendly_count
            ),
            "hostile_memories": (
                hostile_count
            )
        }

    def form_bond(
        self,
        cat,
        other_cat
    ):
        first = self.evaluate(
            cat,
            other_cat
        )

        second = self.evaluate(
            other_cat,
            cat
        )

        if (
            not first["eligible"]
            or not second["eligible"]
        ):
            return {
                "name": "cat_bond_not_formed",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "formed": False,
                "reason": (
                    "bond_requirements_not_met"
                ),
                "cat_evaluation": first,
                "other_cat_evaluation": second
            }

        strength = min(
            first["strength"],
            second["strength"]
        )

        self._store_bond(
            cat,
            other_cat,
            strength
        )

        self._store_bond(
            other_cat,
            cat,
            strength
        )

        event = {
            "name": "cat_bond_formed",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "strength": strength,
            "formed": True,
            "behaviors": [
                "mutual_grooming",
                "sleep_together",
                "follow_bonded_cat"
            ]
        }

        self._record_both(
            cat,
            other_cat,
            event
        )

        return event

    def ensure_bond(
        self,
        cat,
        other_cat
    ):
        if self.is_bonded(
            cat,
            other_cat
        ):
            return {
                "name": "cat_bond_preserved",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "formed": True,
                "existing": True
            }

        return self.form_bond(
            cat,
            other_cat
        )

    def mutual_groom(
        self,
        cat,
        other_cat
    ):
        if not self.is_bonded(
            cat,
            other_cat
        ):
            return self._bond_action_denied(
                cat,
                other_cat,
                "mutual_grooming"
            )

        self._strengthen(
            cat,
            other_cat,
            amount=0.03
        )

        self._strengthen(
            other_cat,
            cat,
            amount=0.03
        )

        event = {
            "name": "cats_mutually_groomed",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "bonded": True
        }

        self._record_both(
            cat,
            other_cat,
            event
        )

        return event

    def sleep_together(
        self,
        cat,
        other_cat
    ):
        if not self.is_bonded(
            cat,
            other_cat
        ):
            return self._bond_action_denied(
                cat,
                other_cat,
                "sleep_together"
            )

        if (
            cat.current_layer
            != other_cat.current_layer
        ):
            return {
                "name": "cat_bond_action_denied",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "action": "sleep_together",
                "reason": "different_layers",
                "performed": False
            }

        if not self._same_position(
            cat.position,
            other_cat.position
        ):
            return {
                "name": "cat_bond_action_denied",
                "cat": cat.name,
                "other_cat": other_cat.name,
                "action": "sleep_together",
                "reason": "cats_not_near",
                "performed": False
            }

        cat.state = (
            "resting_with_bonded_cat"
        )

        other_cat.state = (
            "resting_with_bonded_cat"
        )

        event = {
            "name": "bonded_cats_slept_together",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "bonded": True,
            "performed": True
        }

        self._record_both(
            cat,
            other_cat,
            event
        )

        return event

    def follow(
        self,
        cat,
        other_cat
    ):
        if not self.is_bonded(
            cat,
            other_cat
        ):
            return self._bond_action_denied(
                cat,
                other_cat,
                "follow_bonded_cat"
            )

        cat.navigation_target = (
            other_cat.name
        )

        cat.state = (
            "following_bonded_cat"
        )

        event = {
            "name": "cat_following_bonded_cat",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "bonded": True,
            "performed": True
        }

        self._record_both(
            cat,
            other_cat,
            event
        )

        return event

    def is_bonded(
        self,
        cat,
        other_cat
    ):
        bond = cat.bonds.get(
            other_cat.name
        )

        return bool(
            isinstance(
                bond,
                dict
            )
            and bond.get(
                "active",
                False
            )
        )

    def _store_bond(
        self,
        cat,
        other_cat,
        strength
    ):
        cat.bonds[
            other_cat.name
        ] = {
            "other_cat": other_cat.name,
            "active": True,
            "strength": self._clamp(
                strength
            ),
            "groom_count": 0,
            "sleep_count": 0,
            "follow_count": 0
        }

    def _strengthen(
        self,
        cat,
        other_cat,
        amount
    ):
        bond = cat.bonds.get(
            other_cat.name
        )

        if bond is None:
            return

        bond[
            "strength"
        ] = self._clamp(
            self._number(
                bond.get(
                    "strength",
                    0.0
                )
            )
            + amount
        )

    def _bond_action_denied(
        self,
        cat,
        other_cat,
        action
    ):
        return {
            "name": "cat_bond_action_denied",
            "cat": cat.name,
            "other_cat": other_cat.name,
            "action": action,
            "reason": "cats_not_bonded",
            "performed": False
        }

    def _record_both(
        self,
        cat,
        other_cat,
        event
    ):
        cat.social_interactions.append(
            deepcopy(
                event
            )
        )

        other_cat.social_interactions.append(
            deepcopy(
                event
            )
        )

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None
        )

        if callable(
            emit_event
        ):
            emit_event(
                deepcopy(
                    event
                )
            )

    def _same_position(
        self,
        first,
        second
    ):
        if (
            not isinstance(
                first,
                dict
            )
            or not isinstance(
                second,
                dict
            )
        ):
            return False

        return (
            self._number(
                first.get(
                    "x",
                    0.0
                )
            )
            == self._number(
                second.get(
                    "x",
                    0.0
                )
            )
            and self._number(
                first.get(
                    "y",
                    0.0
                )
            )
            == self._number(
                second.get(
                    "y",
                    0.0
                )
            )
            and self._number(
                first.get(
                    "z",
                    0.0
                )
            )
            == self._number(
                second.get(
                    "z",
                    0.0
                )
            )
        )

    def _number(
        self,
        value
    ):
        try:
            return float(
                value
            )
        except (
            TypeError,
            ValueError
        ):
            return 0.0

    def _clamp(
        self,
        value
    ):
        return max(
            0.0,
            min(
                1.0,
                float(
                    value
                )
            )
        )

    def _require_cat(
        self,
        cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatBondingSystem requires Cat."
            )
