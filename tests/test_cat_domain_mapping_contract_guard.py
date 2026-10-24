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
    'cats/cats.py::Cats.public_state',
}


REAL_MAPPING_ALLOWLIST = {
    (
        'cats/feline_teacher_resolver.py'
        '::_freeze_feline_teacher_payload'
    ),
}


LEGACY_DOMAIN_DEBT = set()



def _contains_mapping_expression(
    node,
    local_mapping_names=None,
):
    if node is None:
        return False

    if local_mapping_names is None:
        local_mapping_names = set()

    if isinstance(
        node,
        (
            ast.Dict,
            ast.DictComp,
        ),
    ):
        return True

    if isinstance(
        node,
        ast.Name,
    ):
        return (
            node.id
            in local_mapping_names
        )

    if isinstance(
        node,
        ast.Call,
    ):
        if isinstance(
            node.func,
            ast.Name,
        ):
            call_name = (
                node.func.id
            )

            if call_name in {
                "dict",
                "vars",
                "MappingProxyType",
            }:
                return True

            if (
                call_name
                in {
                    "copy",
                    "deepcopy",
                }
                and node.args
            ):
                return (
                    _contains_mapping_expression(
                        node.args[0],
                        local_mapping_names,
                    )
                )

        if (
            isinstance(
                node.func,
                ast.Attribute,
            )
            and node.func.attr
            == "copy"
        ):
            return (
                _contains_mapping_expression(
                    node.func.value,
                    local_mapping_names,
                )
            )

        return False

    if isinstance(
        node,
        ast.IfExp,
    ):
        return (
            _contains_mapping_expression(
                node.body,
                local_mapping_names,
            )
            or
            _contains_mapping_expression(
                node.orelse,
                local_mapping_names,
            )
        )

    if isinstance(
        node,
        ast.BoolOp,
    ):
        return any(
            _contains_mapping_expression(
                value,
                local_mapping_names,
            )
            for value
            in node.values
        )

    if isinstance(
        node,
        (
            ast.List,
            ast.Tuple,
            ast.Set,
        ),
    ):
        return any(
            _contains_mapping_expression(
                element,
                local_mapping_names,
            )
            for element
            in node.elts
        )

    return False


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
    local_mapping_names = set()
    detected = False

    def assigned_names(
        assignment,
    ):
        if isinstance(
            assignment,
            ast.Assign,
        ):
            targets = (
                assignment.targets
            )

        elif isinstance(
            assignment,
            ast.AnnAssign,
        ):
            targets = (
                assignment.target,
            )

        else:
            return ()

        return tuple(
            target.id
            for target in targets
            if isinstance(
                target,
                ast.Name,
            )
        )

    def assignment_value(
        assignment,
    ):
        if isinstance(
            assignment,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            return assignment.value

        return None

    assignments = [
        child
        for child in ast.walk(
            node
        )
        if isinstance(
            child,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        )
    ]

    changed = True

    while changed:
        changed = False

        for assignment in assignments:
            value = assignment_value(
                assignment
            )

            if value is None:
                continue

            if not (
                _contains_mapping_expression(
                    value,
                    local_mapping_names,
                )
            ):
                continue

            for name in assigned_names(
                assignment
            ):
                if (
                    name
                    not in local_mapping_names
                ):
                    local_mapping_names.add(
                        name
                    )
                    changed = True

    for assignment in assignments:
        names = assigned_names(
            assignment
        )

        if any(
            name in {
                "event",
                "result",
                "report",
            }
            for name in names
        ):
            value = assignment_value(
                assignment
            )

            if (
                value is not None
                and
                _contains_mapping_expression(
                    value,
                    local_mapping_names,
                )
            ):
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
                and
                _contains_mapping_expression(
                    child.value,
                    local_mapping_names,
                )
            ):
                detected = True

        if not isinstance(
            child,
            ast.Call,
        ):
            continue

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

        if call_name not in {
            "_record",
            "emit_event",
            "append",
        }:
            continue

        if any(
            _contains_mapping_expression(
                argument,
                local_mapping_names,
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


def _function_from_source(
    source,
):
    tree = ast.parse(
        source
    )

    return next(
        node
        for node in tree.body
        if isinstance(
            node,
            ast.FunctionDef,
        )
    )


class CatDomainMappingContractGuardTests(
    unittest.TestCase
):

    def test_detector_catches_mapping_factory_return(
        self,
    ):
        node = _function_from_source(
            """
def sample(value):
    return dict(value)
"""
        )

        self.assertTrue(
            _method_has_mapping_contract(
                node
            )
        )

    def test_detector_catches_dict_comprehension_return(
        self,
    ):
        node = _function_from_source(
            """
def sample(items):
    return {
        key: value
        for key, value in items
    }
"""
        )

        self.assertTrue(
            _method_has_mapping_contract(
                node
            )
        )

    def test_detector_catches_vars_return(
        self,
    ):
        node = _function_from_source(
            """
def sample(value):
    return vars(value)
"""
        )

        self.assertTrue(
            _method_has_mapping_contract(
                node
            )
        )

    def test_detector_catches_named_mapping_return(
        self,
    ):
        node = _function_from_source(
            """
def sample(value):
    snapshot = dict(value)
    return snapshot
"""
        )

        self.assertTrue(
            _method_has_mapping_contract(
                node
            )
        )

    def test_detector_catches_named_mapping_emit(
        self,
    ):
        node = _function_from_source(
            """
def sample(self):
    snapshot = {
        "name": "event"
    }
    self.emit_event(snapshot)
"""
        )

        self.assertTrue(
            _method_has_mapping_contract(
                node
            )
        )

    def test_detector_catches_mapping_copy_return(
        self,
    ):
        node = _function_from_source(
            """
def sample(value):
    snapshot = dict(value)
    detached = snapshot.copy()
    return detached
"""
        )

        self.assertTrue(
            _method_has_mapping_contract(
                node
            )
        )

    def test_detector_does_not_flag_mapping_inside_domain_result(
        self,
    ):
        node = _function_from_source(
            """
def sample(items):
    registry = dict(items)
    return DomainResult(
        registry=registry
    )
"""
        )

        self.assertFalse(
            _method_has_mapping_contract(
                node
            )
        )

    def test_detector_ignores_dict_payload_inside_domain_event(
        self,
    ):
        node = _function_from_source(
            """
def sample():
    event = DomainEvent(
        **{
            "name": "domain_event"
        }
    )
    return event
"""
        )

        self.assertFalse(
            _method_has_mapping_contract(
                node
            )
        )

    def test_detector_ignores_dict_keyword_inside_domain_result(
        self,
    ):
        node = _function_from_source(
            """
def sample():
    return DomainResult(
        metadata={
            "source": "test"
        }
    )
"""
        )

        self.assertFalse(
            _method_has_mapping_contract(
                node
            )
        )

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

    def test_real_mapping_allowlist_is_current(
        self,
    ):
        current = (
            _current_mapping_contracts()
        )

        stale = (
            REAL_MAPPING_ALLOWLIST
            - current
        )

        self.assertEqual(
            stale,
            set(),
            (
                "Real mapping contract was "
                "removed from production code but "
                "not from "
                "REAL_MAPPING_ALLOWLIST. "
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
