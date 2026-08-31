from copy import deepcopy
from cats.cat_social_objects import GarfieldTraining

class GarfieldTrainingSystem:
    LESSONS = ['choose_humans_carefully', 'invitation_means_responsibility', 'observe_before_MEOW', 'do_not_MEOW_every_idiot', 'when_uncertain_go_sleep_on_a_box']

    def assign(self, cat, incident=None):
        training = GarfieldTraining(**{'name': 'garfield_MEOW_responsibility_training', 'instructor': 'Garfield', 'cat': cat.name, 'lessons': list(self.LESSONS), 'incident': deepcopy(incident), 'required': True, 'completed': False})
        cat.meow_invitations.garfield_training_required = True
        cat.meow_invitations.garfield_training = training
        event = {'name': 'garfield_training_assigned', 'cat': cat.name, 'instructor': 'Garfield', 'required': True}
        cat.meow_invitations.history.append(deepcopy(event))
        return event

    def complete(self, cat):
        training = getattr(cat.meow_invitations, 'garfield_training', None)
        if not isinstance(training, GarfieldTraining):
            return {'name': 'garfield_training_not_required', 'cat': cat.name, 'completed': False}
        training.completed = True
        training.required = False
        cat.meow_invitations.garfield_training_required = False
        event = {'name': 'garfield_training_completed', 'cat': cat.name, 'instructor': 'Garfield', 'completed': True}
        cat.meow_invitations.history.append(deepcopy(event))
        return event


    def advise_emergency_lactation(
        self,
        cat,
        kittens
    ):
        state = cat.emergency_nursing

        kitten_names = [
            kitten.name
            for kitten in kittens
        ]

        state.garfield_consultations += 1

        event = {
            "name":
                "garfield_advised_emergency_lactation",
            "instructor":
                "Garfield",
            "cat":
                cat.name,
            "kittens":
                kitten_names,
            "advice": [
                "keep_the_kittens_warm",
                "nurse_them_frequently",
                "teach_them_as_they_grow",
                "do_not_replace_their_biological_history",
            ],
            "advised":
                True,
        }

        state.last_advice = deepcopy(
            event
        )

        cat.social_interactions.append(
            deepcopy(event)
        )

        return event
