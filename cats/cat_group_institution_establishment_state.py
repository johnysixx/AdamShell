from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupInstitutionEstablishedEvent:
    group_id: str
    institution: str
    purpose: str

    name: str = field(
        default="cat_group_institution_established",
        init=False,
    )

    established: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "group_id": self.group_id,
            "institution": self.institution,
            "purpose": self.purpose,
            "established": self.established,
        }
