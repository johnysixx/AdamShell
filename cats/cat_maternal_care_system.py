from copy import deepcopy

from cats.cat import Cat
from cats.cat_family_system import (
    CatFamilySystem
)


class CatMaternalCareSystem:

    NEONATAL_END_DAY = 14
    COMPLETE_CARE_END_DAY = 28
    WEANING_END_DAY = 56

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

    def care_phase(
        self,
        age_days
    ):
        age_days = max(
            0,
            int(
                age_days
            )
        )

        if age_days <= self.NEONATAL_END_DAY:
            return "neonatal_maternal_care"

        if age_days <= self.COMPLETE_CARE_END_DAY:
            return "complete_maternal_care"

        if age_days <= self.WEANING_END_DAY:
            return "reduced_maternal_care"

        return "maternal_independence"

    def evaluate(
        self,
        mother,
        kitten,
        age_days
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
                kitten
            )
        )

        biological_child = (
            relation == "child"
            and kitten.family[
                "parents"
            ].get(
                "mother"
            )
            == mother.name
        )

        phase = self.care_phase(
            age_days
        )

        return {
            "mother": mother.name,
            "kitten": kitten.name,
            "biological_child": biological_child,
            "phase": phase,
            "nursing": (
                biological_child
                and phase != "maternal_independence"
            ),
            "cleaning": biological_child,
            "warming": (
                biological_child
                and phase
                == "neonatal_maternal_care"
            ),
            "protection": biological_child,
            "retrieval": (
                biological_child
                and phase in {
                    "neonatal_maternal_care",
                    "complete_maternal_care"
                }
            ),
            "active": (
                biological_child
                and phase
                != "maternal_independence"
            )
        }

    def provide_care(
        self,
        mother,
        kitten,
        age_days,
        current_day=None
    ):
        assessment = self.evaluate(
            mother,
            kitten,
            age_days
        )

        if not assessment[
            "biological_child"
        ]:
            return {
                "name": "maternal_care_denied",
                "mother": mother.name,
                "kitten": kitten.name,
                "reason": "not_biological_mother",
                "provided": False
            }

        phase = assessment[
            "phase"
        ]

        actions = []

        if assessment[
            "nursing"
        ]:
            actions.append(
                "nursing"
            )

        if assessment[
            "cleaning"
        ]:
            actions.append(
                "cleaning"
            )

        if assessment[
            "warming"
        ]:
            actions.append(
                "warming"
            )

        if assessment[
            "protection"
        ]:
            actions.append(
                "protection"
            )

        if assessment[
            "retrieval"
        ]:
            actions.append(
                "retrieval"
            )

        event = {
            "name": "cat_maternal_care",
            "mother": mother.name,
            "kitten": kitten.name,
            "age_days": int(
                age_days
            ),
            "day": current_day,
            "phase": phase,
            "actions": list(
                actions
            ),
            "provided": True
        }

        self._record(
            mother,
            kitten,
            event
        )

        return event

    def record_upbringing_care(
        self,
        mother,
        kitten,
        events,
        age_days,
        current_day=None
    ):
        """
        Mirror care already performed by
        KittenUpbringingResolver.

        This method never feeds or performs
        care itself, so upbringing effects
        are not duplicated.
        """
        self._require_cat(
            mother
        )

        self._require_cat(
            kitten
        )

        assessment = self.evaluate(
            mother,
            kitten,
            age_days
        )

        if not assessment[
            "biological_child"
        ]:
            return {
                "name": (
                    "maternal_upbringing_sync_denied"
                ),
                "mother": mother.name,
                "kitten": kitten.name,
                "synced": False,
                "reason": "not_biological_mother"
            }

        mapping = {
            "fed_by_mother": "nursing",
            "cleaned_by_mother": "cleaning",
            "warmed_by_mother": "warming",
            "protected_by_mother": "protection"
        }

        actions = []

        for existing_event in events:
            if not isinstance(
                existing_event,
                dict
            ):
                continue

            action = mapping.get(
                existing_event.get(
                    "name"
                )
            )

            if (
                action is not None
                and action not in actions
            ):
                actions.append(
                    action
                )

        sync_event = {
            "name": (
                "maternal_upbringing_care_synced"
            ),
            "mother": mother.name,
            "kitten": kitten.name,
            "age_days": int(
                age_days
            ),
            "day": current_day,
            "phase": assessment[
                "phase"
            ],
            "actions": actions,
            "synced": True
        }

        self._record_state_only(
            mother=mother,
            kitten=kitten,
            event=sync_event
        )

        return sync_event

    def protect_from_threat(
        self,
        mother,
        kitten,
        threat,
        current_day=None
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
            age_days=0
        )

        if not assessment[
            "biological_child"
        ]:
            return {
                "name": (
                    "maternal_protection_denied"
                ),
                "mother": mother.name,
                "kitten": kitten.name,
                "protected": False,
                "reason": "not_biological_mother"
            }

        if isinstance(
            threat,
            dict
        ):
            threat_name = threat.get(
                "name"
            )
        else:
            threat_name = getattr(
                threat,
                "name",
                str(
                    threat
                )
            )

        mother.state = (
            "protecting_kitten"
        )

        kitten.state = (
            "protected_by_mother"
        )

        event = {
            "name": (
                "mother_protected_kitten"
            ),
            "mother": mother.name,
            "kitten": kitten.name,
            "threat": threat_name,
            "day": current_day,
            "protected": True
        }

        mother.maternal_care[
            "care_events"
        ] += 1

        kitten.maternal_care_received[
            "mother"
        ] = mother.name

        kitten.maternal_care_received[
            "care_events"
        ] += 1

        kitten.maternal_care_received[
            "protection_events"
        ] += 1

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
            None
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
        event
    ):
        state = mother.maternal_care

        kitten_state = state[
            "kittens"
        ].setdefault(
            kitten.name,
            {
                "care_events": 0,
                "last_care_day": None,
                "last_phase": None
            }
        )

        state[
            "active"
        ] = (
            event[
                "phase"
            ]
            != "maternal_independence"
        )

        state[
            "care_events"
        ] += 1

        kitten_state[
            "care_events"
        ] += 1

        kitten_state[
            "last_care_day"
        ] = event[
            "day"
        ]

        kitten_state[
            "last_phase"
        ] = event[
            "phase"
        ]

        received = (
            kitten
            .maternal_care_received
        )

        received[
            "mother"
        ] = mother.name

        received[
            "care_events"
        ] += 1

        received[
            "last_care_day"
        ] = event[
            "day"
        ]

        received[
            "last_phase"
        ] = event[
            "phase"
        ]

        counters = {
            "nursing": "nursing_events",
            "cleaning": "cleaning_events",
            "warming": "warming_events",
            "protection": "protection_events",
            "retrieval": "retrieval_events"
        }

        for action in event[
            "actions"
        ]:
            counter = counters.get(
                action
            )

            if counter is not None:
                received[
                    counter
                ] += 1

    def _record(
        self,
        mother,
        kitten,
        event
    ):
        state = mother.maternal_care

        state[
            "active"
        ] = (
            event[
                "phase"
            ]
            != "maternal_independence"
        )

        kitten_state = state[
            "kittens"
        ].setdefault(
            kitten.name,
            {
                "care_events": 0,
                "last_care_day": None,
                "last_phase": None
            }
        )

        state[
            "care_events"
        ] += 1

        kitten_state[
            "care_events"
        ] += 1

        kitten_state[
            "last_care_day"
        ] = event[
            "day"
        ]

        kitten_state[
            "last_phase"
        ] = event[
            "phase"
        ]

        received = (
            kitten
            .maternal_care_received
        )

        received[
            "mother"
        ] = mother.name

        received[
            "care_events"
        ] += 1

        received[
            "last_care_day"
        ] = event[
            "day"
        ]

        received[
            "last_phase"
        ] = event[
            "phase"
        ]

        action_counters = {
            "nursing": (
                "nursing_events"
            ),
            "cleaning": (
                "cleaning_events"
            ),
            "warming": (
                "warming_events"
            ),
            "protection": (
                "protection_events"
            ),
            "retrieval": (
                "retrieval_events"
            )
        }

        for action in event[
            "actions"
        ]:
            received[
                action_counters[
                    action
                ]
            ] += 1

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
            None
        )

        if callable(
            emit_event
        ):
            emit_event(
                deepcopy(
                    event
                )
            )

    def _require_cat(
        self,
        cat
    ):
        if not isinstance(
            cat,
            Cat
        ):
            raise TypeError(
                "CatMaternalCareSystem "
                "requires Cat."
            )
