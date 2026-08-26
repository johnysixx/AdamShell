from copy import deepcopy

from cats.cat import Cat


class CatTerritorySystem:

    def __init__(
        self,
        cats_layer=None
    ):
        self.cats_layer = cats_layer

    def claim(
        self,
        cat,
        layer=None,
        location=None,
        strength=0.6
    ):
        self._require_cat(
            cat
        )

        layer = (
            layer
            if layer is not None
            else cat.current_layer
        )

        location = (
            location
            if location is not None
            else cat.location
        )

        key = self._territory_key(
            layer,
            location
        )

        previous = cat.territories.get(
            key
        )

        if previous is None:
            claim = {
                "owner": cat.name,
                "layer": layer,
                "location": location,
                "strength": self._clamp(
                    strength
                ),
                "scent_marks": 1
            }

            cat.territories[
                key
            ] = claim
        else:
            claim = previous

            claim[
                "strength"
            ] = self._clamp(
                max(
                    float(
                        claim.get(
                            "strength",
                            0.0
                        )
                    ),
                    float(
                        strength
                    )
                )
            )

            claim[
                "scent_marks"
            ] = int(
                claim.get(
                    "scent_marks",
                    0
                )
            ) + 1

        event = {
            "name": "cat_claimed_territory",
            "cat": cat.name,
            "territory": key,
            "layer": layer,
            "location": location,
            "strength": claim[
                "strength"
            ],
            "scent_marks": claim[
                "scent_marks"
            ]
        }

        self._record(
            cat,
            event
        )

        return deepcopy(
            claim
        )

    def scent_mark(
        self,
        cat,
        layer=None,
        location=None
    ):
        self._require_cat(
            cat
        )

        layer = (
            layer
            if layer is not None
            else cat.current_layer
        )

        location = (
            location
            if location is not None
            else cat.location
        )

        key = self._territory_key(
            layer,
            location
        )

        if key not in cat.territories:
            return self.claim(
                cat=cat,
                layer=layer,
                location=location,
                strength=0.5
            )

        claim = cat.territories[
            key
        ]

        claim[
            "scent_marks"
        ] = int(
            claim.get(
                "scent_marks",
                0
            )
        ) + 1

        claim[
            "strength"
        ] = self._clamp(
            float(
                claim.get(
                    "strength",
                    0.0
                )
            )
            + 0.05
        )

        event = {
            "name": "cat_scent_marked_territory",
            "cat": cat.name,
            "territory": key,
            "strength": claim[
                "strength"
            ],
            "scent_marks": claim[
                "scent_marks"
            ]
        }

        self._record(
            cat,
            event
        )

        return deepcopy(
            claim
        )

    def context(
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

        claim = self.claim_at(
            cat=cat,
            layer=cat.current_layer,
            location=cat.location
        )

        if claim is None:
            return {
                "owns_here": False,
                "intrusion": False,
                "accepted": False,
                "claim_strength": 0.0,
                "territory": None
            }

        relation = cat.relationships.get(
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

        accepted = bool(
            affiliation >= 0.65
            or shared_scent >= 0.50
            or (
                familiarity >= 0.70
                and trust >= 0.80
            )
        )

        return {
            "owns_here": True,
            "intrusion": not accepted,
            "accepted": accepted,
            "claim_strength": self._number(
                claim.get(
                    "strength",
                    0.0
                )
            ),
            "territory": self._territory_key(
                claim.get(
                    "layer"
                ),
                claim.get(
                    "location"
                )
            )
        }

    def claim_at(
        self,
        cat,
        layer,
        location
    ):
        self._require_cat(
            cat
        )

        exact_key = self._territory_key(
            layer,
            location
        )

        claim = cat.territories.get(
            exact_key
        )

        if claim is not None:
            return claim

        layer_key = self._territory_key(
            layer,
            None
        )

        return cat.territories.get(
            layer_key
        )

    def _territory_key(
        self,
        layer,
        location
    ):
        return (
            f"{layer}::"
            f"{location if location is not None else '*'}"
        )

    def _record(
        self,
        cat,
        event
    ):
        cat.social_interactions.append(
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
                "CatTerritorySystem requires Cat."
            )
