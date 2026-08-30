class GodBook:

    def __init__(
        self,
        author
    ):
        self.type = "god_book"
        self.author = author

        self.title = None
        self.state = "being_written"

        self.energy_j = 0.0

        self.location = "with_author"
        self.library_status = None
        self.holder = None

        self.entries = []

    def shelve(
        self
    ):
        self.location = "library_shelf"
        self.library_status = "shelved"
        self.holder = None

    def check_out_for_edit(
        self,
        holder
    ):
        self.library_status = (
            "checked_out_for_edit"
        )
        self.holder = holder
        self.location = "with_god"

    def return_to_shelf(
        self
    ):
        self.shelve()

    def write_entry(
        self,
        entry
    ):
        self.entries.append(
            dict(entry)
        )

    def receive_energy(
        self,
        amount_j
    ):
        if amount_j <= 0.0:
            raise ValueError(
                "Book energy transfer must be positive."
            )

        self.energy_j += float(
            amount_j
        )

    def is_checked_out_by(
        self,
        holder
    ):
        return (
            self.library_status
            == "checked_out_for_edit"
            and self.holder is holder
        )

    def __repr__(
        self
    ):
        return (
            "<GodBook "
            f"author={self.author!r} "
            f"title={self.title!r} "
            f"state={self.state!r}>"
        )
