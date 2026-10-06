from cats.cat_social_objects import (
    CatGroupKnowledgeRecord,
    CatGroupKnowledgeTransmission,
)
from cats.cat_group_innovation_tree_system import CatGroupInnovationTreeSystem
from copy import deepcopy
from uuid import uuid4
from cats.cat_culture_objects import CatGroupInnovation
from cats.cat_group_innovation_creation_state import (
    CatGroupInnovationCreatedEvent,
    CatGroupInnovationCreationDeniedResult,
)
from cats.cat_group_innovation_trial_state import (
    CatGroupInnovationTrialDeniedResult,
    CatGroupInnovationTrialResult,
)


class CatGroupInnovationSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def combine(
        self,
        group_id,
        knowledge_ids,
        name,
        category,
        procedure,
        parent_innovation_id=None,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        unique_knowledge_ids = []

        for knowledge_id in knowledge_ids:
            if (
                knowledge_id
                not in unique_knowledge_ids
            ):
                unique_knowledge_ids.append(
                    knowledge_id
                )

        if len(unique_knowledge_ids) < 2:
            return (
                CatGroupInnovationCreationDeniedResult(
                    reason=(
                        "at_least_two_knowledge_sources_required"
                    ),
                )
            )

        source_records = []

        for knowledge_id in unique_knowledge_ids:
            record = (
                group.knowledge.get(
                    knowledge_id
                )
            )

            if record is None:
                return (
                    CatGroupInnovationCreationDeniedResult(
                        reason="missing_knowledge",
                        missing=knowledge_id,
                    )
                )

            source_records.append(
                record
            )

        confidence = (
            sum(
                float(
                    getattr(
                        source,
                        "confidence",
                        0.0,
                    )
                )
                for source
                in source_records
            )
            / len(source_records)
        )

        confidence = self._clamp(
            confidence
            * 0.7
        )

        innovation_id = (
            "cat_innovation_"
            + uuid4().hex[:8]
        )

        innovation = CatGroupInnovation(
            innovation_id=innovation_id,
            name=name,
            category=category,
            source_knowledge=list(
                unique_knowledge_ids
            ),
            procedure=deepcopy(
                procedure
            ),
            origin_group=group_id,
            confidence=confidence,
            verified=False,
            successful_trials=0,
            failed_trials=0,
        )

        group.innovations[
            innovation_id
        ] = innovation

        CatGroupInnovationTreeSystem(
            self.group_system
        ).register(
            group_id,
            innovation_id,
            parent_innovation_id=
                parent_innovation_id,
        )

        group.knowledge[
            innovation_id
        ] = CatGroupKnowledgeRecord(
            knowledge_id=innovation_id,
            category=category,
            content=deepcopy(
                procedure
            ),
            origin_cat=None,
            origin_group=group_id,
            source_type="innovation",
            confidence=innovation.confidence,
            verified=False,
            verification_count=0,
            contradiction_count=0,
            transmission_path=[
                CatGroupKnowledgeTransmission(
                    type="innovation",
                    group=group_id,
                )
            ],
        )

        event = (
            CatGroupInnovationCreatedEvent(
                group_id=group_id,
                innovation_id=innovation_id,
                innovation_name=name,
                sources=tuple(
                    unique_knowledge_ids
                ),
                confidence=(
                    innovation.confidence
                ),
            )
        )

        group.history.append(
            deepcopy(event)
        )

        return event

    def trial(
        self,
        group_id,
        innovation_id,
        success,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        innovation = (
            group.innovations.get(
                innovation_id
            )
        )

        if innovation is None:
            return (
                CatGroupInnovationTrialDeniedResult(
                    reason="unknown_innovation",
                )
            )

        was_successful = bool(
            success
        )

        if was_successful:
            innovation.successful_trials += 1

            innovation.confidence = (
                self._clamp(
                    innovation.confidence
                    + 0.15
                )
            )

        else:
            innovation.failed_trials += 1

            innovation.confidence = (
                self._clamp(
                    innovation.confidence
                    - 0.2
                )
            )

        if (
            innovation.successful_trials
            >= 2
            and innovation.confidence
            >= 0.7
        ):
            innovation.verified = True

        knowledge = (
            group.knowledge[
                innovation_id
            ]
        )

        knowledge.confidence = (
            innovation.confidence
        )

        knowledge.verified = (
            innovation.verified
        )

        if was_successful:
            knowledge.verification_count += 1

        else:
            knowledge.contradiction_count += 1

        return (
            CatGroupInnovationTrialResult(
                group_id=group_id,
                innovation_id=innovation_id,
                success=was_successful,
                confidence=(
                    innovation.confidence
                ),
                verified=(
                    innovation.verified
                ),
            )
        )

    def _clamp(self, value):
        return max(0.0, min(1.0, float(value)))
