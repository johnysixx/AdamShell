class CatLearning:

    MATERNAL_TEACHING_DAYS = 90

    SKILLS = (
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
            "skills": {
                skill: {
                    "learned": True,
                    "progress": 1.0,
                    "teacher": None,
                    "learned_on_day": None
                }
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
            "skills": {
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
                    "learned_on_day": None
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