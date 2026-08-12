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

        knowledge.setdefault(
            "known_aromas",
            []
        )

        knowledge.setdefault(
            "known_scent_places",
            []
        )

        principles = knowledge.setdefault(
            "known_principles",
            {}
        )

        principles.setdefault(
            "quantum_boxes_are_paired",
            True
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
    def learn_aroma(
        cls,
        cat,
        identity,
        components,
        source="direct_experience"
    ):
        knowledge = cls.ensure_cat_knowledge(
            cat
        )

        normalized = {
            str(key): float(value)
            for key, value
            in dict(components).items()
            if float(value) > 0.0
        }

        known = next(
            (
                item
                for item in knowledge[
                    "known_aromas"
                ]
                if item.get(
                    "identity"
                ) == identity
            ),
            None
        )

        if known is None:
            known = {
                "identity": identity,
                "components": normalized,
                "source": source,
                "encounters": 1,
                "confidence": 0.55
            }

            knowledge[
                "known_aromas"
            ].append(
                known
            )

        else:
            known["encounters"] += 1
            known["source"] = source

            previous = known.setdefault(
                "components",
                {}
            )

            all_keys = set(previous) | set(
                normalized
            )

            for key in all_keys:
                previous[key] = (
                    float(
                        previous.get(
                            key,
                            0.0
                        )
                    )
                    + float(
                        normalized.get(
                            key,
                            0.0
                        )
                    )
                ) / 2.0

            known["confidence"] = min(
                1.0,
                float(
                    known.get(
                        "confidence",
                        0.55
                    )
                )
                + 0.10
            )

        return deepcopy(
            known
        )

    @classmethod
    def recognize_aroma(
        cls,
        cat,
        components,
        minimum_similarity=0.55
    ):
        knowledge = cls.ensure_cat_knowledge(
            cat
        )

        observed = {
            str(key): float(value)
            for key, value
            in dict(components).items()
            if float(value) > 0.0
        }

        matches = []

        for known in knowledge[
            "known_aromas"
        ]:
            similarity = cls._aroma_similarity(
                observed,
                known.get(
                    "components",
                    {}
                )
            )

            if similarity < minimum_similarity:
                continue

            matches.append({
                "identity": known[
                    "identity"
                ],
                "similarity": similarity,
                "confidence": known.get(
                    "confidence",
                    0.5
                ),
                "encounters": known.get(
                    "encounters",
                    1
                )
            })

        matches.sort(
            key=lambda item: (
                item["similarity"],
                item["confidence"]
            ),
            reverse=True
        )

        if not matches:
            return {
                "recognized": False,
                "identity": None,
                "similarity": 0.0,
                "matches": []
            }

        winner = matches[0]

        return {
            "recognized": True,
            "identity": winner[
                "identity"
            ],
            "similarity": winner[
                "similarity"
            ],
            "matches": matches
        }

    @staticmethod
    def _aroma_similarity(
        first,
        second
    ):
        keys = set(first) | set(second)

        if not keys:
            return 0.0

        dot = sum(
            float(first.get(key, 0.0))
            * float(second.get(key, 0.0))
            for key in keys
        )

        first_length = sum(
            float(first.get(key, 0.0)) ** 2
            for key in keys
        ) ** 0.5

        second_length = sum(
            float(second.get(key, 0.0)) ** 2
            for key in keys
        ) ** 0.5

        if (
            first_length == 0.0
            or second_length == 0.0
        ):
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                dot
                / (
                    first_length
                    * second_length
                )
            )
        )

    @classmethod
    def remember_scent_place(
        cls,
        cat,
        layer,
        position,
        source_id,
        recognized_identity=None,
        components=None,
        perceived_intensity=0.0,
        universe_tick=None
    ):
        knowledge = cls.ensure_cat_knowledge(
            cat
        )

        position = cls._position(
            position
        )

        place_id = cls._place_id(
            layer,
            position
        )

        identity = (
            recognized_identity
            or "unknown_aroma"
        )

        memory = next(
            (
                item
                for item
                in knowledge[
                    "known_scent_places"
                ]
                if (
                    item.get(
                        "place_id"
                    ) == place_id
                    and item.get(
                        "identity"
                    ) == identity
                    and item.get(
                        "source_id"
                    ) == source_id
                )
            ),
            None
        )

        if memory is None:
            memory = {
                "place_id": place_id,
                "layer": layer,
                "position": deepcopy(
                    position
                ),
                "source_id": source_id,
                "identity": identity,
                "observations": 1,
                "confidence": (
                    0.60
                    if recognized_identity
                    else 0.30
                ),
                "last_intensity": float(
                    perceived_intensity
                ),
                "strongest_intensity": float(
                    perceived_intensity
                ),
                "components": deepcopy(
                    components or {}
                ),
                "first_seen_tick": (
                    universe_tick
                ),
                "last_seen_tick": (
                    universe_tick
                )
            }

            knowledge[
                "known_scent_places"
            ].append(
                memory
            )

        else:
            memory[
                "observations"
            ] += 1

            memory[
                "last_intensity"
            ] = float(
                perceived_intensity
            )

            memory[
                "strongest_intensity"
            ] = max(
                float(
                    memory.get(
                        "strongest_intensity",
                        0.0
                    )
                ),
                float(
                    perceived_intensity
                )
            )

            memory[
                "last_seen_tick"
            ] = universe_tick

            memory[
                "confidence"
            ] = min(
                1.0,
                float(
                    memory.get(
                        "confidence",
                        0.3
                    )
                )
                + (
                    0.10
                    if recognized_identity
                    else 0.03
                )
            )

            if components:
                memory[
                    "components"
                ] = deepcopy(
                    components
                )

        return deepcopy(
            memory
        )

    @classmethod
    def remember_olfaction(
        cls,
        cat,
        olfaction,
        current_layer,
        universe_tick=None
    ):
        remembered = []

        knowledge = (
            cls.ensure_cat_knowledge(
                cat
            )
        )

        if universe_tick is not None:
            knowledge[
                "scent_clock_tick"
            ] = universe_tick

        for item in olfaction.get(
            "detected_aromas",
            []
        ):
            recognition = item.get(
                "recognition",
                {}
            )

            identity = (
                recognition.get(
                    "identity"
                )
                if recognition.get(
                    "recognized",
                    False
                )
                else None
            )

            position = item.get(
                "position"
            )

            if not isinstance(
                position,
                dict
            ):
                continue

            remembered.append(
                cls.remember_scent_place(
                    cat=cat,
                    layer=current_layer,
                    position=position,
                    source_id=item.get(
                        "entity_id"
                    ),
                    recognized_identity=identity,
                    components=item.get(
                        "raw_components",
                        {}
                    ),
                    perceived_intensity=item.get(
                        "perceived_intensity",
                        0.0
                    ),
                    universe_tick=universe_tick
                )
            )

        ambient = olfaction.get(
            "ambient_aroma"
        )

        if isinstance(
            ambient,
            dict
        ):
            recognition = ambient.get(
                "recognition",
                {}
            )

            identity = (
                recognition.get(
                    "identity"
                )
                if recognition.get(
                    "recognized",
                    False
                )
                else ambient.get(
                    "source"
                )
            )

            remembered.append(
                cls.remember_scent_place(
                    cat=cat,
                    layer=current_layer,
                    position=cat.get(
                        "position",
                        {}
                    ),
                    source_id="ambient",
                    recognized_identity=identity,
                    components=ambient.get(
                        "components",
                        {}
                    ),
                    perceived_intensity=sum(
                        float(value)
                        for value
                        in ambient.get(
                            "components",
                            {}
                        ).values()
                    ),
                    universe_tick=universe_tick
                )
            )

        return remembered

    @classmethod
    def infer_scent_direction(
        cls,
        cat,
        identity,
        layer
    ):
        knowledge = cls.ensure_cat_knowledge(
            cat
        )

        memories = [
            memory
            for memory
            in knowledge.get(
                "known_scent_places",
                []
            )
            if (
                memory.get("identity")
                == identity
                and memory.get("layer")
                == layer
                and isinstance(
                    memory.get(
                        "position"
                    ),
                    dict
                )
                and memory.get(
                    "last_seen_tick"
                ) is not None
            )
        ]

        if len(memories) < 2:
            return {
                "inferred": False,
                "reason": (
                    "not_enough_scent_points"
                )
            }

        memories.sort(
            key=lambda memory: int(
                memory[
                    "last_seen_tick"
                ]
            )
        )

        newest = memories[-1]

        older = next(
            (
                memory
                for memory
                in reversed(
                    memories[:-1]
                )
                if memory.get(
                    "position"
                ) != newest.get(
                    "position"
                )
            ),
            None
        )

        if older is None:
            return {
                "inferred": False,
                "reason": (
                    "no_distinct_scent_positions"
                )
            }

        start = older[
            "position"
        ]

        end = newest[
            "position"
        ]

        vector = {
            axis: (
                float(
                    end.get(
                        axis,
                        0.0
                    )
                )
                - float(
                    start.get(
                        axis,
                        0.0
                    )
                )
            )
            for axis in (
                "x",
                "y",
                "z"
            )
        }

        distance = (
            (
                vector["x"] ** 2
                + vector["y"] ** 2
                + vector["z"] ** 2
            )
            ** 0.5
        )

        if distance <= 0.0:
            return {
                "inferred": False,
                "reason": (
                    "zero_length_scent_direction"
                )
            }

        tick_delta = (
            int(
                newest[
                    "last_seen_tick"
                ]
            )
            - int(
                older[
                    "last_seen_tick"
                ]
            )
        )

        if tick_delta <= 0:
            return {
                "inferred": False,
                "reason": (
                    "scent_order_not_temporal"
                )
            }

        unit_vector = {
            axis: (
                vector[axis]
                / distance
            )
            for axis in (
                "x",
                "y",
                "z"
            )
        }

        current_tick = knowledge.get(
            "scent_clock_tick"
        )

        if current_tick is None:
            newest_age = 0
        else:
            newest_age = max(
                0,
                int(current_tick)
                - int(
                    newest[
                        "last_seen_tick"
                    ]
                )
            )

        freshness = (
            0.5
            ** (
                newest_age
                / 50.0
            )
        )

        confidence = min(
            1.0,
            (
                float(
                    older.get(
                        "confidence",
                        0.0
                    )
                )
                + float(
                    newest.get(
                        "confidence",
                        0.0
                    )
                )
            )
            / 2.0
            * freshness
        )

        return {
            "inferred": True,
            "identity": identity,
            "layer": layer,
            "from_position": deepcopy(
                start
            ),
            "to_position": deepcopy(
                end
            ),
            "vector": vector,
            "unit_vector": unit_vector,
            "distance": distance,
            "tick_delta": tick_delta,
            "newest_age_ticks": newest_age,
            "freshness": freshness,
            "confidence": confidence,
            "from_source_id": older.get(
                "source_id"
            ),
            "to_source_id": newest.get(
                "source_id"
            )
        }

    @classmethod
    def choose_legend_to_share(
        cls,
        storyteller,
        listener,
        universe
    ):
        """
        Vybere legendu, kterou m? smysl
        sd?lit konkr?tn?mu poslucha?i.
        """
        legends = cls.ensure_universe_legends(
            universe
        )

        storyteller_name = storyteller.get(
            "name"
        )

        listener_name = listener.get(
            "name"
        )

        knowledge = cls.ensure_cat_knowledge(
            listener
        )

        already_heard = {
            (
                item.get("legend_id"),
                item.get("storyteller")
            )
            for item
            in knowledge["heard_legends"]
        }

        candidates = []

        for legend in legends:
            if not legend.get(
                "active",
                True
            ):
                continue

            if storyteller_name not in legend.get(
                "reported_by",
                []
            ):
                continue

            if (
                legend.get("legend_id"),
                storyteller_name
            ) in already_heard:
                continue

            candidates.append(
                deepcopy(legend)
            )

        if not candidates:
            return {
                "selected": False,
                "reason": "no_shareable_legend",
                "storyteller": storyteller_name,
                "listener": listener_name
            }

        candidates.sort(
            key=lambda item: (
                float(
                    item.get(
                        "confidence",
                        0.0
                    )
                ),
                int(
                    item.get(
                        "verification_count",
                        0
                    )
                )
            ),
            reverse=True
        )

        return {
            "selected": True,
            "legend": candidates[0],
            "candidate_count": len(
                candidates
            ),
            "storyteller": storyteller_name,
            "listener": listener_name
        }

    @classmethod
    def evaluate_legend_sharing(
        cls,
        storyteller,
        listener,
        legend
    ):
        """
        Rozhodne, zda konkr?tn? ko?ka
        konkr?tn? legendu konkr?tn?mu
        poslucha?i v?bec ?ekne.
        """
        listener_name = listener.get(
            "name"
        )

        traits = storyteller.get(
            "personality",
            {}
        ).get(
            "traits",
            {}
        )

        curiosity = float(
            traits.get(
                "curiosity",
                0.5
            )
        )

        patience = float(
            traits.get(
                "patience",
                0.5
            )
        )

        intellect = float(
            storyteller.get(
                "intellect",
                {}
            ).get(
                "normalized",
                0.5
            )
        )

        trust = cls._trust_in_cat(
            storyteller,
            listener_name
        )

        confidence = float(
            legend.get(
                "confidence",
                0.5
            )
        )

        verification_count = int(
            legend.get(
                "verification_count",
                1
            )
        )

        information_value = min(
            1.0,
            confidence * 0.70
            + min(
                verification_count,
                5
            ) * 0.06
        )

        share_score = (
            0.10
            + trust * 0.30
            + curiosity * 0.20
            + patience * 0.10
            + intellect * 0.10
            + information_value * 0.20
        )

        share_score = max(
            0.0,
            min(
                1.0,
                share_score
            )
        )

        return {
            "share": (
                share_score >= 0.55
            ),
            "score": share_score,
            "trust_in_listener": trust,
            "information_value": (
                information_value
            ),
            "reasons": [
                "relationship_to_listener",
                "information_value",
                "curiosity",
                "patience",
                "intellect"
            ]
        }

    @classmethod
    def share_legend(
        cls,
        storyteller,
        listener,
        universe
    ):
        """
        Kompletn? soci?ln? akt:
        vybere legendu, rozhodne o sd?len?
        a p??padn? ji p?ed? poslucha?i.
        """
        selection = cls.choose_legend_to_share(
            storyteller=storyteller,
            listener=listener,
            universe=universe
        )

        if not selection.get(
            "selected",
            False
        ):
            return {
                "name": "cat_legend_not_shared",
                "storyteller": storyteller.get(
                    "name"
                ),
                "listener": listener.get(
                    "name"
                ),
                "reason": selection.get(
                    "reason"
                ),
                "shared": False
            }

        legend = selection[
            "legend"
        ]

        evaluation = (
            cls.evaluate_legend_sharing(
                storyteller=storyteller,
                listener=listener,
                legend=legend
            )
        )

        if not evaluation[
            "share"
        ]:
            return {
                "name": "cat_legend_not_shared",
                "storyteller": storyteller.get(
                    "name"
                ),
                "listener": listener.get(
                    "name"
                ),
                "legend_id": legend.get(
                    "legend_id"
                ),
                "evaluation": evaluation,
                "reason": (
                    "sharing_not_worthwhile"
                ),
                "shared": False
            }

        heard = cls.hear_legend(
            listener=listener,
            storyteller=storyteller,
            legend=legend
        )

        return {
            "name": "cat_shared_legend",
            "storyteller": storyteller.get(
                "name"
            ),
            "listener": listener.get(
                "name"
            ),
            "legend_id": legend.get(
                "legend_id"
            ),
            "layer": legend.get(
                "layer"
            ),
            "position": deepcopy(
                legend.get(
                    "position"
                )
            ),
            "evaluation": evaluation,
            "heard_legend": heard,
            "shared": True
        }

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