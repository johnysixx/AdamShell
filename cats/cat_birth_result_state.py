from dataclasses import dataclass, field

from cats.cat_birth_objects import (
    CatBirthGeneticsResult,
    CatBirthPercentileResult,
    CatBirthProfile,
    CatCanonicalBirthResolution,
)
from cats.cat_trait_dice_mapping import CatTraitDiceMappingResult


@dataclass(slots=True, frozen=True)
class CatBirthProfileResolvedEvent:
    profile: CatBirthProfile
    rolled_profile: CatBirthProfile
    canonical: CatCanonicalBirthResolution
    genetics: CatBirthGeneticsResult
    trait_dice_mapping: CatTraitDiceMappingResult
    percentile: CatBirthPercentileResult
    cat_d20: object = None
    dice_box: object = None
    cronenbergs_created: tuple[object, ...] = ()
    woodoo_white_trace_applied: bool = False
    name: str = field(default="cat_birth_profile_resolved", init=False)
    resolved: bool = field(default=True, init=False)
    visibility: str = field(default="secret_cat_birth_event", init=False)

    @property
    def percentile_history(self):
        return self.percentile.history

    @property
    def percentile_reroll_count(self):
        return self.percentile.reroll_count

    @property
    def cronenberg_count(self):
        return len(self.cronenbergs_created)


@dataclass(slots=True, frozen=True)
class CatBirthManifestationFailedResult:
    result: str
    cat_name: str
    birth: CatBirthProfileResolvedEvent
    cat: object = None
    name: str = field(default="cat_birth_manifestation_failed", init=False)
    created: bool = field(default=False, init=False)


@dataclass(slots=True, frozen=True)
class CatBornFromDiceEvent:
    cat: object
    cat_name: str
    identity: str | None
    profile: CatBirthProfile
    canonical_occurrence: int
    special_birth_event: str | None
    special_birth_result: object
    birth: CatBirthProfileResolvedEvent
    manifestation: object
    cat_id: str | None = None
    name: str = field(default="cat_born_from_dice", init=False)
    created: bool = field(default=True, init=False)
