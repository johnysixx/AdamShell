from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LemonadeTraitProfile:
    acidity: float = 0.0
    sweetness: float = 0.0
    bitterness: float = 0.0
    viscosity: float = 0.0
    stability: float = 0.0
    dark_energy_affinity: float = 0.0
    growth_efficiency: float = 0.0
    cat_scent: float = 0.0
    quantum_coherence: float = 0.0

    TRAIT_NAMES = (
        "acidity",
        "sweetness",
        "bitterness",
        "viscosity",
        "stability",
        "dark_energy_affinity",
        "growth_efficiency",
        "cat_scent",
        "quantum_coherence",
    )

    def value_for(self, trait_name, default=0.0):
        if trait_name not in self.TRAIT_NAMES:
            return default
        return getattr(self, trait_name)

    def to_dict(self):
        return {
            trait_name: self.value_for(trait_name)
            for trait_name in self.TRAIT_NAMES
        }


@dataclass(frozen=True, slots=True)
class LemonadeEntangledPair:
    cronenberg_ids: tuple[str, ...]
    strength: float
    link_types: tuple[str | None, ...]

    def to_dict(self):
        return {
            "cronenberg_ids": list(self.cronenberg_ids),
            "strength": self.strength,
            "link_types": list(self.link_types),
        }


@dataclass(frozen=True, slots=True)
class LemonadeProfile:
    traits: LemonadeTraitProfile
    source_mass: float
    source_cronenbergs: tuple[str, ...]
    entanglement_strength: float
    entangled_pairs: tuple[LemonadeEntangledPair, ...]
    dominant_trait: str | None

    def __post_init__(self):
        if not isinstance(self.traits, LemonadeTraitProfile):
            raise TypeError(
                "Lemonade profile traits must be LemonadeTraitProfile."
            )
        if any(
            not isinstance(pair, LemonadeEntangledPair)
            for pair in self.entangled_pairs
        ):
            raise TypeError(
                "Lemonade profile entangled pairs must be objects."
            )

    @property
    def source_count(self):
        return len(self.source_cronenbergs)

    @property
    def entangled_pair_count(self):
        return len(self.entangled_pairs)

    def to_dict(self):
        return {
            "traits": self.traits.to_dict(),
            "source_count": self.source_count,
            "source_mass": self.source_mass,
            "source_cronenbergs": list(self.source_cronenbergs),
            "entangled_pair_count": self.entangled_pair_count,
            "entanglement_strength": self.entanglement_strength,
            "entangled_pairs": [
                pair.to_dict()
                for pair in self.entangled_pairs
            ],
            "dominant_trait": self.dominant_trait,
        }


@dataclass(frozen=True, slots=True)
class LemonadeBatchRecord:
    amount_litres: float
    source: str
    profile: LemonadeProfile

    def __post_init__(self):
        if not isinstance(self.profile, LemonadeProfile):
            raise TypeError(
                "Lemonade batch profile must be LemonadeProfile."
            )

    def to_dict(self):
        return {
            "amount_litres": self.amount_litres,
            "source": self.source,
            "profile": self.profile.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class CronenbergProcessingRecord:
    batch: int
    cronenbergs: tuple[str, ...]
    lemonade_amount: float
    lemonade_profile: LemonadeProfile | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "batch",
            int(self.batch),
        )
        object.__setattr__(
            self,
            "cronenbergs",
            tuple(
                str(name)
                for name in self.cronenbergs
            ),
        )
        object.__setattr__(
            self,
            "lemonade_amount",
            float(self.lemonade_amount),
        )

        if (
            self.lemonade_profile is not None
            and not isinstance(
                self.lemonade_profile,
                LemonadeProfile,
            )
        ):
            raise TypeError(
                "Cronenberg processing profile must be "
                "a LemonadeProfile object."
            )

    def to_dict(self):
        snapshot = {
            "batch": self.batch,
            "cronenbergs": list(
                self.cronenbergs
            ),
            "lemonade_amount": (
                self.lemonade_amount
            ),
        }

        if self.lemonade_profile is not None:
            snapshot[
                "lemonade_profile"
            ] = (
                self.lemonade_profile.to_dict()
            )

        return snapshot


class LemonadeBatchProfile:

    TRAIT_NAMES = LemonadeTraitProfile.TRAIT_NAMES

    def build(self, cronenbergs):
        cronenbergs = list(cronenbergs)

        total_mass = sum(
            max(
                0.0,
                float(
                    getattr(
                        cronenberg,
                        "size",
                        1.0,
                    )
                ),
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
                            1.0,
                        )
                    ),
                )

                traits = getattr(
                    cronenberg,
                    "traits",
                    None,
                )

                if traits is None:
                    trait_value = 1.0
                else:
                    trait_value = float(
                        traits.value_for(
                            trait_name,
                            1.0,
                        )
                    )

                weighted_total += (
                    trait_value * mass
                )

            weighted_traits[trait_name] = round(
                weighted_total / total_mass,
                4,
            )

        entangled_pairs = tuple(
            self._find_entangled_pairs(
                cronenbergs
            )
        )

        entanglement_strength = round(
            sum(
                pair.strength
                for pair in entangled_pairs
            ),
            4,
        )

        coherence_bonus = min(
            0.50,
            entanglement_strength * 0.10,
        )

        instability_penalty = min(
            0.30,
            entanglement_strength * 0.05,
        )

        weighted_traits[
            "quantum_coherence"
        ] = round(
            min(
                2.50,
                weighted_traits[
                    "quantum_coherence"
                ] + coherence_bonus,
            ),
            4,
        )

        weighted_traits[
            "stability"
        ] = round(
            max(
                0.10,
                weighted_traits[
                    "stability"
                ] - instability_penalty,
            ),
            4,
        )

        dominant_trait = max(
            weighted_traits,
            key=weighted_traits.get,
        )

        return LemonadeProfile(
            traits=LemonadeTraitProfile(
                **weighted_traits
            ),
            source_mass=round(
                total_mass,
                4,
            ),
            source_cronenbergs=tuple(
                cronenberg.name
                for cronenberg in cronenbergs
            ),
            entanglement_strength=(
                entanglement_strength
            ),
            entangled_pairs=entangled_pairs,
            dominant_trait=dominant_trait,
        )

    def _find_entangled_pairs(
        self,
        cronenbergs,
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
                [],
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
                            target_id,
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
                        [],
                    )
                    if reverse_link.get(
                        "target_id"
                    ) == cronenberg.id
                ]

                forward_strength = float(
                    link.get(
                        "strength",
                        0.0,
                    )
                )

                reverse_strength = max(
                    (
                        float(
                            reverse_link.get(
                                "strength",
                                0.0,
                            )
                        )
                        for reverse_link
                        in reverse_links
                    ),
                    default=0.0,
                )

                pair_strength = round(
                    max(
                        forward_strength,
                        reverse_strength,
                    ),
                    4,
                )

                link_types = {
                    link.get("link_type"),
                    *[
                        reverse_link.get(
                            "link_type"
                        )
                        for reverse_link
                        in reverse_links
                    ],
                }

                found_pairs.append(
                    LemonadeEntangledPair(
                        cronenberg_ids=pair_key,
                        strength=pair_strength,
                        link_types=tuple(
                            sorted(
                                link_types,
                                key=lambda value: (
                                    value is None,
                                    str(value),
                                ),
                            )
                        ),
                    )
                )

        return found_pairs

    def empty_profile(self):
        return LemonadeProfile(
            traits=LemonadeTraitProfile(),
            source_mass=0.0,
            source_cronenbergs=(),
            entanglement_strength=0.0,
            entangled_pairs=(),
            dominant_trait=None,
        )
