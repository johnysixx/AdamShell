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
    def hear_legend(
        cls,
        listener,
        storyteller,
        legend
    ):
        """
        Poslucha? si ciz? legendu neulo??
        jako fakt, ale jako sly?en? tvrzen?.
        """
        knowledge = cls.ensure_cat_knowledge(
            listener
        )

        storyteller_name = (
            storyteller.get("name")
            if isinstance(storyteller, dict)
            else str(storyteller)
        )

        trust = cls._trust_in_cat(
            listener,
            storyteller_name
        )

        intellect = float(
            listener.get(
                "intellect",
                {}
            ).get(
                "normalized",
                0.5
            )
        )

        source_confidence = float(
            legend.get(
                "confidence",
                0.5
            )
        )

        credibility = (
            source_confidence * 0.45
            + trust * 0.40
            + intellect * 0.15
        )

        heard = next(
            (
                item
                for item in knowledge[
                    "heard_legends"
                ]
                if item.get(
                    "legend_id"
                ) == legend.get(
                    "legend_id"
                )
                and item.get(
                    "storyteller"
                ) == storyteller_name
            ),
            None
        )

        if heard is None:
            heard = {
                "legend_id": legend.get(
                    "legend_id"
                ),
                "claim_type": legend.get(
                    "claim_type"
                ),
                "place_id": legend.get(
                    "place_id"
                ),
                "layer": legend.get(
                    "layer"
                ),
                "position": deepcopy(
                    legend.get(
                        "position"
                    )
                ),
                "storyteller": storyteller_name,
                "trust_in_storyteller": trust,
                "source_confidence": (
                    source_confidence
                ),
                "credibility": credibility,
                "heard_count": 1,
                "verified": False,
                "contradicted": False
            }

            knowledge[
                "heard_legends"
            ].append(
                heard
            )

        else:
            heard["heard_count"] += 1

            heard[
                "trust_in_storyteller"
            ] = trust

            heard[
                "source_confidence"
            ] = source_confidence

            heard["credibility"] = min(
                1.0,
                (
                    heard["credibility"]
                    + credibility
                ) / 2.0
                + 0.03
            )

        return deepcopy(
            heard
        )

    @classmethod
    def verify_heard_legend(
        cls,
        cat,
        place
    ):
        knowledge = cls.ensure_cat_knowledge(
            cat
        )

        verified = []

        for heard in knowledge[
            "heard_legends"
        ]:
            if (
                heard.get("place_id")
                != place.get("place_id")
            ):
                continue

            if heard.get(
                "verified",
                False
            ):
                continue

            heard["verified"] = True
            heard["contradicted"] = False

            trust_change = (
                cls.adjust_storyteller_trust(
                    listener=cat,
                    storyteller_name=heard[
                        "storyteller"
                    ],
                    delta=0.10,
                    reason=(
                        "legend_confirmed_by_"
                        "personal_observation"
                    ),
                    legend_id=heard[
                        "legend_id"
                    ]
                )
            )

            heard[
                "trust_after_verification"
            ] = trust_change[
                "current"
            ]

            record = {
                "legend_id": heard[
                    "legend_id"
                ],
                "place_id": heard[
                    "place_id"
                ],
                "storyteller": heard[
                    "storyteller"
                ],
                "verified_by": cat.get(
                    "name"
                ),
                "credibility_before": (
                    heard["credibility"]
                ),
                "trust_change": (
                    trust_change
                )
            }

            knowledge[
                "verified_legends"
            ].append(
                record
            )

            verified.append(
                deepcopy(record)
            )

        return verified

    @classmethod
    def adjust_storyteller_trust(
        cls,
        listener,
        storyteller_name,
        delta,
        reason,
        legend_id=None
    ):
        relationships = listener.setdefault(
            "relationships",
            {}
        )

        relation = relationships.setdefault(
            storyteller_name,
            {}
        )

        previous = float(
            relation.get(
                "trust",
                0.5
            )
        )

        current = max(
            0.0,
            min(
                1.0,
                previous + float(delta)
            )
        )

        relation["trust"] = current

        history = relation.setdefault(
            "trust_history",
            []
        )

        event = {
            "previous": previous,
            "current": current,
            "delta": current - previous,
            "reason": reason,
            "legend_id": legend_id
        }

        history.append(
            deepcopy(event)
        )

        return deepcopy(
            event
        )

    @classmethod
    def contradict_heard_legend(
        cls,
        cat,
        legend_id,
        reason="personal_observation_contradicted"
    ):
        knowledge = cls.ensure_cat_knowledge(
            cat
        )

        heard = next(
            (
                item
                for item in knowledge[
                    "heard_legends"
                ]
                if item.get(
                    "legend_id"
                ) == legend_id
            ),
            None
        )

        if heard is None:
            return {
                "contradicted": False,
                "reason": "legend_not_heard",
                "legend_id": legend_id
            }

        if heard.get(
            "verified",
            False
        ):
            return {
                "contradicted": False,
                "reason": "legend_already_verified",
                "legend_id": legend_id
            }

        heard["contradicted"] = True
        heard["verified"] = False

        storyteller = heard.get(
            "storyteller"
        )

        trust_change = (
            cls.adjust_storyteller_trust(
                listener=cat,
                storyteller_name=storyteller,
                delta=-0.15,
                reason=reason,
                legend_id=legend_id
            )
        )

        heard[
            "trust_after_contradiction"
        ] = trust_change[
            "current"
        ]

        return {
            "contradicted": True,
            "legend_id": legend_id,
            "storyteller": storyteller,
            "trust_change": trust_change
        }

    @staticmethod
    def _trust_in_cat(
        listener,
        storyteller_name
    ):
        relationships = listener.get(
            "relationships",
            {}
        )

        if isinstance(
            relationships,
            dict
        ):
            relation = relationships.get(
                storyteller_name
            )

            if isinstance(
                relation,
                dict
            ):
                return max(
                    0.0,
                    min(
                        1.0,
                        float(
                            relation.get(
                                "trust",
                                0.5
                            )
                        )
                    )
                )

        return 0.5

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