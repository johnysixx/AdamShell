from copy import deepcopy

from cats.cat import Cat
from cats.cat_maternal_care_system import (
    CatMaternalCareSystem
)
from cats.garfield_training_system import (
    GarfieldTrainingSystem
)


class CatEmergencyLactationSystem:

    MAX_MILK_AGE_DAYS = (
        CatMaternalCareSystem
        .WEANING_END_DAY
    )

    def __init__(
        self,
        cats_layer=None,
        meeting_place=None
    ):
        self.cats_layer = cats_layer
        self.meeting_place = meeting_place

        self.garfield = (
            GarfieldTrainingSystem()
        )

        self.history = []

    def needs_orphan_rescue(
        self,
        kitten,
        cats=None
    ):
        self._require_cat(
            kitten
        )

        learning = getattr(
            kitten,
            "learning",
            {}
        )

        age_days = int(
            getattr(
                kitten,
                "age_days",
                0
            )
        )

        needs_teaching = bool(
            learning.get(
                "teaching_required",
                False
            )
        )

        needs_milk = (
            age_days
            <= self.MAX_MILK_AGE_DAYS
        )

        mother_name = (
            self._mother_name(
                kitten
            )
        )

        mother_available = (
            self._mother_available(
                mother_name,
                cats
            )
        )

        return {
            "kitten":
                kitten.name,
            "mother":
                mother_name,
            "mother_available":
                mother_available,
            "needs_teaching":
                needs_teaching,
            "needs_milk":
                needs_milk,
            "orphan_rescue_needed":
                (
                    not mother_available
                    and needs_teaching
                    and needs_milk
                ),
        }

    def rescue_orphaned_kittens(
        self,
        rescuer,
        kittens,
        cats=None,
        meeting_place=None,
        current_day=None
    ):
        self._require_cat(
            rescuer
        )

        kittens = list(
            kittens
        )

        if not kittens:
            return {
                "name":
                    "orphan_kitten_rescue_denied",
                "reason":
                    "no_kittens",
                "rescued":
                    False,
            }

        for kitten in kittens:
            self._require_cat(
                kitten
            )

        if not bool(
            getattr(
                rescuer
                .emergency_nursing,
                "can_induce_lactation",
                False
            )
        ):
            return {
                "name":
                    "orphan_kitten_rescue_denied",
                "cat":
                    rescuer.name,
                "reason":
                    "cat_cannot_induce_lactation",
                "rescued":
                    False,
            }

        if cats is None:
            cats = list(
                getattr(
                    self.cats_layer,
                    "cats",
                    []
                )
            )
        else:
            cats = list(
                cats
            )

        assessments = [
            self.needs_orphan_rescue(
                kitten,
                cats=cats
            )
            for kitten
            in kittens
        ]

        eligible = [
            kitten
            for kitten, assessment
            in zip(
                kittens,
                assessments
            )
            if assessment[
                "orphan_rescue_needed"
            ]
        ]

        if not eligible:
            return {
                "name":
                    "orphan_kitten_rescue_denied",
                "cat":
                    rescuer.name,
                "reason":
                    "no_orphaned_milk_dependent_kittens",
                "assessments":
                    assessments,
                "rescued":
                    False,
            }

        bar = (
            meeting_place
            or self.meeting_place
        )

        if bar is None:
            return {
                "name":
                    "orphan_kitten_rescue_denied",
                "cat":
                    rescuer.name,
                "reason":
                    "meeting_place_unavailable",
                "rescued":
                    False,
            }

        transport = (
            self._bring_to_bar(
                rescuer,
                eligible,
                bar
            )
        )

        advice = (
            self.garfield
            .advise_emergency_lactation(
                rescuer,
                eligible
            )
        )

        foster_events = (
            self._induce_and_assign(
                rescuer=rescuer,
                kittens=eligible,
                current_day=current_day
            )
        )

        event = {
            "name":
                "cat_rescued_orphaned_kittens",
            "cat":
                rescuer.name,
            "kittens": [
                kitten.name
                for kitten
                in eligible
            ],
            "bar":
                "meeting_place",
            "transport":
                transport,
            "garfield_advice":
                advice,
            "foster_events":
                foster_events,
            "lactation_induced":
                True,
            "rescued":
                True,
        }

        (
            rescuer
            .emergency_nursing
            .rescued_litters
            .append(
                [
                    kitten.name
                    for kitten
                    in eligible
                ]
            )
        )

        self.history.append(
            deepcopy(event)
        )

        emit_event = getattr(
            self.cats_layer,
            "emit_event",
            None
        )

        if callable(
            emit_event
        ):
            emit_event(
                deepcopy(event)
            )

        return event

    def _bring_to_bar(
        self,
        rescuer,
        kittens,
        meeting_place
    ):
        arrivals = []

        for cat in [
            rescuer,
            *kittens
        ]:

            arrival = (
                meeting_place
                .admit_cat(
                    cat,
                    bartender_available=True
                )
            )

            arrivals.append(
                arrival
            )

        rescuer.state = (
            "rescuing_orphaned_kittens"
        )

        for kitten in kittens:

            kitten.state = (
                "rescued_orphan_kitten"
            )

            (
                kitten
                .maternal_care_received
                .rescued_to_bar
            ) = True

        event = {
            "name":
                "cat_brought_orphaned_kittens_to_bar",
            "cat":
                rescuer.name,
            "kittens": [
                kitten.name
                for kitten
                in kittens
            ],
            "arrivals":
                arrivals,
            "transported":
                True,
        }

        meeting_place.emit_event(
            deepcopy(event)
        )

        return event

    def _induce_and_assign(
        self,
        rescuer,
        kittens,
        current_day=None
    ):
        state = (
            rescuer
            .emergency_nursing
        )

        if (
            int(
                getattr(
                    state,
                    "garfield_consultations",
                    0
                )
            )
            <= 0
        ):
            raise RuntimeError(
                "Garfield advice is required "
                "before emergency lactation."
            )

        state.induced_lactation = True
        state.active = True

        care = (
            CatMaternalCareSystem(
                self.cats_layer
            )
        )

        events = []

        for kitten in kittens:

            if (
                kitten.name
                not in state.foster_kittens
            ):
                state.foster_kittens.append(
                    kitten.name
                )

            received = (
                kitten
                .maternal_care_received
            )

            received.foster_mother = (
                rescuer.name
            )

            received.needs_milk = True
            received.needs_teaching = True

            received.garfield_advice_received = (
                True
            )

            kitten.learning[
                "teacher_mother"
            ] = rescuer.name

            age_days = int(
                getattr(
                    kitten,
                    "age_days",
                    0
                )
            )

            events.append(
                care.provide_foster_care(
                    foster_mother=rescuer,
                    kitten=kitten,
                    age_days=age_days,
                    current_day=current_day
                )
            )

        return events

    def _mother_name(
        self,
        kitten
    ):
        family = getattr(
            kitten,
            "family",
            None
        )

        if family is not None:

            mother = (
                getattr(
                    family,
                    "parents",
                    {}
                )
                .get(
                    "mother"
                )
            )

            if mother is not None:
                return mother

        parents = getattr(
            kitten,
            "parents",
            {}
        )

        mother = parents.get(
            "mother"
        )

        if mother is not None:
            return mother

        return getattr(
            kitten,
            "mother_name",
            None
        )

    def _mother_available(
        self,
        mother_name,
        cats
    ):
        if mother_name is None:
            return False

        if cats is None:
            candidates = list(
                getattr(
                    self.cats_layer,
                    "cats",
                    []
                )
            )
        else:
            candidates = list(
                cats
            )

        for cat in candidates:

            if (
                cat.name
                == mother_name
                and getattr(
                    cat,
                    "active",
                    True
                )
            ):
                return True

        return False

    def _require_cat(
        self,
        cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatEmergencyLactationSystem "
                "requires Cat."
            )
