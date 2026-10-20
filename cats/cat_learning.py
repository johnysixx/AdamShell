from cats.cat_adult_vocalization_state import (
    CatAdultVocalizationState,
)
from cats.cat_learning_state import (
    CatLearningState,
    CatMeowKnowledgeState,
    CatSkillRegistry,
    CatSkillState,
)


class CatLearning:

    MATERNAL_TEACHING_DAYS = 90

    ADULT_VOCALIZATIONS = (
        "food_request",
        "door_request",
        "attention_request",
        "greeting",
        "warning",
        "follow_me",
        "distress_call",
        "human_summoning"
    )

    MEOW_CONTENTS = (
        "cat_identity",
        "cat_social_rules",
        "bar_knowledge",
        "box_knowledge",
        "cat_door_knowledge",
        "litter_box_knowledge",
        "navigation",
        "cronenberg_hunting",
        "family_knowledge",
        "human_communication"
    )

    SKILLS = (
        "socialization",
        "litter_box",
        "box_travel",
        "cat_door_travel",
        "hunting",
        "adult_meowing",
        "human_communication"
    )

    @classmethod
    def _skill_registry(
        cls,
        learned,
    ):
        registry = (
            CatSkillRegistry()
        )

        for skill_name in cls.SKILLS:
            registry.store(
                CatSkillState(
                    name=skill_name,
                    learned=bool(
                        learned
                    ),
                    progress=(
                        1.0
                        if learned
                        else 0.0
                    ),
                    teacher=None,
                    learned_on_day=None,
                    vocalizations=(
                        CatAdultVocalizationState.create(
                            learned=bool(
                                learned
                            )
                        )
                        if (
                            skill_name
                            == "adult_meowing"
                        )
                        else None
                    ),
                )
            )

        return registry

    @classmethod
    def create_complete_state(
        cls
    ):
        """
        Vychozi stav manifestovane kocky.

        Kocky vznikle kostkami, rucni manifestaci
        nebo jinym nebiologickym zpusobem uz vedi,
        jak se chovat jako kocky.
        """
        return CatLearningState(
            teaching_required=False,
            teaching_deadline_days=None,
            teacher_mother=None,
            hunting_teacher_father=None,
            kitten_meowing_instinctive=True,
            adult_meowing_learned=True,
            human_communication_learned=True,
            meow_knowledge=CatMeowKnowledgeState(
                learned=True,
                understood=True,
                can_speak=True,
                teacher=None,
                source="manifestation",
                learned_on_day=None,
                contains=list(cls.MEOW_CONTENTS),
            ),
            skills=cls._skill_registry(
                learned=True
            ),
            lessons=[],
            complete=True,
        )

    @classmethod
    def create_newborn_state(
        cls,
        mother_name=None
    ):
        """
        Narozene kote prirozene mnouka,
        ale ostatni chovani se musi naucit.
        """
        return CatLearningState(
            teaching_required=True,
            teaching_deadline_days=(
                cls.MATERNAL_TEACHING_DAYS
            ),
            teacher_mother=mother_name,
            hunting_teacher_father=None,
            kitten_meowing_instinctive=True,
            adult_meowing_learned=False,
            human_communication_learned=False,
            meow_knowledge=CatMeowKnowledgeState(
                learned=False,
                understood=False,
                can_speak=False,
                teacher=None,
                source=None,
                learned_on_day=None,
                contains=list(cls.MEOW_CONTENTS),
            ),
            skills=cls._skill_registry(
                learned=False
            ),
            lessons=[],
            complete=False,
        )
