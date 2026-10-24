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
    'cats/feline_ability_resolver.py::FelineAbilityResolver._record',
    'cats/cat_door.py::CatDoor.public_state',
    'cats/cat_perception.py::CatEnvironmentObservedEvent.to_dict',
    'cats/cats.py::Cats.public_state',
    'cats/memory.py::CatMemory.public_state',
}


REAL_MAPPING_ALLOWLIST = set()


LEGACY_DOMAIN_DEBT = set()



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

    def test_boundary_mapping_allowlist_is_current(
        self,
    ):
        current = (
            _current_mapping_contracts()
        )

        stale = (
            BOUNDARY_MAPPING_ALLOWLIST
            - current
        )

        self.assertEqual(
            stale,
            set(),
            (
                "Boundary mapping contract was "
                "removed from production code but "
                "not from "
                "BOUNDARY_MAPPING_ALLOWLIST. "
                "Remove these entries from the "
                "guard: "
                f"{sorted(stale)}"
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
