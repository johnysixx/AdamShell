import random
from cats.physical_biology_gate import PhysicalBiologyGate
from cats.estrous_cycle_resolver import CatEstrousCycleResolver
from cats.ovulation_resolver import CatOvulationResolver
from cats.reproduction import CatReproduction
from cats.kitten_embryo_resolver import KittenEmbryoResolver
from cats.paternity_resolver import MultipleSirePaternityResolver
from cats.mating_contact import (
    CatMatingContact,
    CatMatingContactRecordedEvent,
    CatMatingHistoryEvent,
    CatMatingWindowClosedWithoutOvulationEvent,
)
from cats.mating_pregnancy_event import (
    CatPregnancyEmbryoResult,
    CatPregnancyPaternityResult,
    CatPregnancyStartedEvent,
)

class CatMatingResolver:

    def __init__(self, universe):
        self.universe = universe
        self.history = []
        self.biology_gate = PhysicalBiologyGate(universe)
        self.embryo_resolver = KittenEmbryoResolver(universe)
        self.paternity_resolver = MultipleSirePaternityResolver()
        self.estrous_cycle_resolver = CatEstrousCycleResolver(universe)
        self.ovulation_resolver = CatOvulationResolver(universe)

    def mate(self, female, male, current_day=0):
        biology = self.biology_gate.require_physical_world(operation='cat_mating', cat=female)
        if not biology['allowed']:
            return biology
        self._validate_pair(female, male)
        reproduction = female.reproduction
        if not reproduction.estrus_active:
            return {'name': 'cat_mating_denied', 'female': getattr(female, 'name', None), 'male': getattr(male, 'name', None), 'reason': 'female_not_in_estrus', 'mating_recorded': False}
        reproduction = female.reproduction
        current_day = int(current_day)
        if reproduction.pregnant:
            raise ValueError('A pregnant cat cannot add another potential father.')
        if not reproduction.mating_window_open:
            reproduction.estrus_active = True
            reproduction.mating_window_open = True
            reproduction.mating_window_started_day = current_day
            reproduction.mating_contacts = []
            reproduction.potential_fathers = []
        contact_number = len(reproduction.mating_contacts) + 1
        contact = CatMatingContact(
            contact_number=(
                contact_number
            ),
            female=female.name,
            male=male.name,
            successful=True,
            day=current_day,
            male_ref=male,
        )
        reproduction.mating_contacts.append(contact)
        stimulation = self.ovulation_resolver.record_stimulation(female=female, male=male, amount=1, day=current_day)
        if male.name not in reproduction.potential_fathers:
            reproduction.potential_fathers.append(male.name)
        event = (
            CatMatingContactRecordedEvent(
                contact=contact,
                potential_fathers=tuple(
                    reproduction
                    .potential_fathers
                ),
                ovulation_stimulation=(
                    stimulation[
                        "stimulation"
                    ]
                ),
                ovulation_threshold=(
                    stimulation[
                        "threshold"
                    ]
                ),
                ovulation_threshold_reached=(
                    stimulation[
                        "threshold_reached"
                    ]
                ),
            )
        )

        self._record_history_event(
            event
        )

        return event.to_dict()

    def _record_history_event(
        self,
        event
    ):
        if not isinstance(
            event,
            CatMatingHistoryEvent
        ):
            raise TypeError(
                "Cat mating history requires "
                "a CatMatingHistoryEvent object."
            )

        self.history.append(
            event
        )

        return event

    def close_mating_window(self, female, current_day=0, gestation_days=None, embryo_count=None, rng=None):
        biology = self.biology_gate.require_physical_world(operation='close_cat_mating_window', cat=female)
        if not biology['allowed']:
            return biology
        reproduction = female.reproduction
        if reproduction.pregnant:
            raise ValueError('Cat is already pregnant.')
        if not reproduction.mating_window_open:
            raise ValueError('Cat has no open mating window.')
        contacts = reproduction.mating_contacts
        if not contacts:
            raise ValueError('Ovulation requires at least one successful mating contact.')
        ovulation = (
            self.ovulation_resolver.resolve(
                female,
                day=current_day
            )
        )

        ovulation_event = (
            self.ovulation_resolver
            .history[-1]
        )

        if not ovulation_event.ovulation_induced:
            reproduction.estrus_active = False
            reproduction.estrous_phase = 'interestrus'
            reproduction.estrous_cycle_day = 0
            reproduction.mating_window_open = False
            reproduction.mating_window_started_day = None
            reproduction.mating_contacts = []
            reproduction.potential_fathers = []
            reproduction.pregnant = False
            reproduction.embryos = []

            event = (
                CatMatingWindowClosedWithoutOvulationEvent(
                    mother=female.name,
                    mating_contact_count=len(
                        contacts
                    ),
                    ovulation=(
                        ovulation_event
                    ),
                )
            )

            self._record_history_event(
                event
            )

            return event.to_dict()
        rng = rng or random
        gestation_days = CatReproduction.GESTATION_DAYS_DEFAULT if gestation_days is None else int(gestation_days)
        if not CatReproduction.GESTATION_DAYS_MIN <= gestation_days <= CatReproduction.GESTATION_DAYS_MAX:
            raise ValueError(f'Gestation days must be between {CatReproduction.GESTATION_DAYS_MIN} and {CatReproduction.GESTATION_DAYS_MAX}.')
        embryo_count = int(rng.randint(1, 6)) if embryo_count is None else int(embryo_count)
        if embryo_count < 1:
            raise ValueError('Embryo count must be at least one.')
        embryo_results = []
        paternity_results = []

        for _ in range(
            embryo_count
        ):
            paternity = (
                self.paternity_resolver
                .select_father(
                    mating_contacts=contacts,
                    rng=rng
                )
            )

            paternity_event = (
                self.paternity_resolver
                .history[-1]
            )

            father = paternity[
                "father"
            ]

            embryo_boundary = (
                self.embryo_resolver
                .create_embryo(
                    mother=female,
                    father=father,
                    rng=rng
                )
            )

            embryo_event = (
                self.embryo_resolver
                .history[-1]
            )

            embryo_result = (
                CatPregnancyEmbryoResult
                .from_boundary(
                    embryo_boundary,
                    embryo_event,
                )
            )

            embryo_results.append(
                embryo_result
            )

            paternity_results.append(
                CatPregnancyPaternityResult(
                    embryo_id=(
                        embryo_result
                        .embryo_id
                    ),
                    selection=(
                        paternity_event
                    ),
                )
            )

        viable_embryos = [
            result.embryo
            for result
            in embryo_results
            if result.viable
        ]

        current_day = int(
            current_day
        )

        father_names = []

        for result in (
            paternity_results
        ):
            father_name = (
                result.father
            )

            if (
                father_name
                not in father_names
            ):
                father_names.append(
                    father_name
                )

        reproduction.estrus_active = False
        reproduction.estrous_phase = 'diestrus'
        reproduction.estrous_cycle_day = 0
        reproduction.mating_window_open = False
        reproduction.pregnant = True
        reproduction.pregnancy_day = 0
        reproduction.gestation_days = gestation_days
        reproduction.expected_birth_day = (
            current_day
            + gestation_days
        )
        reproduction.mother_name = female.name
        reproduction.father_name = (
            father_names[0]
            if len(father_names) == 1
            else None
        )
        reproduction.father_names = (
            father_names
        )
        reproduction.embryos = (
            viable_embryos
        )

        event = (
            CatPregnancyStartedEvent(
                mother=female.name,
                ovulation=(
                    ovulation_event
                ),
                mating_contact_count=len(
                    contacts
                ),
                paternity_results=tuple(
                    paternity_results
                ),
                gestation_days=(
                    gestation_days
                ),
                started_on_day=(
                    current_day
                ),
                embryo_results=tuple(
                    embryo_results
                ),
            )
        )

        self._record_history_event(
            event
        )

        if hasattr(
            self.universe,
            'quantum_events'
        ):
            self.universe.quantum_events.append(
                event.to_dict()
            )

        return event.to_dict()

    def advance_pregnancy(self, female, days=1):
        biology = self.biology_gate.require_physical_world(operation='advance_cat_pregnancy', cat=female)
        if not biology['allowed']:
            return biology
        reproduction = female.reproduction
        if not reproduction.pregnant:
            return {'name': 'cat_pregnancy_advance_failed', 'reason': 'cat_is_not_pregnant', 'advanced': False}
        days = int(days)
        if days < 1:
            raise ValueError('Pregnancy advance must be at least one day.')
        reproduction.pregnancy_day += days
        ready_for_birth = reproduction.pregnancy_day >= reproduction.gestation_days
        event = {'name': 'cat_pregnancy_advanced', 'mother': female.name, 'days_advanced': days, 'pregnancy_day': reproduction.pregnancy_day, 'gestation_days': reproduction.gestation_days, 'ready_for_birth': ready_for_birth, 'advanced': True}
        self.history.append(event)
        return event

    @staticmethod
    def _validate_pair(female, male):
        if female is male:
            raise ValueError('A cat cannot mate with itself.')
        if not CatReproduction.can_become_pregnant(female):
            raise ValueError('Female cat cannot become pregnant.')
        if not CatReproduction.can_father_kittens(male):
            raise ValueError('Male cat cannot father kittens.')
