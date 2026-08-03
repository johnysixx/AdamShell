class MeowKnowledgeResolver:

    REQUIRED_EXPERIENCES = (
        "socialization",
        "litter_box",
        "box_travel",
        "cat_door_travel",
        "hunting",
        "adult_meowing",
        "human_communication"
    )

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def can_receive_meow(
        self,
        kitten,
        mother
    ):
        kitten_learning = kitten.get(
            "learning",
            {}
        )

        mother_learning = mother.get(
            "learning",
            {}
        )

        kitten_meow = kitten_learning.get(
            "meow_knowledge",
            {}
        )

        mother_meow = mother_learning.get(
            "meow_knowledge",
            {}
        )

        if kitten.get("type") != "cat":
            return {
                "allowed": False,
                "reason": "receiver_is_not_cat"
            }

        if mother.get("type") != "cat":
            return {
                "allowed": False,
                "reason": "teacher_is_not_cat"
            }

        if kitten_meow.get(
            "learned",
            False
        ):
            return {
                "allowed": False,
                "reason": "meow_already_known"
            }

        if not mother_meow.get(
            "learned",
            False
        ):
            return {
                "allowed": False,
                "reason": "mother_does_not_know_meow"
            }

        if not mother_meow.get(
            "can_speak",
            False
        ):
            return {
                "allowed": False,
                "reason": "mother_cannot_speak_meow"
            }

        skills = kitten_learning.get(
            "skills",
            {}
        )

        missing_experiences = [
            skill_name
            for skill_name
            in self.REQUIRED_EXPERIENCES
            if not skills.get(
                skill_name,
                {}
            ).get(
                "learned",
                False
            )
        ]

        if missing_experiences:
            return {
                "allowed": False,
                "reason": (
                    "required_experiences_missing"
                ),
                "missing_experiences": (
                    missing_experiences
                )
            }

        return {
            "allowed": True,
            "reason": "ready_for_meow",
            "missing_experiences": []
        }

    def transmit(
        self,
        mother,
        kitten,
        current_day
    ):
        readiness = self.can_receive_meow(
            kitten,
            mother
        )

        if not readiness["allowed"]:
            event = {
                "name": (
                    "meow_knowledge_transmission_denied"
                ),
                "mother": mother.get("name"),
                "kitten": kitten.get("name"),
                "day": current_day,
                "reason": readiness["reason"],
                "missing_experiences": (
                    readiness.get(
                        "missing_experiences",
                        []
                    )
                ),
                "transmitted": False
            }

            self.history.append(
                event
            )

            return event

        learning = kitten["learning"]

        meow = learning[
            "meow_knowledge"
        ]

        meow.update({
            "learned": True,
            "understood": True,
            "can_speak": True,
            "teacher": mother["name"],
            "source": "maternal_transmission",
            "learned_on_day": current_day
        })

        learning["lessons"].append({
            "name": "mother_spoke_meow",
            "teacher": mother["name"],
            "student": kitten["name"],
            "day": current_day,
            "knowledge": list(
                meow["contains"]
            )
        })

        learning["complete"] = all(
            skill.get(
                "learned",
                False
            )
            for skill
            in learning["skills"].values()
        )

        if learning["complete"]:
            learning[
                "teaching_required"
            ] = False

        event = {
            "name": (
                "meow_knowledge_transmitted"
            ),
            "mother": mother["name"],
            "kitten": kitten["name"],
            "day": current_day,
            "knowledge": list(
                meow["contains"]
            ),
            "adult_meowing_learned": (
                learning[
                    "adult_meowing_learned"
                ]
            ),
            "human_communication_learned": (
                learning[
                    "human_communication_learned"
                ]
            ),
            "learning_complete": (
                learning["complete"]
            ),
            "transmitted": True
        }

        self.history.append(
            event
        )

        quantum_events = getattr(
            self.universe,
            "quantum_events",
            None
        )

        if quantum_events is not None:
            quantum_events.append(
                event
            )

        return event

    def _complete_skill(
        self,
        kitten,
        skill_name,
        teacher_name,
        current_day
    ):
        skill = kitten[
            "learning"
        ][
            "skills"
        ][
            skill_name
        ]

        skill.update({
            "learned": True,
            "progress": 1.0,
            "teacher": teacher_name,
            "learned_on_day": current_day
        })