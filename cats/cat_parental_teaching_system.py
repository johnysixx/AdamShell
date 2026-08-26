from copy import deepcopy

from cats.cat import Cat
from cats.cat_family_system import (
    CatFamilySystem
)


class CatParentalTeachingSystem:

    ALLOWED_SKILLS = {
        "socialization",
        "litter_box",
        "box_travel",
        "cat_door_travel",
        "hunting",
        "adult_meowing"
    }

    def __init__(
        self,
        cats_layer=None
    ):
        self.cats_layer = cats_layer

        self.family_system = (
            CatFamilySystem(
                cats_layer
            )
        )

    def teach(
        self,
        parent,
        kitten,
        skill,
        progress=0.25,
        current_day=None
    ):
        self._require_cat(parent)
        self._require_cat(kitten)

        role = self._parent_role(
            parent,
            kitten
        )

        if role is None:
            return {
                "name": (
                    "parental_teaching_denied"
                ),
                "parent": parent.name,
                "kitten": kitten.name,
                "reason": "not_parent",
                "taught": False
            }

        if skill not in self.ALLOWED_SKILLS:
            return {
                "name": (
                    "parental_teaching_denied"
                ),
                "parent": parent.name,
                "kitten": kitten.name,
                "reason": "unsupported_skill",
                "skill": skill,
                "taught": False
            }

        progress = max(
            0.0,
            float(progress)
        )

        skills = kitten.learning.setdefault(
            "skills",
            {}
        )

        skill_state = skills.setdefault(
            skill,
            {
                "learned": False,
                "progress": 0.0,
                "teacher": None,
                "learned_on_day": None
            }
        )

        old_progress = float(
            skill_state.get(
                "progress",
                0.0
            )
        )

        new_progress = min(
            1.0,
            old_progress + progress
        )

        skill_state[
            "progress"
        ] = new_progress

        skill_state[
            "teacher"
        ] = parent.name

        learned_now = bool(
            not skill_state.get(
                "learned",
                False
            )
            and new_progress >= 1.0
        )

        if new_progress >= 1.0:
            skill_state[
                "learned"
            ] = True

            if (
                skill_state.get(
                    "learned_on_day"
                )
                is None
            ):
                skill_state[
                    "learned_on_day"
                ] = current_day

        if role == "mother":
            kitten.learning[
                "teacher_mother"
            ] = parent.name

        if (
            role == "father"
            and skill == "hunting"
        ):
            kitten.learning[
                "hunting_teacher_father"
            ] = parent.name

        family_knowledge = (
            kitten.learning.setdefault(
                "family_knowledge",
                {}
            )
        )

        family_knowledge[
            "parental_lessons"
        ] = int(
            family_knowledge.get(
                "parental_lessons",
                0
            )
        ) + 1

        self._record(
            parent,
            kitten,
            skill,
            role,
            current_day
        )

        self._strengthen_relationship(
            kitten,
            parent
        )

        event = {
            "name": "cat_parent_taught_kitten",
            "parent": parent.name,
            "parent_role": role,
            "kitten": kitten.name,
            "skill": skill,
            "progress_before": old_progress,
            "progress_after": new_progress,
            "learned": bool(
                skill_state[
                    "learned"
                ]
            ),
            "learned_now": learned_now,
            "day": current_day,
            "taught": True
        }

        parent.social_interactions.append(
            deepcopy(event)
        )

        kitten.social_interactions.append(
            deepcopy(event)
        )

        return event

    def _parent_role(
        self,
        parent,
        kitten
    ):
        parents = kitten.family[
            "parents"
        ]

        if (
            parents.get(
                "mother"
            )
            == parent.name
        ):
            return "mother"

        if (
            parents.get(
                "father"
            )
            == parent.name
        ):
            return "father"

        return None

    def _record(
        self,
        parent,
        kitten,
        skill,
        role,
        current_day
    ):
        state = kitten.parental_teaching

        state[
            "lessons_received"
        ] += 1

        state[
            "last_lesson"
        ] = skill

        state[
            "last_teacher"
        ] = parent.name

        teachers = state[
            "teachers"
        ]

        teachers[
            parent.name
        ] = int(
            teachers.get(
                parent.name,
                0
            )
        ) + 1

        skills = state[
            "skills"
        ]

        skills[
            skill
        ] = int(
            skills.get(
                skill,
                0
            )
        ) + 1

    def _strengthen_relationship(
        self,
        kitten,
        parent
    ):
        relation = (
            kitten.relationships.setdefault(
                parent.name,
                {}
            )
        )

        relation.setdefault(
            "familiarity",
            0.0
        )

        relation.setdefault(
            "trust",
            0.5
        )

        relation.setdefault(
            "affiliation",
            0.0
        )

        relation.setdefault(
            "tension",
            0.0
        )

        relation[
            "familiarity"
        ] = min(
            1.0,
            float(
                relation[
                    "familiarity"
                ]
            ) + 0.03
        )

        relation[
            "trust"
        ] = min(
            1.0,
            float(
                relation[
                    "trust"
                ]
            ) + 0.04
        )

        relation[
            "affiliation"
        ] = min(
            1.0,
            float(
                relation[
                    "affiliation"
                ]
            ) + 0.02
        )

        relation[
            "last_interaction"
        ] = "parental_teaching"

    def _require_cat(
        self,
        cat
    ):
        if not isinstance(cat, Cat):
            raise TypeError(
                "CatParentalTeachingSystem "
                "requires Cat."
            )
