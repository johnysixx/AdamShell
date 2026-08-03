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
    def create_complete_state(
        cls
    ):
        """
        Výchozí stav manifestované kočky.

        Kočky vzniklé kostkami, ruční manifestací
        nebo jiným nebiologickým způsobem už vědí,
        jak se chovat jako kočky.
        """
        return {
            "teaching_required": False,
            "teaching_deadline_days": None,
            "teacher_mother": None,
            "hunting_teacher_father": None,
            "kitten_meowing_instinctive": True,
            "adult_meowing_learned": True,
            "human_communication_learned": True,
            "meow_knowledge": {
                "learned": True,
                "understood": True,
                "can_speak": True,
                "teacher": None,
                "source": "manifestation",
                "learned_on_day": None,
                "contains": list(
                    cls.MEOW_CONTENTS
                )
            },
            "skills": {
                skill: (
                    {
                        "learned": True,
                        "progress": 1.0,
                        "teacher": None,
                        "learned_on_day": None,
                        "vocalizations": {
                            vocalization: True
                            for vocalization
                            in cls.ADULT_VOCALIZATIONS
                        }
                    }
                    if skill == "adult_meowing"
                    else {
                        "learned": True,
                        "progress": 1.0,
                        "teacher": None,
                        "learned_on_day": None
                    }
                )
                for skill in cls.SKILLS
            },
            "lessons": [],
            "complete": True
        }

    @classmethod
    def create_newborn_state(
        cls,
        mother_name=None
    ):
        """
        Narozené kotě přirozeně mňouká,
        ale ostatní chování se musí naučit.
        """
        return {
            "teaching_required": True,
            "teaching_deadline_days": (
                cls.MATERNAL_TEACHING_DAYS
            ),
            "teacher_mother": mother_name,
            "hunting_teacher_father": None,
            "kitten_meowing_instinctive": True,
            "adult_meowing_learned": False,
            "human_communication_learned": False,
            "meow_knowledge": {
                "learned": False,
                "understood": False,
                "can_speak": False,
                "teacher": None,
                "source": None,
                "learned_on_day": None,
                "contains": list(
                    cls.MEOW_CONTENTS
                )
            },
            "skills": {
                "socialization": {
                    "learned": False,
                    "progress": 0.0,
                    "teacher": None,
                    "learned_on_day": None
                },
                "litter_box": {
                    "learned": False,
                    "progress": 0.0,
                    "teacher": None,
                    "learned_on_day": None
                },
                "box_travel": {
                    "learned": False,
                    "progress": 0.0,
                    "teacher": None,
                    "learned_on_day": None
                },
                "cat_door_travel": {
                    "learned": False,
                    "progress": 0.0,
                    "teacher": None,
                    "learned_on_day": None
                },
                "hunting": {
                    "learned": False,
                    "progress": 0.0,
                    "teacher": None,
                    "learned_on_day": None
                },
                "adult_meowing": {
                    "learned": False,
                    "progress": 0.0,
                    "teacher": None,
                    "learned_on_day": None,
                    "vocalizations": {
                        vocalization: False
                        for vocalization
                        in cls.ADULT_VOCALIZATIONS
                    }
                },
                "human_communication": {
                    "learned": False,
                    "progress": 0.0,
                    "teacher": None,
                    "learned_on_day": None
                }
            },
            "lessons": [],
            "complete": False
        }