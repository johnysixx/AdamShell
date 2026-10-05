from uuid import uuid4

from cats.cat_federation import (
    CatFederation,
)
from cats.cat_group_diplomacy_system import (
    CatGroupDiplomacySystem,
)
from cats.cat_group_federation_admission_state import (
    CatFederationAdmissionDeniedResult,
    CatFederationAdmissionSkippedResult,
    CatGroupJoinedFederationEvent,
)
from cats.cat_group_federation_creation_state import (
    CatFederationCreatedResult,
)
from cats.cat_group_federation_knowledge_state import (
    CatFederationKnowledgeDeniedResult,
    CatFederationKnowledgeSharedResult,
)
from cats.cat_group_federation_leave_state import (
    CatFederationLeaveDeniedResult,
    CatGroupLeftFederationResult,
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
)


class CatGroupFederationSystem:

    def __init__(
        self,
        group_system,
    ):
        self.group_system = group_system

        self.federations = {}

        self.diplomacy = (
            CatGroupDiplomacySystem(
                group_system
            )
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                group_system
            )
        )

    def create(
        self,
        founder_group_id,
        name=None,
    ):
        founder = (
            self.group_system._group(
                founder_group_id
            )
        )

        federation_id = (
            "cat_federation_"
            + uuid4().hex[:8]
        )

        federation = CatFederation(
            id=federation_id,
            name=(
                name
                if name is not None
                else federation_id
            ),
            founder_group=
                founder_group_id,
            groups=[
                founder_group_id
            ],
            history=[],
        )

        self.federations[
            federation_id
        ] = federation

        founder.federations.append(
            federation_id
        )

        return (
            CatFederationCreatedResult(
                federation_id=
                    federation_id,
                founder_group=
                    founder_group_id,
            )
        )

    def admit(
        self,
        federation_id,
        group_id,
    ):
        federation = (
            self._federation(
                federation_id
            )
        )

        group = (
            self.group_system._group(
                group_id
            )
        )

        if group_id in federation.groups:
            return (
                CatFederationAdmissionSkippedResult(
                    reason="already_member",
                )
            )

        relations = []

        for existing_group_id in (
            federation.groups
        ):
            relation = (
                self.diplomacy
                .mutual_relation(
                    existing_group_id,
                    group_id,
                )
            )

            relations.append(
                relation[
                    "mutual_score"
                ]
            )

        average = (
            sum(
                relations
            )
            / len(
                relations
            )
            if relations
            else 0.0
        )

        if average < 0.0:
            return (
                CatFederationAdmissionDeniedResult(
                    reason=
                        "negative_diplomacy",
                    score=average,
                )
            )

        federation.groups.append(
            group_id
        )

        group.federations.append(
            federation_id
        )

        event = (
            CatGroupJoinedFederationEvent(
                federation_id=
                    federation_id,
                group_id=
                    group_id,
            )
        )

        federation.history.append(
            event
        )

        return event

    def share_knowledge(
        self,
        federation_id,
        source_group_id,
        knowledge_id,
    ):
        federation = (
            self._federation(
                federation_id
            )
        )

        if (
            source_group_id
            not in federation.groups
        ):
            return (
                CatFederationKnowledgeDeniedResult(
                    reason="source_not_member",
                )
            )

        targets = []

        for group_id in federation.groups:
            if (
                group_id
                == source_group_id
            ):
                continue

            result = (
                self.knowledge
                .transmit_between_groups(
                    source_group_id,
                    group_id,
                    knowledge_id,
                    transmission=
                        "federation",
                )
            )

            if result.transmitted:
                targets.append(
                    group_id
                )

        return (
            CatFederationKnowledgeSharedResult(
                federation_id=
                    federation_id,
                source_group=
                    source_group_id,
                knowledge_id=
                    knowledge_id,
                targets=tuple(
                    targets
                ),
            )
        )

    def leave(
        self,
        federation_id,
        group_id,
    ):
        federation = (
            self._federation(
                federation_id
            )
        )

        group = (
            self.group_system._group(
                group_id
            )
        )

        if (
            group_id
            not in federation.groups
        ):
            return (
                CatFederationLeaveDeniedResult(
                    reason="not_member",
                )
            )

        federation.groups.remove(
            group_id
        )

        if (
            federation_id
            in group.federations
        ):
            group.federations.remove(
                federation_id
            )

        return (
            CatGroupLeftFederationResult(
                federation_id=
                    federation_id,
                group_id=
                    group_id,
            )
        )

    def _federation(
        self,
        federation_id,
    ):
        federation = (
            self.federations.get(
                federation_id
            )
        )

        if federation is None:
            raise KeyError(
                "Unknown federation: "
                f"{federation_id}"
            )

        return federation
