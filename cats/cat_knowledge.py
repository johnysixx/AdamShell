from copy import deepcopy


class CatKnowledge:

    @classmethod
    def ensure_cat_knowledge(
        cls,
        cat
    ):
        knowledge = cat.setdefault(
            "knowledge",
            {}
        )

        knowledge.setdefault(
            "known_places",
            []
        )

        knowledge.setdefault(
            "heard_legends",
            []
        )

        knowledge.setdefault(
            "verified_legends",
            []
        )

        return knowledge

    @classmethod
    def ensure_universe_legends(
        cls,
        universe
    ):
        if not hasattr(
            universe,
            "cat_legends"
        ):
            universe.cat_legends = []

        return universe.cat_legends

    @classmethod
    def remember_place(
        cls,
        cat,
        layer,
        position,
        source="direct_exploration",
        safe=None,
        danger=None,
        universe_tick=None,
        details=None
    ):
        knowledge = cls.ensure_cat_knowledge(
            cat
        )

        normalized_position = (
            cls._position(
                position
            )
        )

        place = cls._find_place(
            knowledge["known_places"],
            layer=layer,
            position=normalized_position
        )

        if place is None:
            place = {
                "place_id": (
                    cls._place_id(
                        layer,
                        normalized_position
                    )
                ),
                "layer": str(layer),
                "position": deepcopy(
                    normalized_position
                ),
                "discovered_by": cat.get(
                    "name"
                ),
                "first_source": source,
                "last_source": source,
                "visit_count": 1,
                "confidence": 0.55,
                "safe_observations": 0,
                "danger_observations": 0,
                "first_seen_tick": universe_tick,
                "last_seen_tick": universe_tick,
                "details": deepcopy(
                    details or {}
                )
            }

            knowledge[
                "known_places"
            ].append(
                place
            )

        else:
            place["visit_count"] += 1
            place["last_source"] = source
            place["last_seen_tick"] = (
                universe_tick
            )

            place["confidence"] = min(
                1.0,
                float(
                    place.get(
                        "confidence",
                        0.55
                    )
                )
                + 0.10
            )

            if details:
                place.setdefault(
                    "details",
                    {}
                ).update(
                    deepcopy(details)
                )

        if safe is True:
            place["safe_observations"] += 1

        if danger is True:
            place["danger_observations"] += 1

        observations = (
            place["safe_observations"]
            + place["danger_observations"]
        )

        if observations:
            place["safety"] = (
                place[
                    "safe_observations"
                ]
                / observations
            )
        else:
            place["safety"] = None

        return deepcopy(
            place
        )

    @classmethod
    def publish_legend(
        cls,
        universe,
        cat,
        place,
        claim_type="place_discovered"
    ):
        legends = cls.ensure_universe_legends(
            universe
        )

        place_id = place[
            "place_id"
        ]

        legend = next(
            (
                item
                for item in legends
                if item.get(
                    "place_id"
                ) == place_id
                and item.get(
                    "claim_type"
                ) == claim_type
            ),
            None
        )

        cat_name = cat.get(
            "name"
        )

        if legend is None:
            legend = {
                "legend_id": (
                    f"cat_legend_"
                    f"{len(legends) + 1:04d}"
                ),
                "claim_type": claim_type,
                "place_id": place_id,
                "layer": place["layer"],
                "position": deepcopy(
                    place["position"]
                ),
                "discoverer": cat_name,
                "reported_by": [
                    cat_name
                ],
                "verification_count": 1,
                "confidence": min(
                    1.0,
                    float(
                        place.get(
                            "confidence",
                            0.55
                        )
                    )
                ),
                "safety": place.get(
                    "safety"
                ),
                "active": True
            }

            legends.append(
                legend
            )

        else:
            reporters = legend.setdefault(
                "reported_by",
                []
            )

            if cat_name not in reporters:
                reporters.append(
                    cat_name
                )

            legend[
                "verification_count"
            ] += 1

            legend["confidence"] = min(
                1.0,
                float(
                    legend.get(
                        "confidence",
                        0.5
                    )
                )
                + 0.08
            )

            if (
                place.get("safety")
                is not None
            ):
                previous_safety = (
                    legend.get(
                        "safety"
                    )
                )

                if previous_safety is None:
                    legend["safety"] = (
                        place["safety"]
                    )

                else:
                    legend["safety"] = (
                        previous_safety
                        + place["safety"]
                    ) / 2.0

        return deepcopy(
            legend
        )

    @classmethod
    def _find_place(
        cls,
        places,
        layer,
        position
    ):
        place_id = cls._place_id(
            layer,
            position
        )

        return next(
            (
                place
                for place in places
                if place.get(
                    "place_id"
                ) == place_id
            ),
            None
        )

    @staticmethod
    def _position(
        position
    ):
        if not isinstance(
            position,
            dict
        ):
            return {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }

        return {
            "x": float(
                position.get(
                    "x",
                    0.0
                )
            ),
            "y": float(
                position.get(
                    "y",
                    0.0
                )
            ),
            "z": float(
                position.get(
                    "z",
                    0.0
                )
            )
        }

    @classmethod
    def _place_id(
        cls,
        layer,
        position
    ):
        position = cls._position(
            position
        )

        # Zaokrouhlení vytvoří praktickou
        # oblast místo přesného matematického bodu.
        return (
            f"{layer}:"
            f"{position['x']:.2f}:"
            f"{position['y']:.2f}:"
            f"{position['z']:.2f}"
        )