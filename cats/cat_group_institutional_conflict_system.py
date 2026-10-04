from uuid import uuid4
from cats.cat_culture_objects import CatInstitutionConflict
from cats.cat_group_institutional_conflict_detection_state import (
    CatInstitutionConflictDetectedResult,
    CatInstitutionConflictDetectionDeniedResult,
)
from cats.cat_group_institutional_conflict_escalation_state import (
    CatGroupInstitutionalConflictEvent,
    CatInstitutionConflictEscalationDeniedResult,
)
from cats.cat_group_institutional_conflict_mediation_state import (
    CatInstitutionConflictMediatedEvent,
    CatInstitutionMediationDeniedResult,
)
from cats.cat_group_institutional_conflict_split_state import (
    CatInstitutionalSplitResult,
    CatInstitutionSplitDeniedResult,
)


class CatGroupInstitutionalConflictSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def detect(
        self,
        group_id,
        first_institution,
        second_institution,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        first = (
            group.institutions.get(
                first_institution
            )
        )

        second = (
            group.institutions.get(
                second_institution
            )
        )

        if (
            first is None
            or second is None
        ):
            return (
                CatInstitutionConflictDetectionDeniedResult(
                    reason="unknown_institution",
                )
            )

        shared_roles = tuple(
            sorted(
                set(
                    getattr(
                        first,
                        "roles",
                        [],
                    )
                ).intersection(
                    getattr(
                        second,
                        "roles",
                        [],
                    )
                )
            )
        )

        shared_rituals = tuple(
            sorted(
                set(
                    getattr(
                        first,
                        "rituals",
                        [],
                    )
                ).intersection(
                    getattr(
                        second,
                        "rituals",
                        [],
                    )
                )
            )
        )

        different_purpose = (
            getattr(
                first,
                "purpose",
                None,
            )
            != getattr(
                second,
                "purpose",
                None,
            )
        )

        score = (
            len(shared_roles)
            * 0.3
            + len(shared_rituals)
            * 0.15
            + (
                0.15
                if (
                    different_purpose
                    and shared_roles
                )
                else 0.0
            )
        )

        score = min(
            1.0,
            score,
        )

        if score >= 0.6:
            status = (
                "institutional_conflict"
            )

        elif score >= 0.25:
            status = (
                "institutional_friction"
            )

        else:
            status = (
                "institutionally_compatible"
            )

        return (
            CatInstitutionConflictDetectedResult(
                group_id=group_id,
                first_institution=first_institution,
                second_institution=second_institution,
                shared_roles=shared_roles,
                shared_rituals=shared_rituals,
                different_purpose=different_purpose,
                score=round(
                    score,
                    4,
                ),
                status=status,
                conflict=(
                    status
                    != "institutionally_compatible"
                ),
            )
        )

    def escalate(
        self,
        group_id,
        first_institution,
        second_institution,
        issue,
        intensity=0.5,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        first = (
            group.institutions.get(
                first_institution
            )
        )

        second = (
            group.institutions.get(
                second_institution
            )
        )

        if (
            first is None
            or second is None
        ):
            return (
                CatInstitutionConflictEscalationDeniedResult(
                    reason="unknown_institution",
                )
            )

        intensity = self._clamp(
            intensity
        )

        conflict_id = (
            "institution_conflict_"
            + uuid4().hex[:8]
        )

        continuity_loss = (
            0.2
            * intensity
        )

        for institution in (
            first,
            second,
        ):
            institution.continuity = max(
                0.0,
                float(
                    getattr(
                        institution,
                        "continuity",
                        1.0,
                    )
                )
                - continuity_loss,
            )

        conflict = CatInstitutionConflict(
            **{
                "id": conflict_id,
                "first_institution":
                    first_institution,
                "second_institution":
                    second_institution,
                "issue": issue,
                "intensity": intensity,
                "resolved": False,
                "mediator": None,
                "history": [],
            }
        )

        group.institution_conflicts[
            conflict_id
        ] = conflict

        event = (
            CatGroupInstitutionalConflictEvent(
                group_id=group_id,
                conflict_id=conflict_id,
                first_institution=first_institution,
                second_institution=second_institution,
                issue=issue,
                intensity=intensity,
            )
        )

        conflict.history.append(
            event.to_dict()
        )

        group.history.append(
            event.to_dict()
        )

        return event

    def mediate(
        self,
        group_id,
        conflict_id,
        mediator,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        conflict = (
            group.institution_conflicts.get(
                conflict_id
            )
        )

        if conflict is None:
            return (
                CatInstitutionMediationDeniedResult(
                    reason="unknown_conflict",
                )
            )

        if (
            "mediator"
            not in mediator.group_roles.active
        ):
            return (
                CatInstitutionMediationDeniedResult(
                    reason="cat_not_mediator",
                )
            )

        influence = float(
            mediator.group.influence
        )

        reduction = min(
            0.5,
            0.15
            + influence
            * 0.3,
        )

        conflict.intensity = (
            self._clamp(
                conflict.intensity
                - reduction
            )
        )

        conflict.mediator = (
            mediator.name
        )

        if (
            conflict.intensity
            <= 0.2
        ):
            conflict.resolved = True

        if conflict.resolved:
            self._restore_institutions(
                group,
                conflict,
                amount=0.1,
            )

        event = (
            CatInstitutionConflictMediatedEvent(
                group_id=group_id,
                conflict_id=conflict_id,
                mediator=mediator.name,
                intensity=conflict.intensity,
                resolved=conflict.resolved,
            )
        )

        conflict.history.append(
            event.to_dict()
        )

        group.history.append(
            event.to_dict()
        )

        return event

    def institutional_split(
        self,
        group_id,
        conflict_id,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        conflict = (
            group.institution_conflicts.get(
                conflict_id
            )
        )

        if conflict is None:
            return (
                CatInstitutionSplitDeniedResult(
                    reason="unknown_conflict",
                )
            )

        if (
            conflict.resolved
            or conflict.intensity < 0.75
        ):
            return (
                CatInstitutionSplitDeniedResult(
                    reason="conflict_not_severe_enough",
                )
            )

        first = (
            group.institutions[
                conflict.first_institution
            ]
        )

        second = (
            group.institutions[
                conflict.second_institution
            ]
        )

        first.continuity = max(
            0.0,
            float(
                first.continuity
            )
            - 0.25,
        )

        second.continuity = max(
            0.0,
            float(
                second.continuity
            )
            - 0.25,
        )

        return (
            CatInstitutionalSplitResult(
                group_id=group_id,
                conflict_id=conflict_id,
                institutions=(
                    conflict.first_institution,
                    conflict.second_institution,
                ),
            )
        )

    def _restore_institutions(self, group, conflict, amount):
        for name in (conflict.first_institution, conflict.second_institution):
            institution = group.institutions[name]
            institution.continuity = min(1.0, float(institution.continuity) + amount)

    def _clamp(self, value):
        return max(0.0, min(1.0, float(value)))
