from cats.cat_birth_effect_resolver import (
    CatBirthEffectResolver
)

from .cat_trait_dice_mapping import CatTraitDiceMapping
from .cat_genetics_validator import CatGeneticsValidator
from .cat_birth_objects import (
    CatBirthProfile,
    CatCanonicalBirthResolution,
)

class CatBirthResolver:

    def __init__(
        self,
        universe,
        meeting_place
    ):
        self.universe = universe
        self.meeting_place = meeting_place

        self.birth_effect_resolver = (
            CatBirthEffectResolver(
                universe,
                meeting_place
            )
        )
        self.history = []

        self.genetics_validator = (
            CatGeneticsValidator()
        )

        self.trait_dice_mapping = (
            CatTraitDiceMapping()
        )

        self.canonical_profile = CatBirthProfile(
            color="black",
            fur_length="short",
            pattern="solid",
            eye_color="green",
            sex="female",
        )

        self.canonical_profile_occurrences = 0

        self.queen_elisabeth_profile = CatBirthProfile(
            color="white",
            fur_length="long",
            pattern="tabby",
            eye_color="green",
            sex="female",
        )

        self.queen_elisabeth_profile_occurrences = 0

        self.garfield_profile = CatBirthProfile(
            color="orange",
            fur_length="short",
            pattern="tabby",
            eye_color="yellow",
            sex="male",
        )

        self.garfield_profile_occurrences = 0

        self.woodoo_birth_count = 0
        self.woodoo_rebirth_chance = 0.001

    def resolve_profile(
        self,
        rng=None
    ):
        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        if cats_layer is None:
            raise RuntimeError(
                "Cat birth requires cats_layer."
            )

        cat_d20_result = (
            self.meeting_place
            .turn_cat_d20_in_box(
                rng=rng
            )
        )

        dice_result = (
            self.meeting_place
            .dice_box
            .rotate_all_dice(
                rng=rng
            )
        )

        rolls = {
            result["die"]: result
            for result in dice_result["results"]
        }

        percentile_history = [
            dict(
                rolls["d10_percentile"]
            )
        ]

        cronenbergs_created = []

        while (
            percentile_history[-1]["value"]
            == 0
        ):
            cronenberg = (
                self.universe
                .create_cronenberg_from_quantum_error(
                    RuntimeError(
                        "Cat birth percentile zero."
                    ),
                    "cat_birth_resolver",
                    "percentile_zero"
                )
            )

            cronenbergs_created.append(
                cronenberg
            )

            if len(percentile_history) >= 100:
                raise RuntimeError(
                    "Percentile die remained zero "
                    "after 100 rotations."
                )

            reroll = (
                self.meeting_place
                .dice_box
                .rotate_named_die(
                    "d10_percentile",
                    rng=rng
                )
            )

            percentile_history.append(
                dict(reroll)
            )

        final_percentile = (
            percentile_history[-1]
        )

        mapping = (
            self.trait_dice_mapping.resolve(
                cat_d20_result["value"]
            )
        )

        trait_options = {
            "color": cats_layer.allowed_colors,
            "fur_length": (
                cats_layer.allowed_fur_lengths
            ),
            "pattern": (
                cats_layer.allowed_patterns
            ),
            "eye_color": (
                cats_layer.allowed_eye_colors
            ),
            "sex": cats_layer.allowed_sexes
        }

        profile = {}

        for die_name, trait in (
            mapping["die_to_trait"].items()
        ):
            profile[trait] = (
                self._select_for_cat_birth(
                    options=trait_options[trait],
                    die_value=rolls[
                        die_name
                    ]["raw_value"],
                    die_sides=rolls[
                        die_name
                    ]["sides"],
                    cat_d20_value=(
                        cat_d20_result["value"]
                    )
                )
            )

        rolled_profile = CatBirthProfile(
            color=profile["color"],
            fur_length=profile["fur_length"],
            pattern=profile["pattern"],
            eye_color=profile["eye_color"],
            sex=profile["sex"],
        )

        genetics_result = (
            self._resolve_genetic_conflicts(
                profile=rolled_profile,
                rolls=rolls,
                mapping=mapping,
                rng=rng
            )
        )

        profile = genetics_result["profile"]

        woodoo_white_trace_applied = bool(
            getattr(
                self.universe,
                "next_cat_birth_white",
                False
            )
        )

        if woodoo_white_trace_applied:
            profile = profile.with_trait(
                "color",
                "white"
            )

            self.universe.next_cat_birth_white = False

        force_next_woodoo = bool(
            getattr(
                self.universe,
                "force_next_woodoo_birth",
                False
            )
        )

        if force_next_woodoo:
            self.universe.force_next_woodoo_birth = False

            self.canonical_profile_occurrences += 1
            self.woodoo_birth_count += 1

            woodoo_profile = (
                self.canonical_profile.with_trait(
                    "eye_color",
                    "gold"
                )
            )

            canonical_result = (
                CatCanonicalBirthResolution(
                    matched=True,
                    occurrence=(
                        self.canonical_profile_occurrences
                    ),
                    identity="woodoo",
                    profile=woodoo_profile,
                    special_birth_event=(
                        "woodoo_rebirth_chaos"
                    ),
                    woodoo_rebirth=True,
                    woodoo_birth_number=(
                        self.woodoo_birth_count
                    ),
                    forced_birth=True,
                    forced_by="garfield",
                )
            )

        else:
            canonical_result = (
                self._resolve_canonical_profile(
                    profile,
                    rng=rng
                )
            )

        resolved_profile = canonical_result.profile

        event = {
            "name": "cat_birth_profile_resolved",
            "profile": resolved_profile,
            "rolled_profile": rolled_profile,
            "canonical": canonical_result,
            "genetics": genetics_result,
            "trait_dice_mapping": mapping,
            "cat_d20": cat_d20_result,
            "dice_box": dice_result,
            "percentile": final_percentile,
            "percentile_history": (
                percentile_history
            ),
            "percentile_reroll_count": (
                len(percentile_history) - 1
            ),
            "cronenbergs_created": (
                cronenbergs_created
            ),
            "cronenberg_count": len(
                cronenbergs_created
            ),
            "woodoo_white_trace_applied": (
                woodoo_white_trace_applied
            ),
            "resolved": True,
            "visibility": (
                "secret_cat_birth_event"
            )
        }

        self.history.append(
            event
        )

        self.universe.quantum_events.append(
            event
        )

        return event

    def create_cat(
        self,
        name=None,
        rng=None,
        source="cat_birth_resolver"
    ):
        birth = self.resolve_profile(
            rng=rng
        )

        profile = birth["profile"]
        canonical = birth["canonical"]

        if not isinstance(
            profile,
            CatBirthProfile
        ):
            raise TypeError(
                "birth profile must be a CatBirthProfile object."
            )

        if not isinstance(
            canonical,
            CatCanonicalBirthResolution
        ):
            raise TypeError(
                "birth canonical state must be a "
                "CatCanonicalBirthResolution object."
            )

        identity = canonical.identity

        if identity is not None:
            cat_name = identity

        elif name is not None:
            cat_name = str(
                name
            )

        else:
            cat_name = (
                self._next_generated_cat_name()
            )

        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        if cats_layer is None:
            raise RuntimeError(
                "Cat creation requires cats_layer."
            )

        existing = next(
            (
                cat
                for cat in cats_layer.cats
                if cat.name == cat_name
            ),
            None
        )

        if existing is not None:
            return {
                "name": "cat_birth_manifestation_failed",
                "result": "cat_name_already_exists",
                "cat_name": cat_name,
                "cat": existing,
                "birth": birth,
                "created": False
            }

        manifestation = (
            self.universe.manifest_cat(
                name=cat_name,
                source=source,
                color=profile.color,
                fur_length=profile.fur_length,
                pattern=profile.pattern,
                eye_color=profile.eye_color,
                sex=profile.sex
            )
        )

        if manifestation is None:
            return {
                "name": "cat_birth_manifestation_failed",
                "result": "manifest_cat_failed",
                "cat_name": cat_name,
                "birth": birth,
                "created": False
            }

        cat = manifestation[
            "cat"
        ]

        rolled_birth_profile = (
            birth["rolled_profile"]
        )

        if not isinstance(
            rolled_birth_profile,
            CatBirthProfile
        ):
            raise TypeError(
                "rolled birth profile must be a "
                "CatBirthProfile object."
            )

        cat.birth_profile = profile
        cat.rolled_birth_profile = (
            rolled_birth_profile
        )
        cat.birth_canonical = canonical

        cat.birth_genetics = (
            birth["genetics"]
        )

        cat.birth_trait_dice_mapping = (
            birth["trait_dice_mapping"]
        )

        cat.birth_percentile = dict(
            birth["percentile"]
        )

        cat.canonical_identity = (
            identity
        )

        if identity is not None:
            trait_name = (
                f"canonical_cat_{identity}"
            )

            if trait_name not in cat.special_traits:
                cat.special_traits.append(
                    trait_name
                )

            if identity not in cat.special_traits:
                cat.special_traits.append(
                    identity
                )

        special_birth_result = (
            self.birth_effect_resolver
            .execute(
                identity=identity,
                cat_name=cat_name,
                rng=rng,
                special_birth_event=(
                    canonical.special_birth_event
                )
            )
        )

        event = {
            "name": "cat_born_from_dice",
            "cat": cat_name,
            "cat_id": getattr(
                cat,
                "id",
                None
            ),
            "identity": identity,
            "profile": profile.to_dict(),
            "canonical_occurrence": (
                canonical.occurrence
            ),
            "special_birth_event": (
                canonical.special_birth_event
            ),
            "special_birth_result": (
                special_birth_result
            ),
            "birth": birth,
            "created": True
        }

        self.history.append(
            event
        )

        self.universe.quantum_events.append(
            event
        )

        # ------------------------------------------------
        # A cat born through CatBirthResolver arrives at the
        # MeetingPlace through the ordinary cat lifecycle.
        #
        # manifest_cat() only creates the cat.
        # admit_cat() handles alarm, bartender decision,
        # Bouncer admission and normal post-entry service.
        # ------------------------------------------------
        arrival = (
            self.meeting_place
            .admit_cat(
                cat,
                bartender_available=True
            )
        )

        return {
            **event,
            "cat": cat,
            "manifestation": manifestation
        }

    def _next_generated_cat_name(
        self
    ):
        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        existing_names = {
            cat.name
            for cat in (
                cats_layer.cats
                if cats_layer is not None
                else []
            )
        }

        number = 1

        while True:
            candidate = (
                f"cat_{number:04d}"
            )

            if candidate not in existing_names:
                return candidate

            number += 1

    def _resolve_genetic_conflicts(
        self,
        profile,
        rolls,
        mapping,
        rng=None
    ):
        if not isinstance(profile, CatBirthProfile):
            raise TypeError(
                "profile must be a CatBirthProfile object."
            )

        current_profile = profile

        conflict_history = []
        cronenbergs_created = []

        die_to_trait = dict(
            mapping["die_to_trait"]
        )

        trait_to_die = dict(
            mapping["trait_to_die"]
        )

        trait_options = {
            "color": (
                self.universe
                .cats_layer
                .allowed_colors
            ),
            "pattern": (
                self.universe
                .cats_layer
                .allowed_patterns
            ),
            "sex": (
                self.universe
                .cats_layer
                .allowed_sexes
            ),
            "eye_color": (
                self.universe
                .cats_layer
                .allowed_eye_colors
            ),
            "fur_length": (
                self.universe
                .cats_layer
                .allowed_fur_lengths
            )
        }

        for attempt in range(1, 101):
            validation = (
                self.genetics_validator.validate(
                    current_profile
                )
            )

            if validation["valid"]:
                return {
                    "valid": True,
                    "profile": current_profile,
                    "validation": validation,
                    "conflict_count": len(
                        conflict_history
                    ),
                    "conflict_history": (
                        conflict_history
                    ),
                    "cronenbergs_created": (
                        cronenbergs_created
                    ),
                    "cronenberg_count": len(
                        cronenbergs_created
                    )
                }

            conflicting_trait = (
                validation.get(
                    "conflicting_trait"
                )
            )

            reroll_die = (
                trait_to_die.get(
                    conflicting_trait
                )
            )

            trait = die_to_trait.get(
                reroll_die
            )

            if reroll_die is None or trait is None:
                raise RuntimeError(
                    "Genetic conflict has no "
                    "rerollable responsible die."
                )

            previous_value = (
                current_profile.trait_value(
                    trait
                )
            )

            reroll = (
                self.meeting_place
                .dice_box
                .rotate_named_die(
                    reroll_die,
                    rng=rng
                )
            )

            new_value = (
                self._select_for_cat_birth(
                    options=trait_options[trait],
                    die_value=reroll[
                        "raw_value"
                    ],
                    die_sides=reroll[
                        "sides"
                    ],
                    cat_d20_value=(
                        mapping["cat_d20_value"]
                    )
                )
            )

            current_profile = (
                current_profile.with_trait(
                    trait,
                    new_value
                )
            )

            rolls[
                reroll_die
            ] = reroll

            conflict_event = {
                "name": (
                    "cat_birth_genetic_"
                    "conflict_resolved"
                ),
                "attempt": attempt,
                "reason": validation[
                    "reason"
                ],
                "trait": trait,
                "die": reroll_die,
                "previous_value": (
                    previous_value
                ),
                "new_value": new_value,
                "reroll": dict(reroll)
            }

            conflict_history.append(
                conflict_event
            )

            cronenberg = (
                self.universe
                .create_cronenberg_from_quantum_error(
                    RuntimeError(
                        "Impossible cat genetic "
                        "combination."
                    ),
                    "cat_birth_resolver",
                    "genetic_conflict"
                )
            )

            cronenbergs_created.append(
                cronenberg
            )

        raise RuntimeError(
            "Cat genetics remained invalid "
            "after 100 corrective rerolls."
        )

    def _resolve_canonical_profile(
        self,
        profile,
        rng=None
    ):
        if not isinstance(profile, CatBirthProfile):
            raise TypeError(
                "profile must be a CatBirthProfile object."
            )

        if profile == self.queen_elisabeth_profile:
            self.queen_elisabeth_profile_occurrences += 1
            occurrence = (
                self.queen_elisabeth_profile_occurrences
            )
            identity = (
                "queen_elisabeth"
                if occurrence == 1
                else (
                    "mia"
                    if occurrence == 2
                    else None
                )
            )

            return CatCanonicalBirthResolution(
                matched=True,
                occurrence=occurrence,
                identity=identity,
                profile=profile,
                special_birth_event=(
                    "mia_birth_global_rotation"
                    if identity == "mia"
                    else (
                        "queen_elisabeth_birth_effects"
                        if identity == "queen_elisabeth"
                        else None
                    )
                ),
            )

        if profile == self.garfield_profile:
            self.garfield_profile_occurrences += 1
            occurrence = (
                self.garfield_profile_occurrences
            )

            return CatCanonicalBirthResolution(
                matched=True,
                occurrence=occurrence,
                identity=(
                    "garfield"
                    if occurrence == 1
                    else None
                ),
                profile=profile,
                special_birth_event=(
                    "garfield_birth_effect_combination"
                    if occurrence == 1
                    else None
                ),
            )

        if profile != self.canonical_profile:
            return CatCanonicalBirthResolution(
                matched=False,
                occurrence=0,
                identity=None,
                profile=profile,
                special_birth_event=None,
            )

        self.canonical_profile_occurrences += 1
        occurrence = (
            self.canonical_profile_occurrences
        )
        resolved_profile = profile

        if occurrence == 1:
            identity = "pazuzu"
            special_birth_event = (
                "pazuzu_birth_dice_resonance"
            )

        elif occurrence == 2:
            identity = "gib"
            resolved_profile = (
                profile.with_trait(
                    "fur_length",
                    "long"
                )
            )
            special_birth_event = (
                "gib_global_dice_resonance"
            )

        elif occurrence == 3:
            identity = "woodoo"
            resolved_profile = (
                profile.with_trait(
                    "eye_color",
                    "gold"
                )
            )
            special_birth_event = (
                "woodoo_birth_chaos"
            )
            self.woodoo_birth_count += 1

        else:
            rebirth = self._resolve_woodoo_rebirth(
                profile=profile,
                rng=rng
            )
            identity = rebirth.identity
            resolved_profile = rebirth.profile
            special_birth_event = (
                rebirth.special_birth_event
            )

        is_rebirth = (
            identity == "woodoo"
            and occurrence > 3
        )

        return CatCanonicalBirthResolution(
            matched=True,
            occurrence=occurrence,
            identity=identity,
            profile=resolved_profile,
            special_birth_event=(
                special_birth_event
            ),
            woodoo_rebirth=is_rebirth,
            woodoo_birth_number=(
                self.woodoo_birth_count
                if is_rebirth
                else None
            ),
            rebirth_probability=(
                self.woodoo_rebirth_chance
                if is_rebirth
                else None
            ),
        )

    def _resolve_woodoo_rebirth(
        self,
        profile,
        rng=None
    ):
        if not isinstance(profile, CatBirthProfile):
            raise TypeError(
                "profile must be a CatBirthProfile object."
            )

        if self.woodoo_birth_count < 1:
            return CatCanonicalBirthResolution(
                matched=False,
                occurrence=0,
                identity=None,
                profile=profile,
                special_birth_event=None,
            )

        if rng is None:
            import random
            rng = random

        reborn = (
            rng.random()
            < self.woodoo_rebirth_chance
        )

        if not reborn:
            return CatCanonicalBirthResolution(
                matched=False,
                occurrence=0,
                identity=None,
                profile=profile,
                special_birth_event=None,
            )

        self.woodoo_birth_count += 1
        woodoo_profile = CatBirthProfile(
            color="black",
            fur_length="short",
            pattern="solid",
            eye_color="gold",
            sex="female",
        )

        return CatCanonicalBirthResolution(
            matched=False,
            occurrence=0,
            identity="woodoo",
            profile=woodoo_profile,
            special_birth_event=(
                "woodoo_rebirth_chaos"
            ),
            woodoo_rebirth=True,
            woodoo_birth_number=(
                self.woodoo_birth_count
            ),
            rebirth_probability=(
                self.woodoo_rebirth_chance
            ),
        )

    @staticmethod
    def _select_for_cat_birth(
        options,
        die_value,
        die_sides,
        cat_d20_value
    ):
        if not options:
            raise ValueError(
                "Cat property options cannot be empty."
            )

        die_value = int(
            die_value
        )

        die_sides = int(
            die_sides
        )

        cat_d20_value = int(
            cat_d20_value
        )

        if die_value < 1 or die_value > die_sides:
            raise ValueError(
                "Die value is outside its valid range."
            )

        combined_position = (
            (cat_d20_value - 1)
            * die_sides
            + (die_value - 1)
        )

        index = (
            combined_position
            % len(options)
        )

        return options[index]

    @staticmethod
    def _select(
        options,
        value
    ):
        if not options:
            raise ValueError(
                "Cat property options cannot be empty."
            )

        index = (
            int(value) - 1
        ) % len(options)

        return options[index]