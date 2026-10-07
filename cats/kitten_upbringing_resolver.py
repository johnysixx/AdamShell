from dataclasses import replace

from cats.kitten_upbringing_state import (
    KittenCareState,
    KittenCronenbergExperienceState,
    KittenUpbringingState,
)
from cats.kitten_upbringing_phase import (
    KittenUpbringingPhase,
)
from cats.cat_maternal_care_system import CatMaternalCareSystem
from cats.adult_vocalization_resolver import AdultVocalizationResolver
from cats.meow_knowledge_resolver import MeowKnowledgeResolver
from cats.cat_learning import CatLearning
from cats.cat_learning_state import CatLearningState
from cats.feline_wisdom import FelineWisdom
from cats.cat_personality import CatPersonality
from cats.kitten_growth import KittenGrowth
from cats.cat_parentage_state import (
    CatParentageState
)
from cats.kitten_upbringing_result_state import (
    KittenAdultVocalizationTeacherUnavailableEvent,
    KittenDailyCareEvent,
    KittenDeadCronenbergDeliveredEvent,
    KittenFamilyHuntEvent,
    KittenFatherFoodDeliveryEvent,
    KittenFirstTrainingKillEvent,
    KittenHumanCommunicationLearnedEvent,
    KittenHumanCommunicationLessonDeniedResult,
    KittenHuntingStepPracticedEvent,
    KittenLiveCronenbergDeliveredEvent,
    KittenMeowTeacherUnavailableEvent,
    KittenMotherLeftBrieflyEvent,
    KittenSiblingPlayLessonEvent,
    KittenSkillCompletedLessonEvent,
    KittenSocializationLessonEvent,
    KittenUpbringingDayCompletedEvent,
    KittenUpbringingDaySkippedResult,
)

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

    def __init__(self, universe):
        self.universe = universe
        self.history = []
        self.vocalization_resolver = AdultVocalizationResolver(universe)
        self.meow_resolver = MeowKnowledgeResolver(universe)
        self.growth = KittenGrowth(universe)

    def tick_day(
        self,
        kitten,
        cats,
        current_day,
    ):
        learning = getattr(
            kitten,
            "learning",
            None,
        )

        if not isinstance(
            learning,
            CatLearningState,
        ):
            return self._skip(
                kitten=kitten,
                current_day=current_day,
                reason="learning_state_unavailable",
            )

        if not learning.teaching_required:
            return self._skip(
                kitten=kitten,
                current_day=current_day,
                reason="maternal_teaching_not_required",
            )

        age_days = int(
            getattr(
                kitten,
                "age_days",
                0,
            )
        )

        if age_days > self.UPBRINGING_LAST_DAY:
            return self._skip(
                kitten=kitten,
                current_day=current_day,
                reason="outside_early_upbringing_period",
            )

        upbringing = (
            self._ensure_upbringing_state(
                kitten
            )
        )

        mother = self._find_parent(
            kitten=kitten,
            cats=cats,
            parent_role="mother",
        )

        father = self._find_parent(
            kitten=kitten,
            cats=cats,
            parent_role="father",
        )

        events = []

        if age_days <= self.CARE_ONLY_LAST_DAY:
            events.extend(
                self._provide_daily_care(
                    kitten=kitten,
                    mother=mother,
                    age_days=age_days,
                    current_day=current_day,
                )
            )

            father_event = (
                self._father_food_delivery(
                    kitten=kitten,
                    father=father,
                    age_days=age_days,
                    current_day=current_day,
                )
            )

            if father_event is not None:
                events.append(
                    father_event
                )

            phase = (
                KittenUpbringingPhase
                .COMPLETE_MATERNAL_CARE
            )

        elif age_days <= self.EARLY_LEARNING_LAST_DAY:
            events.extend(
                self._provide_reduced_care(
                    kitten=kitten,
                    mother=mother,
                    age_days=age_days,
                    current_day=current_day,
                )
            )

            events.extend(
                self._run_early_lessons(
                    kitten=kitten,
                    mother=mother,
                    age_days=age_days,
                    current_day=current_day,
                )
            )

            phase = (
                KittenUpbringingPhase
                .EARLY_SOCIALIZATION
            )

        else:
            events.extend(
                self._run_hunting_upbringing(
                    kitten=kitten,
                    mother=mother,
                    father=father,
                    age_days=age_days,
                    current_day=current_day,
                )
            )

            events.extend(
                self._run_late_education(
                    kitten=kitten,
                    mother=mother,
                    cats=cats,
                    age_days=age_days,
                    current_day=current_day,
                )
            )

            if age_days <= self.LIVE_PREY_PRACTICE_LAST_DAY:
                phase = (
                    KittenUpbringingPhase
                    .LIVE_PREY_TRAINING
                )

            elif age_days == self.FIRST_TRAINING_KILL_DAY:
                phase = (
                    KittenUpbringingPhase
                    .FIRST_TRAINING_KILL
                )

            else:
                phase = (
                    KittenUpbringingPhase
                    .FAMILY_HUNTING
                )

        upbringing.phase = phase
        upbringing.last_processed_age = age_days
        upbringing.last_processed_day = current_day
        upbringing.days_processed += 1

        event = (
            KittenUpbringingDayCompletedEvent(
                kitten=kitten.name,
                age_days=age_days,
                day=current_day,
                phase=phase,
                mother=(
                    mother.name
                    if mother is not None
                    else None
                ),
                father=(
                    father.name
                    if father is not None
                    else None
                ),
                events=tuple(events),
            )
        )

        self._record(
            kitten,
            event,
        )

        return event

    def _provide_daily_care(
        self,
        kitten,
        mother,
        age_days,
        current_day,
    ):
        teacher_name = (
            mother.name
            if mother is not None
            else kitten.learning.teacher_mother
        )

        care_names = (
            "fed_by_mother",
            "cleaned_by_mother",
            "warmed_by_mother",
            "protected_by_mother",
        )

        events = []

        if mother is not None:
            events.append(
                self.growth.feed_cat_milk(
                    kitten=kitten,
                    day=current_day,
                    amount=1.0,
                    source=mother.name,
                )
            )

        for care_name in care_names:
            events.append(
                KittenDailyCareEvent(
                    name=care_name,
                    kitten=kitten.name,
                    mother=teacher_name,
                    age_days=age_days,
                    day=current_day,
                )
            )

        care = kitten.upbringing.care

        care.fed_today = True
        care.cleaned_today = True
        care.warmed_today = True
        care.protected_today = True

        care.mother_present = (
            mother is not None
        )

        if mother is not None:
            care_system = (
                CatMaternalCareSystem()
            )

            if (
                getattr(
                    kitten
                    .maternal_care_received,
                    "foster_mother",
                    None,
                )
                == mother.name
            ):
                maternal_sync = (
                    care_system
                    .record_foster_upbringing_care(
                        foster_mother=mother,
                        kitten=kitten,
                        events=events,
                        age_days=age_days,
                        current_day=current_day,
                    )
                )

            else:
                maternal_sync = (
                    care_system
                    .record_upbringing_care(
                        mother=mother,
                        kitten=kitten,
                        events=events,
                        age_days=age_days,
                        current_day=current_day,
                    )
                )

            events.append(
                maternal_sync
            )

        return events

    def _provide_reduced_care(
        self,
        kitten,
        mother,
        age_days,
        current_day,
    ):
        events = self._provide_daily_care(
            kitten=kitten,
            mother=mother,
            age_days=age_days,
            current_day=current_day,
        )

        kitten.upbringing.care.left_alone_briefly = (
            True
        )

        if age_days == 14:
            events.append(
                KittenMotherLeftBrieflyEvent(
                    kitten=kitten.name,
                    mother=(
                        mother.name
                        if mother is not None
                        else None
                    ),
                    age_days=age_days,
                    day=current_day,
                )
            )

            events.append(
                self.growth.feed_dead_delivery(
                    kitten=kitten,
                    day=current_day,
                )
            )

            events.append(
                KittenDeadCronenbergDeliveredEvent(
                    kitten=kitten.name,
                    mother=(
                        mother.name
                        if mother is not None
                        else None
                    ),
                    age_days=age_days,
                    day=current_day,
                )
            )

            (
                kitten.upbringing
                .cronenberg_experience
                .dead_deliveries
            ) += 1

        return events

    def _run_early_lessons(
        self,
        kitten,
        mother,
        age_days,
        current_day,
    ):
        events = []

        if age_days >= 14:
            events.append(
                self._advance_socialization_skill(
                    kitten=kitten,
                    teacher=mother,
                    age_days=age_days,
                    current_day=current_day,
                )
            )

        if age_days == 16:
            events.append(
                KittenSiblingPlayLessonEvent(
                    kitten=kitten.name,
                    age_days=age_days,
                    day=current_day,
                )
            )

        if age_days == 18:
            events.append(
                self._complete_skill(
                    kitten=kitten,
                    skill_name="litter_box",
                    teacher=mother,
                    age_days=age_days,
                    current_day=current_day,
                    lesson_name="mother_taught_litter_box",
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
                    lesson_name="mother_taught_box_travel",
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
                    lesson_name="mother_taught_cat_door_travel",
                )
            )

        return events

    def _run_hunting_upbringing(self, kitten, mother, father, age_days, current_day):
        events = []
        if age_days == self.LIVE_PREY_FIRST_DAY:
            events.append(self._bring_live_cronenberg(kitten=kitten, mother=mother, age_days=age_days, current_day=current_day))
        if self.LIVE_PREY_FIRST_DAY <= age_days <= 27:
            events.append(self._practice_hunting_step(kitten=kitten, teacher=mother, skill_step='tracking_and_chasing', progress_amount=0.04, age_days=age_days, current_day=current_day))
        elif 28 <= age_days <= self.LIVE_PREY_PRACTICE_LAST_DAY:
            events.append(self._practice_hunting_step(kitten=kitten, teacher=mother, skill_step='capture_and_killing_bite', progress_amount=0.05, age_days=age_days, current_day=current_day))
        elif age_days == self.FIRST_TRAINING_KILL_DAY:
            events.append(self._first_training_kill(kitten=kitten, mother=mother, age_days=age_days, current_day=current_day))
        elif age_days >= self.FAMILY_HUNT_FIRST_DAY:
            events.append(self._family_hunt(kitten=kitten, mother=mother, father=father, age_days=age_days, current_day=current_day))
        return events

    def _bring_live_cronenberg(
        self,
        kitten,
        mother,
        age_days,
        current_day,
    ):
        experience = (
            kitten.upbringing
            .cronenberg_experience
        )

        experience.live_deliveries += 1

        event = (
            KittenLiveCronenbergDeliveredEvent(
                kitten=kitten.name,
                mother=(
                    mother.name
                    if mother is not None
                    else None
                ),
                age_days=age_days,
                day=current_day,
            )
        )

        kitten.learning.lessons.append(
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
        current_day,
    ):
        hunting = (
            kitten.learning.skills[
                "hunting"
            ]
        )

        previous_progress = float(
            hunting.progress
        )

        progress = min(
            0.8,
            previous_progress
            + progress_amount,
        )

        teacher_name = (
            teacher.name
            if teacher is not None
            else kitten.learning.teacher_mother
        )

        hunting.progress = progress
        hunting.teacher = teacher_name

        event = (
            KittenHuntingStepPracticedEvent(
                kitten=kitten.name,
                teacher=teacher_name,
                step=skill_step,
                age_days=age_days,
                day=current_day,
                previous_progress=
                    previous_progress,
                progress=progress,
            )
        )

        kitten.learning.lessons.append(
            event
        )

        return event

    def _first_training_kill(
        self,
        kitten,
        mother,
        age_days,
        current_day,
    ):
        experience = (
            kitten.upbringing
            .cronenberg_experience
        )

        experience.successful_kills += 1

        hunting = (
            kitten.learning.skills[
                "hunting"
            ]
        )

        previous_progress = float(
            hunting.progress
        )

        hunting.progress = max(
            previous_progress,
            0.85,
        )

        growth_event = (
            self.growth.feed_first_kill(
                kitten=kitten,
                day=current_day,
            )
        )

        event = (
            KittenFirstTrainingKillEvent(
                kitten=kitten.name,
                mother=(
                    mother.name
                    if mother is not None
                    else None
                ),
                age_days=age_days,
                day=current_day,
                successful_kills=
                    experience.successful_kills,
                hunting_progress=
                    hunting.progress,
                growth=growth_event,
            )
        )

        kitten.learning.lessons.append(
            event
        )

        return event

    def _family_hunt(
        self,
        kitten,
        mother,
        father,
        age_days,
        current_day,
    ):
        experience = (
            kitten.upbringing
            .cronenberg_experience
        )

        experience.family_hunts += 1

        family_hunt_number = (
            experience.family_hunts
        )

        father_joined = (
            father is not None
            and family_hunt_number % 2 == 0
        )

        hunting = (
            kitten.learning.skills[
                "hunting"
            ]
        )

        previous_progress = float(
            hunting.progress
        )

        progress = min(
            1.0,
            previous_progress + 0.05,
        )

        enough_experience = (
            experience.successful_kills >= 1
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
                mother.name
            )

        if father_joined:
            teacher_names.append(
                father.name
            )

            kitten.learning.hunting_teacher_father = (
                father.name
            )

        hunting.progress = progress
        hunting.learned = learned

        hunting.teacher = (
            teacher_names[0]
            if teacher_names
            else None
        )

        if learned:
            hunting.learned_on_day = (
                current_day
            )

        growth_event = (
            self.growth.feed_family_hunt(
                kitten=kitten,
                day=current_day,
            )
        )

        event = (
            KittenFamilyHuntEvent(
                kitten=kitten.name,
                mother=(
                    mother.name
                    if mother is not None
                    else None
                ),
                father=(
                    father.name
                    if father is not None
                    else None
                ),
                father_joined=
                    father_joined,
                teachers=tuple(
                    teacher_names
                ),
                age_days=age_days,
                day=current_day,
                family_hunt_number=
                    family_hunt_number,
                hunting_progress=
                    progress,
                hunting_learned=
                    learned,
                growth=growth_event,
            )
        )

        kitten.learning.lessons.append(
            event
        )

        return event

    def _run_late_education(
        self,
        kitten,
        mother,
        cats,
        age_days,
        current_day,
    ):
        events = []

        teacher = self._find_late_teacher(
            kitten=kitten,
            mother=mother,
            cats=cats,
        )

        vocalization_index = (
            age_days - 60
        )

        if (
            0
            <= vocalization_index
            < len(
                CatLearning.ADULT_VOCALIZATIONS
            )
        ):
            if teacher is None:
                events.append(
                    KittenAdultVocalizationTeacherUnavailableEvent(
                        kitten=kitten.name,
                        age_days=age_days,
                        day=current_day,
                    )
                )

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
                        current_day=current_day,
                    )
                )

        if age_days == 75:
            events.append(
                self._teach_human_communication(
                    kitten=kitten,
                    teacher=teacher,
                    age_days=age_days,
                    current_day=current_day,
                )
            )

        if age_days == 90:
            if teacher is None:
                events.append(
                    KittenMeowTeacherUnavailableEvent(
                        kitten=kitten.name,
                        age_days=age_days,
                        day=current_day,
                    )
                )

            else:
                events.append(
                    self.meow_resolver.transmit(
                        mother=teacher,
                        kitten=kitten,
                        current_day=current_day,
                    )
                )

        return events

    def _teach_human_communication(
        self,
        kitten,
        teacher,
        age_days,
        current_day,
    ):
        learning = kitten.learning

        adult_meowing = (
            learning.skills[
                "adult_meowing"
            ]
        )

        if not adult_meowing.learned:
            return (
                KittenHumanCommunicationLessonDeniedResult(
                    kitten=kitten.name,
                    teacher=(
                        teacher.name
                        if teacher is not None
                        else None
                    ),
                    age_days=age_days,
                    day=current_day,
                    reason=(
                        "adult_vocalization_repertoire_incomplete"
                    ),
                )
            )

        if teacher is None:
            return (
                KittenHumanCommunicationLessonDeniedResult(
                    kitten=kitten.name,
                    teacher=None,
                    age_days=age_days,
                    day=current_day,
                    reason="teacher_unavailable",
                )
            )

        skill = (
            learning.skills[
                "human_communication"
            ]
        )

        skill.learned = True
        skill.progress = 1.0
        skill.teacher = teacher.name
        skill.learned_on_day = (
            current_day
        )

        learning.human_communication_learned = (
            True
        )

        event = (
            KittenHumanCommunicationLearnedEvent(
                kitten=kitten.name,
                teacher=teacher.name,
                age_days=age_days,
                day=current_day,
                uses=tuple(
                    CatLearning
                    .ADULT_VOCALIZATIONS
                ),
            )
        )

        learning.lessons.append(
            event
        )

        return event

    def _find_late_teacher(self, kitten, mother, cats):
        if self._is_qualified_late_teacher(mother, parental_exception=True):
            return mother
        substitute_name = getattr(
            getattr(kitten, 'learning', None),
            'teacher_mother',
            None,
        )
        if substitute_name:
            substitute = next((candidate for candidate in cats if getattr(candidate, 'name', None) == substitute_name), None)
            if self._is_qualified_late_teacher(substitute):
                return substitute
        for candidate in cats:
            if candidate is kitten:
                continue
            if candidate is mother:
                continue
            if self._is_qualified_late_teacher(candidate):
                return candidate
        return None

    def _is_qualified_late_teacher(self, candidate, parental_exception=False):
        if candidate is None:
            return False
        if not self._knows_meow(candidate):
            return False
        if parental_exception:
            return True
        wisdom = FelineWisdom.ensure_state(candidate)
        teaching = wisdom.ability_record(
            'teach_other_cats'
        )

        return bool(
            teaching is not None
            and teaching.learned
        )

    def _knows_meow(self, cat):
        meow = getattr(cat.learning, 'meow_knowledge', None)
        return bool(
            meow is not None
            and meow.learned
            and meow.can_speak
        )

    def _advance_socialization_skill(
        self,
        kitten,
        teacher,
        age_days,
        current_day,
    ):
        skill = (
            kitten.learning.skills[
                "socialization"
            ]
        )

        previous_progress = float(
            skill.progress
        )

        progress = min(
            1.0,
            previous_progress
            + (1.0 / 7.0),
        )

        learned = (
            progress >= 0.999999
        )

        teacher_name = (
            teacher.name
            if teacher is not None
            else kitten.learning.teacher_mother
        )

        skill.progress = progress
        skill.learned = learned
        skill.teacher = teacher_name

        if learned:
            skill.learned_on_day = (
                current_day
            )

        personality = (
            CatPersonality.apply_experience(
                cat=kitten,
                source="maternal_socialization",
                changes={
                    "empathy": 0.01,
                    "patience": 0.005,
                },
                day=current_day,
                metadata={
                    "teacher": teacher_name,
                    "age_days": age_days,
                    "skill_progress": progress,
                },
            )
        )

        event = (
            KittenSocializationLessonEvent(
                student=kitten.name,
                teacher=teacher_name,
                skill="socialization",
                age_days=age_days,
                day=current_day,
                previous_progress=
                    previous_progress,
                progress=progress,
                learned=learned,
                personality=personality,
            )
        )

        kitten.learning.lessons.append(
            event
        )

        return event

    def _complete_skill(
        self,
        kitten,
        skill_name,
        teacher,
        age_days,
        current_day,
        lesson_name,
    ):
        skill = (
            kitten.learning.skills[
                skill_name
            ]
        )

        teacher_name = (
            teacher.name
            if teacher is not None
            else kitten.learning.teacher_mother
        )

        skill.learned = True
        skill.progress = 1.0
        skill.teacher = teacher_name
        skill.learned_on_day = (
            current_day
        )

        event = (
            KittenSkillCompletedLessonEvent(
                name=lesson_name,
                student=kitten.name,
                teacher=teacher_name,
                skill=skill_name,
                age_days=age_days,
                day=current_day,
            )
        )

        kitten.learning.lessons.append(
            event
        )

        return event

    def _father_food_delivery(
        self,
        kitten,
        father,
        age_days,
        current_day,
    ):
        if father is None:
            return None

        if (
            age_days == 0
            or age_days % 5 != 0
        ):
            return None

        growth_event = (
            self.growth.feed_father_delivery(
                kitten=kitten,
                day=current_day,
            )
        )

        event = (
            KittenFatherFoodDeliveryEvent(
                kitten=kitten.name,
                father=father.name,
                age_days=age_days,
                day=current_day,
                growth=growth_event,
            )
        )

        (
            kitten.upbringing
            .cronenberg_experience
            .father_food_deliveries
        ) += 1

        return event

    def _find_parent(
        self,
        kitten,
        cats,
        parent_role
    ):
        parents = (
            CatParentageState
            .require_from_cat(kitten)
        )

        parent_name = (
            parents.name_for_role(
                parent_role
            )
        )

        if parent_name is not None:

            for cat in cats:

                if (
                    cat.name
                    == parent_name
                    and getattr(
                        cat,
                        "active",
                        True
                    )
                ):
                    return cat

        if parent_role == "mother":

            foster_name = getattr(
                kitten
                .maternal_care_received,
                "foster_mother",
                None
            )

            if foster_name is not None:

                for cat in cats:

                    if (
                        cat.name
                        == foster_name
                        and getattr(
                            cat,
                            "active",
                            True
                        )
                    ):
                        return cat

            learning = getattr(
                kitten,
                "learning",
                None
            )

            teacher_name = getattr(
                learning,
                "teacher_mother",
                None
            )

            if teacher_name is not None:

                for cat in cats:

                    if (
                        cat.name
                        == teacher_name
                        and getattr(
                            cat,
                            "active",
                            True
                        )
                    ):
                        return cat

        return None

    def _create_upbringing_state(self):
        return KittenUpbringingState()

    def _ensure_upbringing_state(
        self,
        kitten,
    ):
        state = getattr(
            kitten,
            'upbringing',
            None,
        )

        if state is None:
            state = (
                self._create_upbringing_state()
            )
            kitten.upbringing = state

        elif not isinstance(
            state,
            KittenUpbringingState,
        ):
            raise TypeError(
                'Kitten upbringing state must be '
                'KittenUpbringingState.'
            )

        if not isinstance(
            state.care,
            KittenCareState,
        ):
            raise TypeError(
                'Kitten upbringing care state '
                'must be KittenCareState.'
            )

        if not isinstance(
            state.cronenberg_experience,
            KittenCronenbergExperienceState,
        ):
            raise TypeError(
                'Kitten Cronenberg experience '
                'state must be '
                'KittenCronenbergExperienceState.'
            )

        return state

    def _skip(
        self,
        kitten,
        current_day,
        reason,
    ):
        event = (
            KittenUpbringingDaySkippedResult(
                kitten=getattr(
                    kitten,
                    "name",
                    None,
                ),
                day=current_day,
                reason=reason,
            )
        )

        self.history.append(
            replace(
                event
            )
        )

        return event

    def _record(
        self,
        kitten,
        event,
    ):
        if not isinstance(
            event,
            KittenUpbringingDayCompletedEvent,
        ):
            raise TypeError(
                "Kitten upbringing history "
                "requires completed event objects."
            )

        self.history.append(
            replace(
                event
            )
        )

        kitten.upbringing.history.append(
            replace(
                event
            )
        )

        quantum_events = getattr(
            self.universe,
            "quantum_events",
            None,
        )

        if quantum_events is not None:
            quantum_events.append(
                replace(
                    event
                )
            )
