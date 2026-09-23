from dataclasses import dataclass, field

@dataclass(slots=True, frozen=True)
class KittenFatherSelectedEvent:
    father: str
    successful_contact_count: int
    total_successful_contacts: int
    weighted_candidate_names: tuple[str, ...]
    name: str = field(
        default="kitten_father_selected",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "father",
            str(self.father),
        )
        object.__setattr__(
            self,
            "successful_contact_count",
            int(
                self.successful_contact_count
            ),
        )
        object.__setattr__(
            self,
            "total_successful_contacts",
            int(
                self.total_successful_contacts
            ),
        )
        object.__setattr__(
            self,
            "weighted_candidate_names",
            tuple(
                str(name)
                for name
                in self.weighted_candidate_names
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "father": self.father,
            "successful_contact_count": (
                self.successful_contact_count
            ),
            "total_successful_contacts": (
                self.total_successful_contacts
            ),
            "weighted_candidate_names": list(
                self.weighted_candidate_names
            ),
        }


class MultipleSirePaternityResolver:

    def __init__(self):
        self.history = []

    def select_father(self, mating_contacts, rng):
        successful_contacts = [contact for contact in mating_contacts if contact.get('successful', False) and contact.get('_male_ref') is not None]
        if not successful_contacts:
            raise ValueError('Paternity selection requires at least one successful contact.')
        weighted_fathers = [contact['_male_ref'] for contact in successful_contacts]
        father = rng.choice(weighted_fathers)
        father_name = father.name
        contact_count = sum((1 for contact in successful_contacts if contact['male_name'] == father_name))
        event = KittenFatherSelectedEvent(
            father=father_name,
            successful_contact_count=contact_count,
            total_successful_contacts=len(
                successful_contacts
            ),
            weighted_candidate_names=tuple(
                candidate.name
                for candidate in weighted_fathers
            ),
        )

        self.record_selection(
            event
        )

        return {
            'father': father,
            'event': event.to_dict(),
        }

    def record_selection(
        self,
        event,
    ):
        if not isinstance(
            event,
            KittenFatherSelectedEvent,
        ):
            raise TypeError(
                'Paternity history requires a '
                'KittenFatherSelectedEvent object.'
            )

        self.history.append(
            event
        )

        return event
