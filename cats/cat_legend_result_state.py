from dataclasses import (
    dataclass,
    field,
)

from core.entity.components import (
    SpatialVector3,
)
from cats.cat_social_objects import (
    CatLegend,
    CatRelationshipTrustEvent,
)
from cats.cat_knowledge_objects import (
    CatHeardLegend,
)


@dataclass(
    slots=True,
    frozen=True,
)
class CatLegendSelectionResult:

    selected: bool
    storyteller: str
    listener: str
    legend: CatLegend | None = None
    candidate_count: int = 0
    reason: str | None = None

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "selected",
            bool(
                self.selected
            ),
        )

        object.__setattr__(
            self,
            "candidate_count",
            int(
                self.candidate_count
            ),
        )

        if (
            self.selected
            and not isinstance(
                self.legend,
                CatLegend,
            )
        ):
            raise TypeError(
                "Selected cat legend must be "
                "CatLegend."
            )


@dataclass(
    slots=True,
    frozen=True,
)
class CatLegendSharingEvaluationResult:

    share: bool
    score: float
    trust_in_listener: float
    information_value: float
    reasons: tuple[str, ...]

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "share",
            bool(
                self.share
            ),
        )

        object.__setattr__(
            self,
            "score",
            float(
                self.score
            ),
        )

        object.__setattr__(
            self,
            "trust_in_listener",
            float(
                self.trust_in_listener
            ),
        )

        object.__setattr__(
            self,
            "information_value",
            float(
                self.information_value
            ),
        )

        object.__setattr__(
            self,
            "reasons",
            tuple(
                self.reasons
            ),
        )


@dataclass(
    slots=True,
    frozen=True,
)
class CatLegendNotSharedResult:

    storyteller: str
    listener: str
    reason: str
    legend_id: object = None
    evaluation: (
        CatLegendSharingEvaluationResult
        | None
    ) = None

    name: str = field(
        default="cat_legend_not_shared",
        init=False,
    )

    shared: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(
        self,
    ):
        if (
            self.evaluation
            is not None
            and not isinstance(
                self.evaluation,
                CatLegendSharingEvaluationResult,
            )
        ):
            raise TypeError(
                "Cat legend sharing evaluation "
                "must be "
                "CatLegendSharingEvaluationResult."
            )


@dataclass(
    slots=True,
    frozen=True,
)
class CatLegendSharedEvent:

    storyteller: str
    listener: str
    legend_id: object
    layer: object
    position: SpatialVector3 | None
    evaluation: (
        CatLegendSharingEvaluationResult
    )
    heard_legend: CatHeardLegend

    name: str = field(
        default="cat_shared_legend",
        init=False,
    )

    shared: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.evaluation,
            CatLegendSharingEvaluationResult,
        ):
            raise TypeError(
                "Cat legend sharing evaluation "
                "must be "
                "CatLegendSharingEvaluationResult."
            )

        if not isinstance(
            self.heard_legend,
            CatHeardLegend,
        ):
            raise TypeError(
                "Shared legend heard state must be "
                "CatHeardLegend."
            )

        if (
            self.position
            is not None
            and not isinstance(
                self.position,
                SpatialVector3,
            )
        ):
            raise TypeError(
                "Shared legend position must be "
                "SpatialVector3 or None."
            )


CAT_LEGEND_SHARE_RESULT_TYPES = (
    CatLegendNotSharedResult,
    CatLegendSharedEvent,
)


@dataclass(
    slots=True,
    frozen=True,
)
class CatLegendContradictionResult:

    contradicted: bool
    legend_id: object
    reason: str | None = None
    storyteller: str | None = None
    trust_change: (
        CatRelationshipTrustEvent
        | None
    ) = None

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "contradicted",
            bool(
                self.contradicted
            ),
        )

        if (
            self.trust_change
            is not None
            and not isinstance(
                self.trust_change,
                CatRelationshipTrustEvent,
            )
        ):
            raise TypeError(
                "Legend contradiction trust change "
                "must be "
                "CatRelationshipTrustEvent."
            )


@dataclass(
    slots=True,
    frozen=True,
)
class CatLegendIntentionExecutionFailedResult:

    cat: str
    reason: str
    listener: str | None = None

    name: str = field(
        default="cat_legend_not_shared",
        init=False,
    )

    executed: bool = field(
        default=False,
        init=False,
    )

    shared: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatLegendIntentionExecutedEvent:

    cat: str
    legend_result: object
    intention: str = (
        "share_legend"
    )
    decision_source: str = (
        "cat_mind"
    )

    executed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.legend_result,
            CAT_LEGEND_SHARE_RESULT_TYPES,
        ):
            raise TypeError(
                "Legend intention result must be "
                "a cat legend share result object."
            )

    @property
    def name(
        self,
    ):
        return (
            self.legend_result.name
        )

    @property
    def shared(
        self,
    ):
        return (
            self.legend_result.shared
        )

    @property
    def storyteller(
        self,
    ):
        return (
            self.legend_result.storyteller
        )

    @property
    def listener(
        self,
    ):
        return (
            self.legend_result.listener
        )

    @property
    def legend_id(
        self,
    ):
        return getattr(
            self.legend_result,
            "legend_id",
            None,
        )

    @property
    def reason(
        self,
    ):
        return getattr(
            self.legend_result,
            "reason",
            None,
        )

    @property
    def evaluation(
        self,
    ):
        return getattr(
            self.legend_result,
            "evaluation",
            None,
        )
