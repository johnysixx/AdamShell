from copy import deepcopy

from cats.cat_group_hierarchy_system import (
    CatGroupHierarchySystem,
)
from cats.cat_group_recruitment_state import (
    CatGroupRecruitmentCompletedResult,
    CatGroupRecruitmentFailedResult,
    CatGroupRecruitmentVote,
    CatGroupRecruitmentVoteEvent,
)
from cats.cat_social_objects import (
    CatRelationship,
)


class CatGroupRecruitmentSystem:

    def __init__(
        self,
        group_system,
    ):
        self.group_system = group_system

        self.hierarchy = (
            CatGroupHierarchySystem(
                group_system
            )
        )

    def vote(
        self,
        group_id,
        candidate,
        cats,
        sponsor=None,
    ):
        group = self.group_system._group(
            group_id
        )

        members = (
            self.group_system
            ._member_objects(
                group,
                cats,
            )
        )

        ranking_result = (
            self.hierarchy.rank(
                group_id,
                cats,
            )
        )

        ranking = {
            item.cat:
                item.influence
            for item
            in ranking_result.ranking
        }

        votes = []
        weighted_yes = 0.0
        weighted_no = 0.0
        vetoes = []

        for member in members:
            relation = (
                member.relationships.get(
                    candidate.name,
                    CatRelationship.create(),
                )
            )

            trust = float(
                relation.trust
            )

            affiliation = float(
                relation.affiliation
            )

            familiarity = float(
                relation.familiarity
            )

            tension = float(
                relation.tension
            )

            shared_scent = float(
                relation.shared_scent
            )

            score = (
                trust * 0.4
                + affiliation * 0.25
                + familiarity * 0.15
                + shared_scent * 0.1
                + 0.2
                - tension * 0.55
            )

            if (
                sponsor is not None
                and sponsor.name
                == member.name
            ):
                score += 0.15

            vote_yes = (
                score >= 0.35
            )

            influence = max(
                0.1,
                ranking.get(
                    member.name,
                    0.1,
                ),
            )

            if (
                tension >= 0.9
                and trust <= 0.1
            ):
                vetoes.append(
                    member.name
                )

                member.group.recruitment_vetoes += 1

            if vote_yes:
                weighted_yes += (
                    influence
                )

                member.group.recruitment_support += 1
            else:
                weighted_no += (
                    influence
                )

            votes.append(
                CatGroupRecruitmentVote(
                    member=member.name,
                    yes=vote_yes,
                    score=round(
                        score,
                        4,
                    ),
                    weight=round(
                        influence,
                        4,
                    ),
                )
            )

        accepted = bool(
            not vetoes
            and weighted_yes
            > weighted_no
        )

        event = (
            CatGroupRecruitmentVoteEvent(
                group_id=group_id,
                candidate=candidate.name,
                sponsor=(
                    sponsor.name
                    if sponsor is not None
                    else None
                ),
                votes=tuple(
                    votes
                ),
                weighted_yes=round(
                    weighted_yes,
                    4,
                ),
                weighted_no=round(
                    weighted_no,
                    4,
                ),
                vetoes=tuple(
                    vetoes
                ),
                accepted=accepted,
            )
        )

        group.history.append(
            deepcopy(
                event
            )
        )

        return event

    def recruit(
        self,
        group_id,
        candidate,
        cats,
        sponsor=None,
    ):
        vote = self.vote(
            group_id=group_id,
            candidate=candidate,
            cats=cats,
            sponsor=sponsor,
        )

        if not vote.accepted:
            return (
                CatGroupRecruitmentFailedResult(
                    group_id=group_id,
                    candidate=(
                        candidate.name
                    ),
                    vote=vote,
                )
            )

        result = (
            self.group_system
            .add_member(
                group_id,
                candidate,
                cats,
            )
        )

        return (
            CatGroupRecruitmentCompletedResult(
                group_id=group_id,
                candidate=(
                    candidate.name
                ),
                vote=vote,
                join_result=result,
                joined=bool(
                    result.joined
                ),
            )
        )
