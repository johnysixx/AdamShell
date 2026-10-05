from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupMythVerificationDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_myth_verification_denied",
        init=False,
    )

    verified: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupMythVerificationResult:
    group_id: str
    myth_id: str
    verified: bool
    credibility: float

    name: str = field(
        default="cat_group_myth_verified",
        init=False,
    )
