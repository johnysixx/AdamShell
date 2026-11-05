from copy import deepcopy
from dataclasses import dataclass

from cats.cat_group_role_state import (
    CatGroupRoleAssignedEvent,
    CatGroupRoleAssignmentDeniedResult,
    CatGroupRoleReleasedEvent,
    CatGroupRoleState,
    CatGroupRoleSuitabilityResult,
)

@dataclass(frozen=True, slots=True)
class CatGroupTraitWeight:
    trait: str
    weight: float

    def __post_init__(self):
        if not isinstance(self.trait, str) or not self.trait:
            raise TypeError("Role trait requires a nonempty name.")
        if not isinstance(self.weight, (int, float)):
            raise TypeError("Role trait weight must be numeric.")


@dataclass(frozen=True, slots=True)
class CatGroupRoleProfile:
    trait_weights: tuple[CatGroupTraitWeight, ...]
    knowledge_weight: float = 0.0
    influence_weight: float = 0.0
    group_scent_weight: float = 0.0

    def __post_init__(self):
        if not isinstance(self.trait_weights, tuple):
            raise TypeError("Role trait weights must be a tuple.")
        if not all(
            isinstance(weight, CatGroupTraitWeight)
            for weight in self.trait_weights
        ):
            raise TypeError("Role trait weights must be typed objects.")


class CatGroupRoleSystem:
    ROLE_PROFILES = {
        "storyteller": CatGroupRoleProfile(
            trait_weights=(
                CatGroupTraitWeight("sociability", 0.45),
                CatGroupTraitWeight("curiosity", 0.35),
            ),
            knowledge_weight=0.2,
        ),
        "scout": CatGroupRoleProfile(
            trait_weights=(
                CatGroupTraitWeight("curiosity", 0.55),
                CatGroupTraitWeight("courage", 0.35),
            ),
            knowledge_weight=0.1,
        ),
        "guardian": CatGroupRoleProfile(
            trait_weights=(
                CatGroupTraitWeight("courage", 0.6),
            ),
            influence_weight=0.4,
        ),
        "kitten_teacher": CatGroupRoleProfile(
            trait_weights=(
                CatGroupTraitWeight("sociability", 0.4),
            ),
            knowledge_weight=0.35,
        ),
        "scent_keeper": CatGroupRoleProfile(
            trait_weights=(
                CatGroupTraitWeight("sociability", 0.3),
            ),
            group_scent_weight=0.5,
        ),
        "mediator": CatGroupRoleProfile(
            trait_weights=(
                CatGroupTraitWeight("sociability", 0.55),
            ),
            influence_weight=0.3,
        ),
    }

    def __init__(self, group_system):
        self.group_system = group_system

    def suitability(
        self,
        group_id,
        cat,
        role,
    ):
        group = self.group_system._group(
            group_id
        )

        if cat.name not in group.members:
            return CatGroupRoleSuitabilityResult(
                role=role,
                eligible=False,
                score=0.0,
                reason="not_group_member",
            )

        profile = self.ROLE_PROFILES.get(
            role
        )

        if profile is None:
            return CatGroupRoleSuitabilityResult(
                role=role,
                eligible=False,
                score=0.0,
                reason="unknown_role",
            )

        traits = cat.personality.traits
        score = 0.0

        for trait_weight in profile.trait_weights:
            trait = trait_weight.trait
            weight = trait_weight.weight
            score += (
                self._number(
                    getattr(
                        traits,
                        trait,
                        0.5,
                    )
                )
                * weight
            )

        score += (
            self._number(
                cat.group.influence
            )
            * profile.influence_weight
        )

        score += (
            cat.knowledge
            .role_knowledge_score()
            * profile.knowledge_weight
        )

        score += (
            self._number(
                cat.group.shared_scent
            )
            * profile.group_scent_weight
        )

        score = min(
            1.0,
            score,
        )

        return CatGroupRoleSuitabilityResult(
            role=role,
            eligible=score >= 0.35,
            score=round(
                score,
                4,
            ),
        )

    def assign(self, group_id, cat, role):
        check = self.suitability(group_id, cat, role)
        if not check.eligible:
            return (
                CatGroupRoleAssignmentDeniedResult(
                    group_id=group_id,
                    cat=cat.name,
                    role=role,
                    reason=(
                        check.reason
                        or 'insufficient_suitability'
                    ),
                )
            )
        existing = (
            cat.group_roles.record(
                role
            )
        )

        if existing is None:
            existing = CatGroupRoleState()

        group = self.group_system._group(
            group_id
        )

        group.roles.assign(
            role,
            cat.name,
        )

        existing.assign_base(
            group_id=group_id,
            role=role,
            score=check.score,
        )

        cat.group_roles.store(
            existing
        )

        cat.group_roles.role_events += 1

        event = CatGroupRoleAssignedEvent(
            group_id=group_id,
            cat=cat.name,
            role=role,
            score=check.score,
        )

        cat.group_roles.record_event(
            event
        )

        group.history.append(
            deepcopy(
                event
            )
        )

        return event

    def release(self, group_id, cat, role, reason='role_released'):
        group = self.group_system._group(group_id)
        group.roles.release_holder(
            role,
            cat.name,
        )
        cat.group_roles.release(
            role
        )

        event = CatGroupRoleReleasedEvent(
            group_id=group_id,
            cat=cat.name,
            role=role,
            reason=reason,
        )

        cat.group_roles.record_event(
            event
        )

        return event

    def holders(self, group_id, role):
        group = self.group_system._group(group_id)
        return list(
            group.roles.holders(
                role
            )
        )

    def _number(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
