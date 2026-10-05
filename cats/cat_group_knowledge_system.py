from copy import deepcopy

from cats.cat_group_knowledge_contribution_state import (
    CatGroupKnowledgeContributedEvent,
    CatGroupKnowledgeContributionDeniedResult,
)
from cats.cat_group_knowledge_propagation_state import (
    CatGroupKnowledgePropagatedResult,
    CatGroupKnowledgePropagationDeniedResult,
)
from cats.cat_group_knowledge_sharing_state import (
    CatGroupKnowledgeSharedResult,
    CatGroupKnowledgeShareDeniedResult,
)
from cats.cat_group_knowledge_transmission_state import (
    CatGroupKnowledgeTransmittedEvent,
    CatGroupKnowledgeTransmissionDeniedResult,
)
from cats.cat_group_knowledge_verification_state import (
    CatGroupKnowledgeVerificationDeniedResult,
    CatGroupKnowledgeVerifiedEvent,
)
from cats.cat_social_objects import (
    CatGroupKnowledgeRecord,
    CatGroupKnowledgeTransmission,
)


class CatGroupKnowledgeSystem:

    def __init__(
        self,
        group_system,
    ):
        self.group_system = group_system

    def contribute(
        self,
        group_id,
        cat,
        knowledge_id,
        content,
        category,
        confidence=1.0,
        verified=True,
        source_type="personal_experience",
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        if cat.name not in group.members:
            return (
                CatGroupKnowledgeContributionDeniedResult(
                    reason="cat_not_group_member",
                )
            )

        confidence = self._clamp(
            confidence
        )

        existing = (
            group.knowledge.get(
                knowledge_id
            )
        )

        record = (
            CatGroupKnowledgeRecord(
                knowledge_id=knowledge_id,
                category=category,
                content=deepcopy(
                    content
                ),
                origin_cat=cat.name,
                origin_group=group_id,
                source_type=source_type,
                confidence=confidence,
                verified=bool(
                    verified
                ),
                verification_count=(
                    1
                    if verified
                    else 0
                ),
                contradiction_count=0,
                transmission_path=[
                    CatGroupKnowledgeTransmission(
                        type=source_type,
                        source=cat.name,
                        group=group_id,
                    )
                ],
            )
        )

        if existing is not None:
            record.verification_count += int(
                getattr(
                    existing,
                    "verification_count",
                    0,
                )
            )

            record.contradiction_count += int(
                getattr(
                    existing,
                    "contradiction_count",
                    0,
                )
            )

        group.knowledge[
            knowledge_id
        ] = record

        self._offer_to_member(
            cat,
            record,
            transmission=
                "personal_experience",
        )

        event = (
            CatGroupKnowledgeContributedEvent(
                group_id=group_id,
                cat=cat.name,
                knowledge_id=knowledge_id,
                category=category,
                confidence=confidence,
                verified=bool(
                    verified
                ),
            )
        )

        group.history.append(
            event.to_dict()
        )

        return event

    def share_with_group_members(
        self,
        group_id,
        cats,
        knowledge_id,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        record = (
            group.knowledge.get(
                knowledge_id
            )
        )

        if record is None:
            return (
                CatGroupKnowledgeShareDeniedResult(
                    reason="unknown_knowledge",
                )
            )

        members = (
            self.group_system._member_objects(
                group,
                cats,
            )
        )

        receivers = []

        for cat in members:
            self._offer_to_member(
                cat,
                record,
                transmission="own_group",
            )

            receivers.append(
                cat.name
            )

        return (
            CatGroupKnowledgeSharedResult(
                group_id=group_id,
                knowledge_id=knowledge_id,
                receivers=tuple(
                    receivers
                ),
            )
        )

    def transmit_between_groups(
        self,
        source_group_id,
        target_group_id,
        knowledge_id,
        transmission="allied_group",
    ):
        source = (
            self.group_system._group(
                source_group_id
            )
        )

        target = (
            self.group_system._group(
                target_group_id
            )
        )

        record = (
            source.knowledge.get(
                knowledge_id
            )
        )

        if record is None:
            return (
                CatGroupKnowledgeTransmissionDeniedResult(
                    reason="source_does_not_know",
                )
            )

        copied = deepcopy(
            record
        )

        copied.confidence = (
            self._clamp(
                float(
                    getattr(
                        copied,
                        "confidence",
                        0.0,
                    )
                )
                * 0.88
            )
        )

        copied.verified = False

        copied.transmission_path.append(
            CatGroupKnowledgeTransmission(
                type=transmission,
                source_group=
                    source_group_id,
                target_group=
                    target_group_id,
            )
        )

        existing = (
            target.knowledge.get(
                knowledge_id
            )
        )

        if existing is None:
            target.knowledge[
                knowledge_id
            ] = copied

        elif (
            copied.confidence
            > float(
                getattr(
                    existing,
                    "confidence",
                    0.0,
                )
            )
        ):
            target.knowledge[
                knowledge_id
            ] = copied

        event = (
            CatGroupKnowledgeTransmittedEvent(
                source_group=
                    source_group_id,
                target_group=
                    target_group_id,
                knowledge_id=
                    knowledge_id,
                confidence=
                    copied.confidence,
                transmission=
                    transmission,
            )
        )

        source.history.append(
            event.to_dict()
        )

        target.history.append(
            event.to_dict()
        )

        return event

    def propagate_to_members(
        self,
        group_id,
        cats,
        knowledge_id,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        record = (
            group.knowledge.get(
                knowledge_id
            )
        )

        if record is None:
            return (
                CatGroupKnowledgePropagationDeniedResult(
                    reason="unknown_knowledge",
                )
            )

        receivers = []

        for cat in (
            self.group_system._member_objects(
                group,
                cats,
            )
        ):
            self._offer_to_member(
                cat,
                record,
                transmission=
                    "group_propagation",
            )

            receivers.append(
                cat.name
            )

        return (
            CatGroupKnowledgePropagatedResult(
                group_id=group_id,
                knowledge_id=knowledge_id,
                receivers=tuple(
                    receivers
                ),
            )
        )

    def verify(
        self,
        group_id,
        cat,
        knowledge_id,
        confirmed,
    ):
        group = (
            self.group_system._group(
                group_id
            )
        )

        record = (
            group.knowledge.get(
                knowledge_id
            )
        )

        if record is None:
            return (
                CatGroupKnowledgeVerificationDeniedResult(
                    reason="unknown_knowledge",
                )
            )

        if confirmed:
            record.verification_count += 1

            record.confidence = (
                self._clamp(
                    float(
                        record.confidence
                    )
                    + 0.12
                )
            )

            record.verified = True
            outcome = "confirmed"

        else:
            record.contradiction_count += 1

            record.confidence = (
                self._clamp(
                    float(
                        record.confidence
                    )
                    - 0.25
                )
            )

            if record.confidence < 0.35:
                record.verified = False

            outcome = "contradicted"

        member_knowledge = (
            cat.knowledge
            .group_received_knowledge
        )

        personal = (
            member_knowledge.get(
                knowledge_id
            )
        )

        if personal is not None:
            personal.confidence = (
                record.confidence
            )

            personal.verified = bool(
                confirmed
            )

            personal.verified_by = (
                cat.name
            )

        event = (
            CatGroupKnowledgeVerifiedEvent(
                group_id=group_id,
                cat=cat.name,
                knowledge_id=knowledge_id,
                outcome=outcome,
                confidence=
                    record.confidence,
            )
        )

        group.history.append(
            event.to_dict()
        )

        return event

    def _offer_to_member(
        self,
        cat,
        record,
        transmission,
    ):
        received = (
            cat.knowledge
            .group_received_knowledge
        )

        copy = deepcopy(
            record
        )

        if (
            transmission
            != "personal_experience"
        ):
            copy.verified = False

        copy.received_via = (
            transmission
        )

        received[
            record.knowledge_id
        ] = copy

        return copy

    def _clamp(
        self,
        value,
    ):
        return max(
            0.0,
            min(
                1.0,
                float(
                    value
                ),
            ),
        )
