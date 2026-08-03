class KittenUpbringingResolver:

    CARE_ONLY_LAST_DAY = 13
    EARLY_LEARNING_FIRST_DAY = 14
    EARLY_LEARNING_LAST_DAY = 20

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def tick_day(
        self,
        kitten,
        cats,
        current_day
    ):
        learning = kitten.get(
            "learning"
        )

        if not isinstance(
            learning,
            dict
        ):
            return self._skip(
                kitten=kitten,
                current_day=current_day,
                reason="learning_state_unavailable"
            )

        if not learning.get(
            "teaching_required",
            False
        ):
            return self._skip(
                kitten=kitten,
                current_day=current_day,
                reason="maternal_teaching_not_required"
            )

        age_days = int(
            kitten.get(
                "age_days",
                0
            )
        )

        if age_days > (
            self.EARLY_LEARNING_LAST_DAY
        ):
            return self._skip(
                kitten=kitten,
                current_day=current_day,
                reason="outside_early_upbringing_period"
            )

        upbringing = kitten.setdefault(
            "upbringing",
            self._create_upbringing_state()
        )

        mother = self._find_parent(
            kitten=kitten,
            cats=cats,
            parent_role="mother"
        )

        father = self._find_parent(
            kitten=kitten,
            cats=cats,
            parent_role="father"
        )

        events = []

        if age_days <= (
            self.CARE_ONLY_LAST_DAY
        ):
            events.extend(
                self._provide_daily_care(
                    kitten=kitten,
                    mother=mother,
                    age_days=age_days,
                    current_day=current_day
                )
            )

            father_event = (
                self._father_food_delivery(
                    kitten=kitten,
                    father=father,
                    age_days=age_days,
                    current_day=current_day
                )
            )

            if father_event is not None:
                events.append(
                    father_event
                )

            phase = "complete_maternal_care"

        else:
            events.extend(
                self._provide_reduced_care(
                    kitten=kitten,
                    mother=mother,
                    age_days=age_days,
                    current_day=current_day
                )
            )

            events.extend(
                self._run_early_lessons(
                    kitten=kitten,
                    mother=mother,
                    age_days=age_days,
                    current_day=current_day
                )
            )

            phase = "early_socialization"

        upbringing["phase"] = phase
        upbringing["last_processed_age"] = (
            age_days
        )
        upbringing["last_processed_day"] = (
            current_day
        )
        upbringing[
            "days_processed"
        ] += 1

        event = {
            "name": (
                "kitten_upbringing_day_completed"
            ),
            "kitten": kitten["name"],
            "age_days": age_days,
            "day": current_day,
            "phase": phase,
            "mother": (
                mother.get("name")
                if mother is not None
                else None
            ),
            "father": (
                father.get("name")
                if father is not None
                else None
            ),
            "events": events,
            "event_count": len(events),
            "processed": True
        }

        self._record(
            kitten,
            event
        )

        return event

    def _provide_daily_care(
        self,
        kitten,
        mother,
        age_days,
        current_day
    ):
        teacher_name = (
            mother.get("name")
            if mother is not None
            else kitten[
                "learning"
            ].get(
                "teacher_mother"
            )
        )

        care_names = (
            "fed_by_mother",
            "cleaned_by_mother",
            "warmed_by_mother",
            "protected_by_mother"
        )

        events = []

        for care_name in care_names:
            events.append({
                "name": care_name,
                "kitten": kitten["name"],
                "mother": teacher_name,
                "age_days": age_days,
                "day": current_day,
                "care": True
            })

        care = kitten[
            "upbringing"
        ][
            "care"
        ]

        care.update({
            "fed_today": True,
            "cleaned_today": True,
            "warmed_today": True,
            "protected_today": True,
            "mother_present": (
                mother is not None
            )
        })

        return events

    def _provide_reduced_care(
        self,
        kitten,
        mother,
        age_days,
        current_day
    ):
        events = self._provide_daily_care(
            kitten=kitten,
            mother=mother,
            age_days=age_days,
            current_day=current_day
        )

        kitten[
            "upbringing"
        ][
            "care"
        ][
            "left_alone_briefly"
        ] = True

        if age_days == 14:
            events.append({
                "name": (
                    "mother_left_kittens_"
                    "alone_briefly"
                ),
                "kitten": kitten["name"],
                "mother": (
                    mother.get("name")
                    if mother is not None
                    else None
                ),
                "age_days": age_days,
                "day": current_day,
                "first_time": True
            })

            events.append({
                "name": (
                    "mother_brought_small_"
                    "dead_cronenberg"
                ),
                "kitten": kitten["name"],
                "mother": (
                    mother.get("name")
                    if mother is not None
                    else None
                ),
                "age_days": age_days,
                "day": current_day,
                "prey_alive": False,
                "purpose": (
                    "food_and_prey_recognition"
                )
            })

            kitten[
                "upbringing"
            ][
                "cronenberg_experience"
            ][
                "dead_deliveries"
            ] += 1

        return events

    def _run_early_lessons(
        self,
        kitten,
        mother,
        age_days,
        current_day
    ):
        events = []

        if age_days >= 14:
            events.append(
                self._advance_skill(
                    kitten=kitten,
                    skill_name="socialization",
                    amount=1.0 / 7.0,
                    teacher=mother,
                    age_days=age_days,
                    current_day=current_day,
                    lesson_name=(
                        "kitten_socialization_lesson"
                    )
                )
            )

        if age_days == 16:
            events.append({
                "name": (
                    "kitten_played_with_siblings"
                ),
                "kitten": kitten["name"],
                "age_days": age_days,
                "day": current_day,
                "learned": (
                    "play_boundaries"
                )
            })

        if age_days == 18:
            events.append(
                self._complete_skill(
                    kitten=kitten,
                    skill_name="litter_box",
                    teacher=mother,
                    age_days=age_days,
                    current_day=current_day,
                    lesson_name=(
                        "mother_taught_litter_box"
                    )
                )
            )

        if age_days == 19:
            events.append(
                self._complete_skill(
                    kitten=kitten,
                    skill_name="box_travel",
                    teacher=mother,
                    age_days=age_days,
                    current_day=current_day,
                    lesson_name=(
                        "mother_taught_box_travel"
                    )
                )
            )

        if age_days == 20:
            events.append(
                self._complete_skill(
                    kitten=kitten,
                    skill_name="cat_door_travel",
                    teacher=mother,
                    age_days=age_days,
                    current_day=current_day,
                    lesson_name=(
                        "mother_taught_cat_door_travel"
                    )
                )
            )

        return events

    def _advance_skill(
        self,
        kitten,
        skill_name,
        amount,
        teacher,
        age_days,
        current_day,
        lesson_name
    ):
        skill = kitten[
            "learning"
        ][
            "skills"
        ][
            skill_name
        ]

        previous_progress = float(
            skill.get(
                "progress",
                0.0
            )
        )

        progress = min(
            1.0,
            previous_progress + amount
        )

        learned = progress >= 0.999999

        skill.update({
            "progress": progress,
            "learned": learned,
            "teacher": (
                teacher.get("name")
                if teacher is not None
                else kitten[
                    "learning"
                ].get(
                    "teacher_mother"
                )
            )
        })

        if learned:
            skill[
                "learned_on_day"
            ] = current_day

        lesson = {
            "name": lesson_name,
            "student": kitten["name"],
            "teacher": skill["teacher"],
            "skill": skill_name,
            "age_days": age_days,
            "day": current_day,
            "previous_progress": (
                previous_progress
            ),
            "progress": progress,
            "learned": learned
        }

        kitten[
            "learning"
        ][
            "lessons"
        ].append(
            lesson
        )

        return lesson

    def _complete_skill(
        self,
        kitten,
        skill_name,
        teacher,
        age_days,
        current_day,
        lesson_name
    ):
        skill = kitten[
            "learning"
        ][
            "skills"
        ][
            skill_name
        ]

        teacher_name = (
            teacher.get("name")
            if teacher is not None
            else kitten[
                "learning"
            ].get(
                "teacher_mother"
            )
        )

        skill.update({
            "learned": True,
            "progress": 1.0,
            "teacher": teacher_name,
            "learned_on_day": current_day
        })

        lesson = {
            "name": lesson_name,
            "student": kitten["name"],
            "teacher": teacher_name,
            "skill": skill_name,
            "age_days": age_days,
            "day": current_day,
            "progress": 1.0,
            "learned": True
        }

        kitten[
            "learning"
        ][
            "lessons"
        ].append(
            lesson
        )

        return lesson

    def _father_food_delivery(
        self,
        kitten,
        father,
        age_days,
        current_day
    ):
        if father is None:
            return None

        # Předvídatelné "občas":
        # každý pátý den věku kotěte.
        if age_days == 0 or age_days % 5 != 0:
            return None

        event = {
            "name": (
                "father_brought_dead_cronenberg"
            ),
            "kitten": kitten["name"],
            "father": father["name"],
            "age_days": age_days,
            "day": current_day,
            "prey_alive": False,
            "purpose": "family_food"
        }

        kitten[
            "upbringing"
        ][
            "cronenberg_experience"
        ][
            "father_food_deliveries"
        ] += 1

        return event

    def _find_parent(
        self,
        kitten,
        cats,
        parent_role
    ):
        parents = kitten.get(
            "parents",
            {}
        )

        parent_name = parents.get(
            parent_role
        )

        if (
            parent_name is None
            and parent_role == "mother"
        ):
            parent_name = kitten.get(
                "learning",
                {}
            ).get(
                "teacher_mother"
            )

        if parent_name is None:
            return None

        for cat in cats:
            if cat.get("name") == parent_name:
                return cat

        return None

    def _create_upbringing_state(self):
        return {
            "phase": "complete_maternal_care",
            "days_processed": 0,
            "last_processed_age": None,
            "last_processed_day": None,
            "care": {
                "fed_today": False,
                "cleaned_today": False,
                "warmed_today": False,
                "protected_today": False,
                "mother_present": False,
                "left_alone_briefly": False
            },
            "cronenberg_experience": {
                "dead_deliveries": 0,
                "father_food_deliveries": 0,
                "live_deliveries": 0,
                "successful_kills": 0,
                "family_hunts": 0
            },
            "history": []
        }

    def _skip(
        self,
        kitten,
        current_day,
        reason
    ):
        event = {
            "name": (
                "kitten_upbringing_day_skipped"
            ),
            "kitten": kitten.get("name"),
            "day": current_day,
            "reason": reason,
            "processed": False
        }

        self.history.append(
            event
        )

        return event

    def _record(
        self,
        kitten,
        event
    ):
        self.history.append(
            event
        )

        kitten[
            "upbringing"
        ][
            "history"
        ].append(
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