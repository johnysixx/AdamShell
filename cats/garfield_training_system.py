from copy import deepcopy


class GarfieldTrainingSystem:

    LESSONS = [
        "choose_humans_carefully",
        "invitation_means_responsibility",
        "observe_before_MEOW",
        "do_not_MEOW_every_idiot",
        "when_uncertain_go_sleep_on_a_box"
    ]

    def assign(
        self,
        cat,
        incident=None
    ):
        training = {
            "name": "garfield_MEOW_responsibility_training",
            "instructor": "Garfield",
            "cat": cat.name,
            "lessons": list(
                self.LESSONS
            ),
            "incident": deepcopy(
                incident
            ),
            "required": True,
            "completed": False
        }

        cat.meow_invitations[
            "garfield_training_required"
        ] = True

        cat.meow_invitations[
            "garfield_training"
        ] = training

        event = {
            "name": "garfield_training_assigned",
            "cat": cat.name,
            "instructor": "Garfield",
            "required": True
        }

        cat.meow_invitations[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        return event

    def complete(
        self,
        cat
    ):
        training = cat.meow_invitations.get(
            "garfield_training"
        )

        if not isinstance(
            training,
            dict
        ):
            return {
                "name": "garfield_training_not_required",
                "cat": cat.name,
                "completed": False
            }

        training[
            "completed"
        ] = True

        training[
            "required"
        ] = False

        cat.meow_invitations[
            "garfield_training_required"
        ] = False

        event = {
            "name": "garfield_training_completed",
            "cat": cat.name,
            "instructor": "Garfield",
            "completed": True
        }

        cat.meow_invitations[
            "history"
        ].append(
            deepcopy(
                event
            )
        )

        return event
