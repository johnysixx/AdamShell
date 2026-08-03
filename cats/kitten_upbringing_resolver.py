from cats.adult_vocalization_resolver import (
    AdultVocalizationResolver
)
from cats.meow_knowledge_resolver import (
    MeowKnowledgeResolver
)
from cats.cat_learning import CatLearning
from cats.feline_wisdom import FelineWisdom


class KittenUpbringingResolver:

    CARE_ONLY_LAST_DAY = 13
    EARLY_LEARNING_FIRST_DAY = 14
    EARLY_LEARNING_LAST_DAY = 20

    LIVE_PREY_FIRST_DAY = 21
    LIVE_PREY_PRACTICE_LAST_DAY = 34
    FIRST_TRAINING_KILL_DAY = 35
    FAMILY_HUNT_FIRST_DAY = 36
    UPBRINGING_LAST_DAY = 90

    REQUIRED_FAMILY_HUNTS = 3

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

        self.vocalization_resolver = (
            AdultVocalizationResolver(
                universe
            )
        )

        self.meow_resolver = (
            MeowKnowledgeResolver(
                universe
            )
        )

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
            self.UPBRINGING_LAST_DAY
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

        elif age_days <= (
            self.EARLY_LEARNING_LAST_DAY
        ):
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

        else:
            events.extend(
                self._run_hunting_upbringing(
                    kitten=kitten,
                    mother=mother,
                    father=father,
                    age_days=age_days,
                    current_day=current_day
                )
            )

            events.extend(
                self._run_late_education(
                    kitten=kitten,
                    mother=mother,
                    cats=cats,
                    age_days=age_days,
                    current_day=current_day
                )
            )

            if age_days <= (
                self.LIVE_PREY_PRACTICE_LAST_DAY
            ):
                phase = "live_prey_training"

            elif age_days == (
                self.FIRST_TRAINING_KILL_DAY
            ):
                phase = "first_training_kill"

            else:
                phase = "family_hunting"

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

    def _run_hunting_upbringing(
        self,
        kitten,
        mother,
        father,
        age_days,
        current_day
    ):
        events = []

        if age_days == (
            self.LIVE_PREY_FIRST_DAY
        ):
            events.append(
                self._bring_live_cronenberg(
                    kitten=kitten,
                    mother=mother,
                    age_days=age_days,
                    current_day=current_day
                )
            )

        if (
            self.LIVE_PREY_FIRST_DAY
            <= age_days
            <= 27
        ):
            events.append(
                self._practice_hunting_step(
                    kitten=kitten,
                    teacher=mother,
                    skill_step="tracking_and_chasing",
                    progress_amount=0.04,
                    age_days=age_days,
                    current_day=current_day
                )
            )

        elif 28 <= age_days <= (
            self.LIVE_PREY_PRACTICE_LAST_DAY
        ):
            events.append(
                self._practice_hunting_step(
                    kitten=kitten,
                    teacher=mother,
                    skill_step=(
                        "capture_and_killing_bite"
                    ),
                    progress_amount=0.05,
                    age_days=age_days,
                    current_day=current_day
                )
            )

        elif age_days == (
            self.FIRST_TRAINING_KILL_DAY
        ):
            events.append(
                self._first_training_kill(
                    kitten=kitten,
                    mother=mother,
                    age_days=age_days,
                    current_day=current_day
                )
            )

        elif age_days >= (
            self.FAMILY_HUNT_FIRST_DAY
        ):
            events.append(
                self._family_hunt(
                    kitten=kitten,
                    mother=mother,
                    father=father,
                    age_days=age_days,
                    current_day=current_day
                )
            )

        return events

    def _bring_live_cronenberg(
        self,
        kitten,
        mother,
        age_days,
        current_day
    ):
        experience = kitten[
            "upbringing"
        ][
            "cronenberg_experience"
        ]

        experience[
            "live_deliveries"
        ] += 1

        event = {
            "name": (
                "mother_brought_small_"
                "live_cronenberg"
            ),
            "kitten": kitten["name"],
            "mother": (
                mother.get("name")
                if mother is not None
                else None
            ),
            "age_days": age_days,
            "day": current_day,
            "prey_alive": True,
            "prey_controlled_by_mother": True,
            "purpose": "live_prey_training"
        }

        kitten[
            "learning"
        ][
            "lessons"
        ].append(
            event
        )

        return event

    def _practice_hunting_step(
        self,
        kitten,
        teacher,
        skill_step,
        progress_amount,
        age_days,
        current_day
    ):
        hunting = kitten[
            "learning"
        ][
            "skills"
        ][
            "hunting"
        ]

        previous_progress = float(
            hunting.get(
                "progress",
                0.0
            )
        )

        progress = min(
            0.8,
            previous_progress
            + progress_amount
        )

        teacher_name = (
            teacher.get("name")
            if teacher is not None
            else kitten[
                "learning"
            ].get(
                "teacher_mother"
            )
        )

        hunting.update({
            "progress": progress,
            "teacher": teacher_name
        })

        event = {
            "name": (
                "kitten_hunting_step_practiced"
            ),
            "kitten": kitten["name"],
            "teacher": teacher_name,
            "step": skill_step,
            "age_days": age_days,
            "day": current_day,
            "previous_progress": (
                previous_progress
            ),
            "progress": progress,
            "learned": False
        }

        kitten[
            "learning"
        ][
            "lessons"
        ].append(
            event
        )

        return event

    def _first_training_kill(
        self,
        kitten,
        mother,
        age_days,
        current_day
    ):
        experience = kitten[
            "upbringing"
        ][
            "cronenberg_experience"
        ]

        experience[
            "successful_kills"
        ] += 1

        hunting = kitten[
            "learning"
        ][
            "skills"
        ][
            "hunting"
        ]

        previous_progress = float(
            hunting.get(
                "progress",
                0.0
            )
        )

        hunting["progress"] = max(
            previous_progress,
            0.85
        )

        event = {
            "name": (
                "kitten_completed_first_"
                "training_kill"
            ),
            "kitten": kitten["name"],
            "mother": (
                mother.get("name")
                if mother is not None
                else None
            ),
            "age_days": age_days,
            "day": current_day,
            "prey": "small_live_cronenberg",
            "successful": True,
            "successful_kills": experience[
                "successful_kills"
            ],
            "hunting_progress": hunting[
                "progress"
            ]
        }

        kitten[
            "learning"
        ][
            "lessons"
        ].append(
            event
        )

        return event

    def _family_hunt(
        self,
        kitten,
        mother,
        father,
        age_days,
        current_day
    ):
        experience = kitten[
            "upbringing"
        ][
            "cronenberg_experience"
        ]

        experience[
            "family_hunts"
        ] += 1

        family_hunt_number = experience[
            "family_hunts"
        ]

        # Otec se přidá občas:
        # při každé druhé rodinné výpravě.
        father_joined = (
            father is not None
            and family_hunt_number % 2 == 0
        )

        hunting = kitten[
            "learning"
        ][
            "skills"
        ][
            "hunting"
        ]

        previous_progress = float(
            hunting.get(
                "progress",
                0.0
            )
        )

        progress = min(
            1.0,
            previous_progress + 0.05
        )

        enough_experience = (
            experience[
                "successful_kills"
            ] >= 1
            and family_hunt_number
            >= self.REQUIRED_FAMILY_HUNTS
        )

        learned = (
            enough_experience
            and progress >= 0.999999
        )

        teacher_names = []

        if mother is not None:
            teacher_names.append(
                mother["name"]
            )

        if father_joined:
            teacher_names.append(
                father["name"]
            )

            kitten[
                "learning"
            ][
                "hunting_teacher_father"
            ] = father["name"]

        hunting.update({
            "progress": progress,
            "learned": learned,
            "teacher": (
                teacher_names[0]
                if teacher_names
                else None
            )
        })

        if learned:
            hunting[
                "learned_on_day"
            ] = current_day

        event = {
            "name": (
                "kitten_joined_family_"
                "cronenberg_hunt"
            ),
            "kitten": kitten["name"],
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
            "father_joined": father_joined,
            "teachers": teacher_names,
            "age_days": age_days,
            "day": current_day,
            "family_hunt_number": (
                family_hunt_number
            ),
            "hunting_progress": progress,
            "hunting_learned": learned,
            "successful": True
        }

        kitten[
            "learning"
        ][
            "lessons"
        ].append(
            event
        )

        return event

    def _run_late_education(
        self,
        kitten,
        mother,
        cats,
        age_days,
        current_day
    ):
        events = []

        teacher = self._find_late_teacher(
            kitten=kitten,
            mother=mother,
            cats=cats
        )

        # Osm běžných dospělých hlasů:
        # jeden každý den od 60. do 67. dne.
        vocalization_index = age_days - 60

        if (
            0 <= vocalization_index
            < len(
                CatLearning.ADULT_VOCALIZATIONS
            )
        ):
            if teacher is None:
                events.append({
                    "name": (
                        "adult_vocalization_teacher_"
                        "unavailable"
                    ),
                    "kitten": kitten["name"],
                    "age_days": age_days,
                    "day": current_day,
                    "learned": False
                })

            else:
                vocalization = (
                    CatLearning
                    .ADULT_VOCALIZATIONS[
                        vocalization_index
                    ]
                )

                events.append(
                    self.vocalization_resolver.teach(
                        teacher=teacher,
                        kitten=kitten,
                        vocalization=vocalization,
                        current_day=current_day
                    )
                )

        # Praktické používání naučených zvuků
        # vůči lidem je samostatná dovednost.
        if age_days == 75:
            events.append(
                self._teach_human_communication(
                    kitten=kitten,
                    teacher=teacher,
                    age_days=age_days,
                    current_day=current_day
                )
            )

        # MEOW je závěrečná lekce.
        if age_days == 90:
            if teacher is None:
                events.append({
                    "name": (
                        "meow_teacher_unavailable"
                    ),
                    "kitten": kitten["name"],
                    "age_days": age_days,
                    "day": current_day,
                    "transmitted": False
                })

            else:
                events.append(
                    self.meow_resolver.transmit(
                        mother=teacher,
                        kitten=kitten,
                        current_day=current_day
                    )
                )

        return events

    def _teach_human_communication(
        self,
        kitten,
        teacher,
        age_days,
        current_day
    ):
        learning = kitten[
            "learning"
        ]

        adult_meowing = learning[
            "skills"
        ][
            "adult_meowing"
        ]

        if not adult_meowing.get(
            "learned",
            False
        ):
            return {
                "name": (
                    "human_communication_lesson_denied"
                ),
                "kitten": kitten["name"],
                "teacher": (
                    teacher.get("name")
                    if teacher is not None
                    else None
                ),
                "age_days": age_days,
                "day": current_day,
                "reason": (
                    "adult_vocalization_repertoire_"
                    "incomplete"
                ),
                "learned": False
            }

        if teacher is None:
            return {
                "name": (
                    "human_communication_lesson_denied"
                ),
                "kitten": kitten["name"],
                "teacher": None,
                "age_days": age_days,
                "day": current_day,
                "reason": "teacher_unavailable",
                "learned": False
            }

        skill = learning[
            "skills"
        ][
            "human_communication"
        ]

        skill.update({
            "learned": True,
            "progress": 1.0,
            "teacher": teacher["name"],
            "learned_on_day": current_day
        })

        learning[
            "human_communication_learned"
        ] = True

        lesson = {
            "name": (
                "human_feline_communication_learned"
            ),
            "kitten": kitten["name"],
            "teacher": teacher["name"],
            "age_days": age_days,
            "day": current_day,
            "uses": list(
                CatLearning.ADULT_VOCALIZATIONS
            ),
            "learned": True
        }

        learning[
            "lessons"
        ].append(
            lesson
        )

        return lesson

    def _find_late_teacher(
        self,
        kitten,
        mother,
        cats
    ):
        # Biologická matka má vždy přednost.
        if self._is_qualified_late_teacher(
            mother,
            parental_exception=True
        ):
            return mother

        # Potom určená náhradní kočka.
        substitute_name = kitten.get(
            "learning",
            {}
        ).get(
            "teacher_mother"
        )

        if substitute_name:
            substitute = next(
                (
                    candidate
                    for candidate in cats
                    if candidate.get("name")
                    == substitute_name
                ),
                None
            )

            if self._is_qualified_late_teacher(
                substitute
            ):
                return substitute

        # Nakonec jiná kvalifikovaná kočka.
        for candidate in cats:
            if candidate is kitten:
                continue

            if candidate is mother:
                continue

            if self._is_qualified_late_teacher(
                candidate
            ):
                return candidate

        return None

    def _is_qualified_late_teacher(
        self,
        candidate,
        parental_exception=False
    ):
        if candidate is None:
            return False

        if not self._knows_meow(
            candidate
        ):
            return False

        if parental_exception:
            return True

        wisdom = FelineWisdom.ensure_state(
            candidate
        )

        teaching = wisdom[
            "abilities"
        ].get(
            "teach_other_cats"
        )

        return bool(
            teaching
            and teaching.get(
                "learned",
                False
            )
        )

    def _knows_meow(
        self,
        cat
    ):
        meow = cat.get(
            "learning",
            {}
        ).get(
            "meow_knowledge",
            {}
        )

        return bool(
            meow.get(
                "learned",
                False
            )
            and meow.get(
                "can_speak",
                False
            )
        )

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