class CatD20Adapter:

    def __init__(self, meeting_place):
        self.name = "cat_d20"
        self.type = "d20_artifact"
        self.location = "meeting_place"
        self.meeting_place = meeting_place

    def roll(self, rng=None):
        return (
            self.meeting_place
            .turn_cat_d20_in_box(
                rng=rng
            )
        )