class MultipleSirePaternityResolver:

    def __init__(self):
        self.history = []

    def select_father(
        self,
        mating_contacts,
        rng
    ):
        successful_contacts = [
            contact
            for contact in mating_contacts
            if contact.get(
                "successful",
                False
            )
            and contact.get(
                "_male_ref"
            ) is not None
        ]

        if not successful_contacts:
            raise ValueError(
                "Paternity selection requires "
                "at least one successful contact."
            )

        weighted_fathers = [
            contact["_male_ref"]
            for contact in successful_contacts
        ]

        father = rng.choice(
            weighted_fathers
        )

        father_name = father[
            "name"
        ]

        contact_count = sum(
            1
            for contact in successful_contacts
            if contact["male_name"]
            == father_name
        )

        event = {
            "name": (
                "kitten_father_selected"
            ),
            "father": father_name,
            "successful_contact_count": (
                contact_count
            ),
            "total_successful_contacts": len(
                successful_contacts
            ),
            "weighted_candidate_names": [
                candidate["name"]
                for candidate in weighted_fathers
            ]
        }

        self.history.append(
            event
        )

        return {
            "father": father,
            "event": event
        }