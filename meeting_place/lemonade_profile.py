class LemonadeBatchProfile:

    TRAIT_NAMES = (
        "acidity",
        "sweetness",
        "bitterness",
        "viscosity",
        "stability",
        "dark_energy_affinity",
        "growth_efficiency",
        "cat_scent",
        "quantum_coherence"
    )

    def build(self, cronenbergs):
        cronenbergs = list(cronenbergs)

        total_mass = sum(
            max(
                0.0,
                float(
                    getattr(
                        cronenberg,
                        "size",
                        1.0
                    )
                )
            )
            for cronenberg in cronenbergs
        )

        if not cronenbergs or total_mass <= 0.0:
            return self.empty_profile()

        weighted_traits = {}

        for trait_name in self.TRAIT_NAMES:
            weighted_total = 0.0

            for cronenberg in cronenbergs:
                mass = max(
                    0.0,
                    float(
                        getattr(
                            cronenberg,
                            "size",
                            1.0
                        )
                    )
                )

                traits = getattr(
                    cronenberg,
                    "traits",
                    None
                )

                if traits is None:
                    trait_value = 1.0
                else:
                    trait_value = float(
                        traits.value_for(
                            trait_name,
                            1.0
                        )
                    )

                weighted_total += (
                    trait_value * mass
                )

            weighted_traits[trait_name] = round(
                weighted_total / total_mass,
                4
            )

        entangled_pairs = (
            self._find_entangled_pairs(
                cronenbergs
            )
        )

        entanglement_strength = round(
            sum(
                pair["strength"]
                for pair in entangled_pairs
            ),
            4
        )

        coherence_bonus = min(
            0.50,
            entanglement_strength * 0.10
        )

        instability_penalty = min(
            0.30,
            entanglement_strength * 0.05
        )

        weighted_traits[
            "quantum_coherence"
        ] = round(
            min(
                2.50,
                weighted_traits[
                    "quantum_coherence"
                ] + coherence_bonus
            ),
            4
        )

        weighted_traits[
            "stability"
        ] = round(
            max(
                0.10,
                weighted_traits[
                    "stability"
                ] - instability_penalty
            ),
            4
        )

        dominant_trait = max(
            weighted_traits,
            key=weighted_traits.get
        )

        return {
            "traits": weighted_traits,
            "source_count": len(
                cronenbergs
            ),
            "source_mass": round(
                total_mass,
                4
            ),
            "source_cronenbergs": [
                cronenberg.name
                for cronenberg
                in cronenbergs
            ],
            "entangled_pair_count": len(
                entangled_pairs
            ),
            "entanglement_strength": (
                entanglement_strength
            ),
            "entangled_pairs": (
                entangled_pairs
            ),
            "dominant_trait": (
                dominant_trait
            )
        }

    def _find_entangled_pairs(
        self,
        cronenbergs
    ):
        by_id = {
            cronenberg.id: cronenberg
            for cronenberg in cronenbergs
        }

        found_pairs = []
        seen_pairs = set()

        for cronenberg in cronenbergs:
            for link in getattr(
                cronenberg,
                "quantum_links",
                []
            ):
                target_id = link.get(
                    "target_id"
                )

                if target_id not in by_id:
                    continue

                pair_key = tuple(
                    sorted(
                        (
                            cronenberg.id,
                            target_id
                        )
                    )
                )

                if pair_key in seen_pairs:
                    continue

                seen_pairs.add(pair_key)

                reverse_links = [
                    reverse_link
                    for reverse_link in getattr(
                        by_id[target_id],
                        "quantum_links",
                        []
                    )
                    if reverse_link.get(
                        "target_id"
                    ) == cronenberg.id
                ]

                forward_strength = float(
                    link.get(
                        "strength",
                        0.0
                    )
                )

                reverse_strength = max(
                    (
                        float(
                            reverse_link.get(
                                "strength",
                                0.0
                            )
                        )
                        for reverse_link
                        in reverse_links
                    ),
                    default=0.0
                )

                pair_strength = round(
                    max(
                        forward_strength,
                        reverse_strength
                    ),
                    4
                )

                found_pairs.append({
                    "cronenberg_ids": list(
                        pair_key
                    ),
                    "strength": pair_strength,
                    "link_types": sorted({
                        link.get(
                            "link_type"
                        ),
                        *[
                            reverse_link.get(
                                "link_type"
                            )
                            for reverse_link
                            in reverse_links
                        ]
                    })
                })

        return found_pairs

    def empty_profile(self):
        return {
            "traits": {
                trait_name: 0.0
                for trait_name
                in self.TRAIT_NAMES
            },
            "source_count": 0,
            "source_mass": 0.0,
            "source_cronenbergs": [],
            "entangled_pair_count": 0,
            "entanglement_strength": 0.0,
            "entangled_pairs": [],
            "dominant_trait": None
        }
