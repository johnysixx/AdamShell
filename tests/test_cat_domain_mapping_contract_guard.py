import ast
from pathlib import Path
import unittest


REPO_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

CATS_ROOT = (
    REPO_ROOT
    / "cats"
)


BOUNDARY_MAPPING_ALLOWLIST = {
    'cats/cat_bar_guidance_system.py::CatBarGuidanceAdmissionSnapshot.to_dict',
    'cats/cat_bar_guidance_system.py::CatGuidedHumanToBarEvent.to_dict',
    'cats/cat_birth_objects.py::CatLitter.to_dict',
    'cats/cat_birth_objects.py::_kitten_birth_result_snapshot',
    'cats/cat_birth_objects.py::cat_birth_profile_snapshot',
    'cats/cat_birth_objects.py::cat_phenotype_snapshot',
    'cats/cat_birth_objects.py::kitten_genetic_viability_snapshot',
    'cats/cat_door.py::CatDoor.public_state',
    'cats/cat_door_registry.py::CatDoorRegistry.public_state',
    'cats/cat_learning_state.py::CatFamilyKnowledgeState.to_dict',
    'cats/cat_learning_state.py::CatLearningState.to_dict',
    'cats/cat_learning_state.py::CatMeowKnowledgeState.to_dict',
    'cats/cat_learning_state.py::CatSkillState.to_dict',
    'cats/cat_memory_record.py::CatMemoryRecord.to_dict',
    'cats/cat_perception.py::CatEnvironmentObservedEvent.to_dict',
    'cats/cat_reproduction_state.py::CatReproductionState.to_dict',
    'cats/cat_reproduction_state.py::_kitten_embryo_snapshot',
    'cats/cat_reproduction_state.py::_mating_contact_snapshot',
    'cats/cat_social_objects.py::cat_group_knowledge_transmission_snapshot',
    'cats/cat_social_objects.py::cat_relationship_trust_event_snapshot',
    'cats/cats.py::Cats.public_state',
    'cats/cronenberg_encounter.py::CatCronenbergEncounter._origin_snapshot',
    'cats/cronenberg_encounter.py::CatCronenbergEncounter.public_state',
    'cats/development_resolver.py::CatAgeAdvancedEvent.to_dict',
    'cats/development_resolver.py::CatDevelopmentStageTransition.to_dict',
    'cats/development_resolver.py::NewbornCatDevelopmentInitializedEvent.to_dict',
    'cats/duplicate_consumption_energy.py::DuplicateConsumptionEnergyResolutionSkippedResult.to_dict',
    'cats/duplicate_consumption_energy.py::DuplicateConsumptionEnergyResolvedEvent.to_dict',
    'cats/duplicate_consumption_energy.py::DuplicateConsumptionEnergyStoredEvent.to_dict',
    'cats/feline_teacher_resolver.py::FelineAbilityLessonRequestedEvent.to_dict',
    'cats/feline_teacher_resolver.py::FelineAbilityTeacherChosenEvent.to_dict',
    'cats/feline_teacher_resolver.py::FelineAbilityTeacherNotFoundEvent.to_dict',
    'cats/feline_teacher_resolver.py::FelineAbilityTeacherSearchEvent.to_dict',
    'cats/feline_teacher_resolver.py::FelineTeacherCandidate.to_dict',
    'cats/feline_teacher_resolver.py::FelineTeacherMatch.to_dict',
    'cats/feline_wisdom_state.py::FelineAbilityAwarenessTransmissionDeniedResult.to_dict',
    'cats/feline_wisdom_state.py::FelineAbilityAwarenessTransmissionEvent.to_dict',
    'cats/feline_wisdom_state.py::FelineAbilityLessonDeniedResult.to_dict',
    'cats/feline_wisdom_state.py::FelineAbilityMethodLearnedEvent.to_dict',
    'cats/feline_wisdom_state.py::FelineAbilityTeachingCronenbergResult.to_dict',
    'cats/feline_wisdom_state.py::FelineTeachingAbilitiesRegistrationResult.to_dict',
    'cats/feline_wisdom_state.py::MeowFelineAwarenessTransmissionEvent.to_dict',
    'cats/feline_wisdom_state.py::_personality_experience_snapshot',
    'cats/feline_wisdom_state.py::_personality_trait_event_snapshot',
    'cats/kitten_embryo_resolver.py::NonviableKittenEmbryoReplacedByCronenbergEvent.to_dict',
    'cats/kitten_growth_state.py::KittenGrowthAlreadyProcessedEvent.to_dict',
    'cats/kitten_growth_state.py::KittenGrowthAppliedEvent.to_dict',
    'cats/mating_pregnancy_event.py::CatPregnancyStartedEvent.to_dict',
    'cats/mating_pregnancy_event.py::_induced_ovulation_snapshot',
    'cats/mating_pregnancy_event.py::_kitten_embryo_event_snapshot',
    'cats/mating_pregnancy_event.py::_kitten_embryo_result_snapshot',
    'cats/mating_pregnancy_event.py::_pregnancy_paternity_snapshot',
    'cats/memory.py::CatMemory.public_state',
    'cats/physical_biology_gate.py::PhysicalBiologyGateBlockedEvent.to_dict',
}


REAL_MAPPING_ALLOWLIST = {
    'cats/cat_birth_objects.py::CatBirthProfile.with_trait',
    'cats/cat_group_role_specialization_system.py::CatGroupRoleSpecializationSystem.specializations',
}


LEGACY_DOMAIN_DEBT = {
    'cats/cat.py::Cat.accept_pet',
    'cats/cat.py::Cat.meow_to',
    'cats/cat_bar_guidance_system.py::CatBarGuidanceSystem._failed',
    'cats/cat_birth_effect_resolver.py::CatBirthEffectResolver._emit_non_dice_effect',
    'cats/cat_birth_effect_resolver.py::CatBirthEffectResolver._execute_garfield_effects',
    'cats/cat_birth_effect_resolver.py::CatBirthEffectResolver._rotate_all_dice',
    'cats/cat_birth_effect_resolver.py::CatBirthEffectResolver.execute',
    'cats/cat_birth_resolver.py::CatBirthResolver.create_cat',
    'cats/cat_birth_resolver.py::CatBirthResolver.resolve_profile',
    'cats/cat_distribution_system.py::CatDistributionSystem.handle_after_milk',
    'cats/cat_group_sanction_system.py::CatGroupSanctionSystem.sanction',
    'cats/cat_intention_executor.py::CatIntentionExecutor._execute_approach_cat',
    'cats/cat_intention_executor.py::CatIntentionExecutor.execute_current_intention',
    'cats/cat_meow_invitation_system.py::CatMeowInvitationSystem.interpret',
    'cats/cat_meow_invitation_system.py::CatMeowInvitationSystem.offer',
    'cats/cat_mind.py::CatMind.clear_intention',
    'cats/cat_quantum_box_intention_handler.py::CatQuantumBoxIntentionHandler._advance_box_exploration',
    'cats/cat_quantum_box_intention_handler.py::CatQuantumBoxIntentionHandler._finish_box_exploration',
    'cats/cat_quantum_box_intention_handler.py::CatQuantumBoxIntentionHandler.explore',
    'cats/cat_quantum_box_intention_handler.py::CatQuantumBoxIntentionHandler.sense',
    'cats/cat_quantum_box_intention_handler.py::CatQuantumBoxIntentionHandler.travel',
    'cats/cats.py::Cats._cat_tick_error',
    'cats/cats.py::Cats._run_cat_tick_operation',
    'cats/cats.py::Cats._run_group_tick_operation',
    'cats/cats.py::Cats._tick_cat_autonomously',
    'cats/cats.py::Cats.think_and_act',
    'cats/cats.py::Cats.tick',
    'cats/duplicate_consumption_energy.py::DuplicateConsumptionEnergy._create_counterpart_or_fallback',
    'cats/duplicate_consumption_energy.py::DuplicateConsumptionEnergy._manifest_cronenberg',
    'cats/garfield_training_system.py::GarfieldTrainingSystem.assign',
    'cats/garfield_training_system.py::GarfieldTrainingSystem.complete',
}



def _contains_dict(
    node,
):
    return any(
        isinstance(
            child,
            ast.Dict,
        )
        for child
        in ast.walk(
            node
        )
    )


def _iter_functions(
    tree,
):
    def walk_body(
        body,
        parents=(),
    ):
        for node in body:
            if isinstance(
                node,
                ast.ClassDef,
            ):
                yield from walk_body(
                    node.body,
                    parents
                    + (
                        node.name,
                    ),
                )

            elif isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                qualname = ".".join(
                    parents
                    + (
                        node.name,
                    )
                )

                yield (
                    node,
                    qualname,
                )

    yield from walk_body(
        tree.body
    )


def _method_has_mapping_contract(
    node,
):
    local_dict_names = set()
    detected = False

    for child in ast.walk(
        node
    ):
        if (
            isinstance(
                child,
                ast.Assign,
            )
            and isinstance(
                child.value,
                ast.Dict,
            )
        ):
            for target in child.targets:
                if isinstance(
                    target,
                    ast.Name,
                ):
                    local_dict_names.add(
                        target.id
                    )

                    if target.id in {
                        "event",
                        "result",
                        "report",
                    }:
                        detected = True

    for child in ast.walk(
        node
    ):
        if isinstance(
            child,
            ast.Return,
        ):
            if (
                child.value is not None
                and _contains_dict(
                    child.value
                )
            ):
                detected = True

            if (
                isinstance(
                    child.value,
                    ast.Name,
                )
                and child.value.id
                in local_dict_names
            ):
                detected = True

        if isinstance(
            child,
            ast.Call,
        ):
            call_name = None

            if isinstance(
                child.func,
                ast.Attribute,
            ):
                call_name = (
                    child.func.attr
                )

            elif isinstance(
                child.func,
                ast.Name,
            ):
                call_name = (
                    child.func.id
                )

            if call_name in {
                "_record",
                "emit_event",
                "append",
            }:
                if any(
                    _contains_dict(
                        argument
                    )
                    for argument
                    in child.args
                ):
                    detected = True

    return detected


def _current_mapping_contracts():
    findings = set()

    for path in sorted(
        CATS_ROOT.rglob(
            "*.py"
        )
    ):
        source = path.read_text(
            encoding="utf-8-sig"
        )

        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

        relative_path = (
            path.relative_to(
                REPO_ROOT
            )
            .as_posix()
        )

        for (
            node,
            qualname,
        ) in _iter_functions(
            tree
        ):
            if (
                _method_has_mapping_contract(
                    node
                )
            ):
                findings.add(
                    f"{relative_path}"
                    f"::{qualname}"
                )

    return findings


class CatDomainMappingContractGuardTests(
    unittest.TestCase
):

    def test_no_unclassified_mapping_contracts(
        self,
    ):
        current = (
            _current_mapping_contracts()
        )

        classified = (
            BOUNDARY_MAPPING_ALLOWLIST
            | REAL_MAPPING_ALLOWLIST
            | LEGACY_DOMAIN_DEBT
        )

        unexpected = (
            current
            - classified
        )

        self.assertEqual(
            unexpected,
            set(),
            (
                "New unclassified cat-domain "
                "mapping contracts detected: "
                f"{sorted(unexpected)}"
            ),
        )

    def test_legacy_domain_debt_list_is_current(
        self,
    ):
        current = (
            _current_mapping_contracts()
        )

        stale = (
            LEGACY_DOMAIN_DEBT
            - current
        )

        self.assertEqual(
            stale,
            set(),
            (
                "Legacy mapping debt was removed "
                "from production code but not from "
                "LEGACY_DOMAIN_DEBT. Remove these "
                "entries from the guard: "
                f"{sorted(stale)}"
            ),
        )

    def test_boundary_and_real_mapping_contracts_are_not_debt(
        self,
    ):
        self.assertFalse(
            LEGACY_DOMAIN_DEBT
            & BOUNDARY_MAPPING_ALLOWLIST
        )

        self.assertFalse(
            LEGACY_DOMAIN_DEBT
            & REAL_MAPPING_ALLOWLIST
        )


if __name__ == "__main__":
    unittest.main()
