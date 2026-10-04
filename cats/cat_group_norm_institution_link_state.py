from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatNormInstitutionLinkDeniedResult:
    name: str = field(
        default="cat_norm_institution_link_denied",
        init=False,
    )

    linked: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatNormAttachedToInstitutionResult:
    group_id: str
    institution: str
    norm_id: str

    name: str = field(
        default="cat_norm_attached_to_institution",
        init=False,
    )

    linked: bool = field(
        default=True,
        init=False,
    )
