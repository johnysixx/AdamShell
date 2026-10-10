from copy import deepcopy

from cats.cat_intention_state import (
    CatExplorationPairTarget,
)
from cats.cat_exploration_pair_execution_result_state import (
    CatAutonomousExplorationPairStartedEvent,
    CatExplorationPairCreationFailedResult,
    CatExplorationPairTransferFailedResult,
)
from quantum.cat_stable_exploration_pair_result_state import (
    CAT_STABLE_EXPLORATION_PAIR_CREATION_RESULT_TYPES,
    CatStableExplorationPairCreatedResult,
)
from quantum.cat_box_transfer_result_state import (
    CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
)


class CatExplorationPairIntentionHandler:

    def __init__(
        self,
        universe,
        recorder,
    ):
        self.universe = universe
        self._recorder = recorder

    def _record(
        self,
        event,
    ):
        return self._recorder(
            event
        )

    def execute(
        self,
        cat,
        intention,
    ):
        target = intention.target

        if not isinstance(
            target,
            CatExplorationPairTarget,
        ):
            return self._record(
                CatExplorationPairCreationFailedResult(
                    cat=cat.name,
                    reason=(
                        "invalid_exploration_pair_target"
                    ),
                )
            )

        destination_layer = (
            target.layer
        )

        destination_position = (
            target.position
        )

        if (
            destination_layer is None
            or destination_position is None
        ):
            return self._record(
                CatExplorationPairCreationFailedResult(
                    cat=cat.name,
                    reason=(
                        "missing_exploration_destination"
                    ),
                )
            )

        transfer_system = getattr(
            self.universe,
            "cat_box_transfer",
            None,
        )

        if transfer_system is None:
            return self._record(
                CatExplorationPairCreationFailedResult(
                    cat=cat.name,
                    reason=(
                        "cat_box_transfer_unavailable"
                    ),
                )
            )

        creation = (
            transfer_system
            .create_exploration_pair(
                cat=cat,
                destination_layer=
                    destination_layer,
                destination_position=
                    destination_position,
            )
        )

        if not isinstance(
            creation,
            CAT_STABLE_EXPLORATION_PAIR_CREATION_RESULT_TYPES,
        ):
            raise TypeError(
                "Stable exploration pair creation "
                "must return a creation result object."
            )

        if not creation.created:
            return self._record(
                CatExplorationPairCreationFailedResult(
                    cat=cat.name,
                    reason=creation.reason,
                    creation_result=creation,
                )
            )

        if not isinstance(
            creation,
            CatStableExplorationPairCreatedResult,
        ):
            raise TypeError(
                "Successful stable pair creation "
                "must return "
                "CatStableExplorationPairCreatedResult."
            )

        source_box = (
            creation.source_box
        )

        target_box = (
            creation.target_box
        )

        transfer = (
            transfer_system.transfer_cat(
                cat=cat,
                source_box_id=
                    source_box.id,
                target_box_id=
                    target_box.id,
            )
        )

        if not isinstance(
            transfer,
            CAT_QUANTUM_BOX_TRANSFER_RESULT_TYPES,
        ):
            raise TypeError(
                "Cat quantum box transfer must "
                "return a transfer result object."
            )

        if not transfer.transferred:
            cat.state = (
                "exploration_pair_created_"
                "but_transfer_failed"
            )

            return self._record(
                CatExplorationPairTransferFailedResult(
                    cat=cat.name,
                    pair_id=
                        creation.pair_id,
                    source_box_id=
                        source_box.id,
                    target_box_id=
                        target_box.id,
                    reason=getattr(
                        transfer,
                        "reason",
                        "stable_pair_transfer_failed",
                    ),
                    transfer_result=
                        transfer,
                    pair_preserved=True,
                )
            )

        exploration_route = None

        if (
            cat.current_layer
            == "quantum_layer"
        ):
            exploration_route = (
                transfer_system
                .start_quantum_exploration_route(
                    cat=cat,
                    pair_id=
                        creation.pair_id,
                )
            )

        mind = cat.mind

        mind.previous_intention = (
            deepcopy(
                intention
            )
        )

        mind.current_intention = None

        event = (
            CatAutonomousExplorationPairStartedEvent(
                cat=cat.name,
                pair_id=
                    creation.pair_id,
                source_box_id=
                    source_box.id,
                target_box_id=
                    target_box.id,
                source_layer=
                    creation.source_layer,
                target_layer=
                    creation.target_layer,
                energy_cost_j=
                    creation.energy_cost_j,
                remaining_cat_energy=(
                    creation
                    .remaining_cat_energy
                ),
                transfer=transfer,
                exploration_route=
                    exploration_route,
            )
        )

        mind.active_body_execution = (
            deepcopy(
                event
            )
        )

        return self._record(
            event
        )
