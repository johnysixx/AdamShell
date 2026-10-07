from copy import deepcopy
from cats.cat_maternal_kitten_care_state import (
    CatMaternalKittenCareState,
)
from cats.maternal_care_phase import (
    MaternalCarePhase,
)
from cats.cat import Cat
from cats.cat_family_system import CatFamilySystem
from cats.cat_parentage_state import (
    CatParentageState
)
from cats.cat_maternal_care_result_state import (
    CatMaternalCareAssessment,
    CatMaternalCareDeniedResult,
    CatMaternalCareEvent,
    CatMaternalProtectionDeniedResult,
    CatMotherProtectedKittenEvent,
    CatFosterMaternalCareDeniedResult,
    CatFosterMaternalCareEvent,
    CatMaternalUpbringingSyncDeniedResult,
    CatMaternalUpbringingCareSyncedEvent,
    CatFosterUpbringingSyncDeniedResult,
    CatFosterUpbringingCareSyncedEvent,
)

class CatMaternalCareSystem:
    NEONATAL_END_DAY = 14
    COMPLETE_CARE_END_DAY = 28
    WEANING_END_DAY = 56

    def __init__(self, cats_layer=None):
        self.cats_layer = cats_layer
        self.family_system = CatFamilySystem(cats_layer)

    def care_phase(self, age_days):
        age_days = max(0, int(age_days))
        if age_days <= self.NEONATAL_END_DAY:
            return MaternalCarePhase.NEONATAL
        if age_days <= self.COMPLETE_CARE_END_DAY:
            return MaternalCarePhase.COMPLETE
        if age_days <= self.WEANING_END_DAY:
            return MaternalCarePhase.REDUCED
        return MaternalCarePhase.INDEPENDENCE

    def evaluate(
        self,
        mother,
        kitten,
        age_days,
    ):
        self._require_cat(
            mother
        )

        self._require_cat(
            kitten
        )

        relation = (
            self.family_system.relation(
                mother,
                kitten,
            )
        )

        parentage = (
            CatParentageState
            .require_from_cat(
                kitten
            )
        )

        biological_child = (
            relation == "child"
            and parentage.mother
            == mother.name
        )

        phase = self.care_phase(
            age_days
        )

        return CatMaternalCareAssessment(
            mother=mother.name,
            kitten=kitten.name,
            biological_child=
                biological_child,
            phase=phase,
            nursing=(
                biological_child
                and phase
                is not
                MaternalCarePhase.INDEPENDENCE
            ),
            cleaning=
                biological_child,
            warming=(
                biological_child
                and phase
                is MaternalCarePhase.NEONATAL
            ),
            protection=
                biological_child,
            retrieval=(
                biological_child
                and phase
                in {
                    MaternalCarePhase.NEONATAL,
                    MaternalCarePhase.COMPLETE,
                }
            ),
            active=(
                biological_child
                and phase
                is not
                MaternalCarePhase.INDEPENDENCE
            ),
        )

    def provide_care(
        self,
        mother,
        kitten,
        age_days,
        current_day=None,
    ):
        assessment = self.evaluate(
            mother,
            kitten,
            age_days,
        )

        if not assessment.biological_child:
            return CatMaternalCareDeniedResult(
                mother=mother.name,
                kitten=kitten.name,
                reason="not_biological_mother",
            )

        actions = []

        if assessment.nursing:
            actions.append(
                "nursing"
            )

        if assessment.cleaning:
            actions.append(
                "cleaning"
            )

        if assessment.warming:
            actions.append(
                "warming"
            )

        if assessment.protection:
            actions.append(
                "protection"
            )

        if assessment.retrieval:
            actions.append(
                "retrieval"
            )

        event = CatMaternalCareEvent(
            mother=mother.name,
            kitten=kitten.name,
            age_days=age_days,
            day=current_day,
            phase=assessment.phase,
            actions=tuple(actions),
        )

        self._record(
            mother,
            kitten,
            event,
        )

        return event

    def record_upbringing_care(
        self,
        mother,
        kitten,
        events,
        age_days,
        current_day=None,
    ):
        self._require_cat(
            mother
        )

        self._require_cat(
            kitten
        )

        assessment = self.evaluate(
            mother,
            kitten,
            age_days,
        )

        if not assessment.biological_child:
            return (
                CatMaternalUpbringingSyncDeniedResult(
                    mother=mother.name,
                    kitten=kitten.name,
                    reason="not_biological_mother",
                )
            )

        mapping = {
            "fed_by_mother":
                "nursing",
            "cleaned_by_mother":
                "cleaning",
            "warmed_by_mother":
                "warming",
            "protected_by_mother":
                "protection",
        }

        actions = []

        for existing_event in events:
            if isinstance(
                existing_event,
                dict,
            ):
                raise TypeError(
                    "Maternal upbringing sync "
                    "requires event objects."
                )

            event_name = getattr(
                existing_event,
                "name",
                None,
            )

            if event_name is None:
                raise TypeError(
                    "Maternal upbringing event "
                    "must expose a name attribute."
                )

            action = mapping.get(
                event_name
            )

            if (
                action is not None
                and action not in actions
            ):
                actions.append(
                    action
                )

        event = (
            CatMaternalUpbringingCareSyncedEvent(
                mother=mother.name,
                kitten=kitten.name,
                age_days=age_days,
                day=current_day,
                phase=assessment.phase,
                actions=tuple(actions),
            )
        )

        self._record_state_only(
            mother=mother,
            kitten=kitten,
            event=event,
        )

        return event

    def provide_foster_care(
        self,
        foster_mother,
        kitten,
        age_days,
        current_day=None,
    ):
        self._require_cat(
            foster_mother
        )

        self._require_cat(
            kitten
        )

        received = (
            kitten
            .maternal_care_received
        )

        registered = (
            getattr(
                received,
                "foster_mother",
                None,
            )
            == foster_mother.name
            and kitten.name
            in getattr(
                foster_mother
                .emergency_nursing,
                "foster_kittens",
                [],
            )
            and bool(
                getattr(
                    foster_mother
                    .emergency_nursing,
                    "active",
                    False,
                )
            )
        )

        if not registered:
            return (
                CatFosterMaternalCareDeniedResult(
                    foster_mother=
                        foster_mother.name,
                    kitten=kitten.name,
                    reason=(
                        "foster_relationship_not_active"
                    ),
                )
            )

        phase = self.care_phase(
            age_days
        )

        actions = []

        if (
            phase
            is not
            MaternalCarePhase.INDEPENDENCE
        ):
            actions.append(
                "nursing"
            )

        actions.append(
            "cleaning"
        )

        if (
            phase
            is MaternalCarePhase.NEONATAL
        ):
            actions.append(
                "warming"
            )

        actions.append(
            "protection"
        )

        if phase in {
            MaternalCarePhase.NEONATAL,
            MaternalCarePhase.COMPLETE,
        }:
            actions.append(
                "retrieval"
            )

        event = (
            CatFosterMaternalCareEvent(
                foster_mother=
                    foster_mother.name,
                kitten=kitten.name,
                age_days=age_days,
                day=current_day,
                phase=phase,
                actions=tuple(actions),
            )
        )

        self._record_foster_care(
            foster_mother,
            kitten,
            event,
        )

        return event

    def record_foster_upbringing_care(
        self,
        foster_mother,
        kitten,
        events,
        age_days,
        current_day=None,
    ):
        self._require_cat(
            foster_mother
        )

        self._require_cat(
            kitten
        )

        if (
            getattr(
                kitten
                .maternal_care_received,
                "foster_mother",
                None,
            )
            != foster_mother.name
        ):
            return (
                CatFosterUpbringingSyncDeniedResult(
                    foster_mother=
                        foster_mother.name,
                    kitten=kitten.name,
                    reason=(
                        "not_registered_foster_mother"
                    ),
                )
            )

        mapping = {
            "fed_by_mother":
                "nursing",
            "cleaned_by_mother":
                "cleaning",
            "warmed_by_mother":
                "warming",
            "protected_by_mother":
                "protection",
        }

        actions = []

        for existing_event in events:
            if isinstance(
                existing_event,
                dict,
            ):
                raise TypeError(
                    "Foster upbringing sync "
                    "requires event objects."
                )

            event_name = getattr(
                existing_event,
                "name",
                None,
            )

            if event_name is None:
                raise TypeError(
                    "Foster upbringing event "
                    "must expose a name attribute."
                )

            action = mapping.get(
                event_name
            )

            if (
                action is not None
                and action not in actions
            ):
                actions.append(
                    action
                )

        event = (
            CatFosterUpbringingCareSyncedEvent(
                foster_mother=
                    foster_mother.name,
                kitten=kitten.name,
                age_days=age_days,
                day=current_day,
                phase=self.care_phase(
                    age_days
                ),
                actions=tuple(actions),
            )
        )

        self._record_foster_upbringing_sync(
            foster_mother,
            kitten,
            event,
        )

        return event

    def _record_foster_care(
        self,
        foster_mother,
        kitten,
        event,
    ):
        state = (
            foster_mother
            .maternal_care
        )

        kitten_state = self._kitten_state(
            state,
            kitten.name,
        )

        state.active = (
            event.phase
            is not
            MaternalCarePhase.INDEPENDENCE
        )

        state.care_events += 1

        kitten_state.record(
            event.day,
            event.phase,
        )

        received = (
            kitten
            .maternal_care_received
        )

        received.foster_mother = (
            foster_mother.name
        )

        received.care_events += 1
        received.foster_care_events += 1

        received.last_care_day = (
            event.day
        )

        received.last_phase = (
            event.phase
        )

        counters = {
            "nursing":
                "nursing_events",
            "cleaning":
                "cleaning_events",
            "warming":
                "warming_events",
            "protection":
                "protection_events",
            "retrieval":
                "retrieval_events",
        }

        for action in event.actions:
            counter = counters.get(
                action
            )

            if counter is not None:
                setattr(
                    received,
                    counter,
                    getattr(
                        received,
                        counter,
                    )
                    + 1,
                )

            if action == "nursing":
                received.foster_nursing_events += 1

                (
                    foster_mother
                    .emergency_nursing
                    .milk_feedings
                ) += 1

                received.needs_milk = False

        foster_mother.social_interactions.append(
            deepcopy(
                event
            )
        )

        kitten.social_interactions.append(
            deepcopy(
                event
            )
        )

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None,
        )

        if callable(
            emit_event
        ):
            emit_event(
                deepcopy(
                    event
                )
            )

    def _record_foster_upbringing_sync(
        self,
        foster_mother,
        kitten,
        event,
    ):
        state = (
            foster_mother
            .maternal_care
        )

        kitten_state = self._kitten_state(
            state,
            kitten.name,
        )

        state.active = (
            event.phase
            is not
            MaternalCarePhase.INDEPENDENCE
        )

        state.care_events += 1

        kitten_state.record(
            event.day,
            event.phase,
        )

        received = (
            kitten
            .maternal_care_received
        )

        received.foster_mother = (
            foster_mother.name
        )

        received.care_events += 1
        received.foster_care_events += 1

        received.last_care_day = (
            event.day
        )

        received.last_phase = (
            event.phase
        )

        counters = {
            "nursing":
                "nursing_events",
            "cleaning":
                "cleaning_events",
            "warming":
                "warming_events",
            "protection":
                "protection_events",
            "retrieval":
                "retrieval_events",
        }

        for action in event.actions:
            counter = counters.get(
                action
            )

            if counter is not None:
                setattr(
                    received,
                    counter,
                    getattr(
                        received,
                        counter,
                    )
                    + 1,
                )

            if action == "nursing":
                received.foster_nursing_events += 1

                (
                    foster_mother
                    .emergency_nursing
                    .milk_feedings
                ) += 1

                received.needs_milk = False

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None,
        )

        if callable(
            emit_event
        ):
            emit_event(
                deepcopy(
                    event
                )
            )

    def protect_from_threat(
        self,
        mother,
        kitten,
        threat,
        current_day=None,
    ):
        self._require_cat(
            mother
        )

        self._require_cat(
            kitten
        )

        assessment = self.evaluate(
            mother,
            kitten,
            age_days=0,
        )

        if not assessment.biological_child:
            return (
                CatMaternalProtectionDeniedResult(
                    mother=mother.name,
                    kitten=kitten.name,
                    reason="not_biological_mother",
                )
            )

        if isinstance(
            threat,
            dict,
        ):
            threat_name = threat.get(
                "name"
            )

        else:
            threat_name = getattr(
                threat,
                "name",
                str(threat),
            )

        mother.state = (
            "protecting_kitten"
        )

        kitten.state = (
            "protected_by_mother"
        )

        event = (
            CatMotherProtectedKittenEvent(
                mother=mother.name,
                kitten=kitten.name,
                threat=threat_name,
                day=current_day,
            )
        )

        mother.maternal_care.care_events += 1

        received = (
            kitten.maternal_care_received
        )

        received.mother = mother.name
        received.care_events += 1
        received.protection_events += 1

        mother.social_interactions.append(
            deepcopy(
                event
            )
        )

        kitten.social_interactions.append(
            deepcopy(
                event
            )
        )

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None,
        )

        if callable(
            emit_event
        ):
            emit_event(
                deepcopy(
                    event
                )
            )

        return event

    def _record_state_only(
        self,
        mother,
        kitten,
        event,
    ):
        state = mother.maternal_care

        kitten_state = self._kitten_state(
            state,
            kitten.name,
        )

        state.active = (
            event.phase
            is not
            MaternalCarePhase.INDEPENDENCE
        )

        state.care_events += 1

        kitten_state.record(
            event.day,
            event.phase,
        )

        received = (
            kitten
            .maternal_care_received
        )

        received.mother = mother.name
        received.care_events += 1

        received.last_care_day = (
            event.day
        )

        received.last_phase = (
            event.phase
        )

        counters = {
            "nursing":
                "nursing_events",
            "cleaning":
                "cleaning_events",
            "warming":
                "warming_events",
            "protection":
                "protection_events",
            "retrieval":
                "retrieval_events",
        }

        for action in event.actions:
            counter = counters.get(
                action
            )

            if counter is not None:
                setattr(
                    received,
                    counter,
                    getattr(
                        received,
                        counter,
                    )
                    + 1,
                )

    def _record(
        self,
        mother,
        kitten,
        event,
    ):
        state = mother.maternal_care

        state.active = (
            event.phase
            is not
            MaternalCarePhase.INDEPENDENCE
        )

        kitten_state = self._kitten_state(
            state,
            kitten.name,
        )

        state.care_events += 1

        kitten_state.record(
            event.day,
            event.phase,
        )

        received = (
            kitten.maternal_care_received
        )

        received.mother = mother.name
        received.care_events += 1

        received.last_care_day = (
            event.day
        )

        received.last_phase = (
            event.phase
        )

        action_counters = {
            "nursing":
                "nursing_events",
            "cleaning":
                "cleaning_events",
            "warming":
                "warming_events",
            "protection":
                "protection_events",
            "retrieval":
                "retrieval_events",
        }

        for action in event.actions:
            counter = (
                action_counters[
                    action
                ]
            )

            setattr(
                received,
                counter,
                getattr(
                    received,
                    counter,
                )
                + 1,
            )

        mother.social_interactions.append(
            deepcopy(
                event
            )
        )

        kitten.social_interactions.append(
            deepcopy(
                event
            )
        )

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None,
        )

        if callable(
            emit_event
        ):
            emit_event(
                deepcopy(
                    event
                )
            )

    def _kitten_state(
        self,
        maternal_state,
        kitten_name,
    ):
        kitten_state = (
            maternal_state.kittens.get(
                kitten_name
            )
        )

        if kitten_state is None:
            kitten_state = (
                CatMaternalKittenCareState()
            )

            maternal_state.kittens[
                kitten_name
            ] = kitten_state

        elif not isinstance(
            kitten_state,
            CatMaternalKittenCareState,
        ):
            raise TypeError(
                'Maternal kitten care record '
                'must be '
                'CatMaternalKittenCareState.'
            )

        return kitten_state

    def _require_cat(self, cat):
        if not isinstance(cat, Cat):
            raise TypeError('CatMaternalCareSystem requires Cat.')
