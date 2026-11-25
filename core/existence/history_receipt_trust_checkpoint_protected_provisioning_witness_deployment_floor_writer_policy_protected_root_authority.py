"""Protected-root writer policy authority.

The independently trusted root is the authoritative security state.
No legacy durable-state or coordination database is required.

Lock order:

    protected root exclusive fence
        -> persistent policy transaction
            -> existing floor CAS backend

Root transitions remain committed if a later policy operation fails.

The in-memory reference root models this trust boundary. It does
not provide process durability, hardware protection or remote
backend authentication. All cooperating authorities must share
one independently trusted root backend.
"""

import hashlib
import json

from dataclasses import dataclass, field, replace

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root
    as root,
)

from core.existence import (
    history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_durable_high_water
    as durable,
)


persistent = durable.persistent
versioned = durable.versioned
remote = durable.remote

PolicyReference = durable.PolicyReference
PreparedPolicyPublication = durable.PreparedPolicyPublication
DurablePolicyHighWaterState = durable.DurablePolicyHighWaterState

ProtectedDeploymentIdentity = root.ProtectedDeploymentIdentity
ProtectedDurableRootState = root.ProtectedDurableRootState
ProtectedRootBackend = root.ProtectedRootBackend


def _configuration_sha256(pins, deployment_id):

    # Preserve the exact existing durable configuration commitment.
    # Do not inspect or create any legacy durable/fence databases.

    backend = pins.backend

    material = (
        durable._STORE_DOMAIN,
        deployment_id,
        pins.policy_id,
        pins.policy_public_key.hex(),
        pins.genesis_sha256,
        backend.floor_id,
        backend.subject_id,
        backend.authority_id,
        backend.witness_id,
        *(
            key.hex()
            for key in versioned._reserved_backend_keys(backend)
        ),
    )

    encoded = json.dumps(
        material,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True, init=False, eq=False)
class ProtectedDurableWriterPolicyAuthority:

    _pins: object = field(repr=False)
    _root: ProtectedRootBackend = field(repr=False)
    _identity: ProtectedDeploymentIdentity

    def __init__(self):
        raise ValueError("Use explicit protected bootstrap or open.")

    @classmethod
    def _construct(
        cls,
        *,
        path,
        backend,
        root_backend,
        expected_identity,
        expected_policy_id,
        expected_policy_public_key,
        expected_genesis_sha256,
    ):

        if cls is not ProtectedDurableWriterPolicyAuthority:
            raise ValueError("Expected canonical authority type.")

        if type(expected_identity) is not ProtectedDeploymentIdentity:
            raise ValueError("Expected externally pinned deployment identity.")

        if not isinstance(root_backend, ProtectedRootBackend):
            raise ValueError("Expected trusted protected root backend.")

        pins = persistent._make_pins(
            path=path,
            backend=backend,
            expected_policy_id=expected_policy_id,
            expected_policy_public_key=expected_policy_public_key,
            expected_genesis_sha256=expected_genesis_sha256,
        )

        if (
            _configuration_sha256(pins, expected_identity.deployment_id)
            != expected_identity.configuration_sha256
        ):
            raise ValueError("Protected deployment configuration mismatch.")

        if (
            type(root_backend.identity) is not ProtectedDeploymentIdentity
            or root_backend.identity != expected_identity
        ):
            raise ValueError("Protected backend identity mismatch.")

        instance = object.__new__(cls)

        object.__setattr__(instance, "_pins", pins)
        object.__setattr__(instance, "_root", root_backend)
        object.__setattr__(instance, "_identity", expected_identity)

        return instance

    @classmethod
    def bootstrap(
        cls,
        *,
        path,
        backend,
        root_backend,
        expected_identity,
        expected_policy_id,
        expected_policy_public_key,
        expected_genesis_sha256,
        initial_policy_reference,
    ):

        with durable._operation("protected bootstrap"):

            if type(initial_policy_reference) is not PolicyReference:
                raise ValueError("Expected trusted initial policy reference.")

            instance = cls._construct(
                path=path,
                backend=backend,
                root_backend=root_backend,
                expected_identity=expected_identity,
                expected_policy_id=expected_policy_id,
                expected_policy_public_key=expected_policy_public_key,
                expected_genesis_sha256=expected_genesis_sha256,
            )

            with root_backend.exclusive():

                instance._check_identity()

                with persistent._transaction(instance._pins) as connection:

                    history = persistent._load_history(
                        connection,
                        instance._pins,
                    )

                    current = durable._reference(history.current)

                    if current != initial_policy_reference:
                        raise ValueError("Trusted initial reference mismatch.")

                    initial = ProtectedDurableRootState(
                        identity=expected_identity,
                        revision=1,
                        durable_state=durable._stable(current),
                    )

                    result = root_backend.provision(state=initial)

                    if result != initial.reference():
                        raise ValueError("Protected provisioning receipt mismatch.")

                    if instance._read_root() != initial:
                        raise ValueError("Protected provisioning state mismatch.")

            return instance

    @classmethod
    def open(
        cls,
        *,
        path,
        backend,
        root_backend,
        expected_identity,
        expected_policy_id,
        expected_policy_public_key,
        expected_genesis_sha256,
    ):

        with durable._operation("protected open"):

            instance = cls._construct(
                path=path,
                backend=backend,
                root_backend=root_backend,
                expected_identity=expected_identity,
                expected_policy_id=expected_policy_id,
                expected_policy_public_key=expected_policy_public_key,
                expected_genesis_sha256=expected_genesis_sha256,
            )

            with root_backend.exclusive():

                state = instance._read_root()

                # Opening never provisions a missing root and never
                # automatically completes an unresolved publication.

                if state.durable_state.prepared is not None:
                    return instance

                with persistent._transaction(instance._pins) as connection:
                    instance._load_and_observe(connection, state)

            return instance

    def _check_identity(self):

        actual = self._root.identity

        if (
            type(actual) is not ProtectedDeploymentIdentity
            or actual != self._identity
        ):
            raise ValueError("Protected root identity changed.")

    def _parse_prepared(self, prepared):

        candidate = persistent._parse_policy(
            self._pins,
            prepared.signed_policy,
        )

        if (
            durable._reference(candidate) != prepared.candidate
            or candidate.previous_sha256 != prepared.predecessor.sha256
        ):
            raise ValueError("Protected prepared candidate mismatch.")

        return candidate

    def _read_root(self):

        self._check_identity()

        state = self._root.read()

        if type(state) is not ProtectedDurableRootState:
            raise ValueError("Expected canonical protected root state.")

        if state.identity != self._identity:
            raise ValueError("Protected root state identity mismatch.")

        current = state.durable_state

        if (
            current.anchor.epoch == 1
            and current.anchor.sha256 != self._pins.genesis_sha256
        ):
            raise ValueError("Protected genesis mismatch.")

        if current.prepared is not None:
            self._parse_prepared(current.prepared)

        return state

    def root_state(self):

        with durable._operation("protected state inspection"):
            with self._root.exclusive():
                return self._read_root()

    def _replace_root(self, expected, durable_state):

        replacement = replace(
            expected,
            revision=expected.revision + 1,
            durable_state=durable_state,
        )

        reference = replacement.reference()

        result = self._root.compare_and_set(
            expected=expected.reference(),
            replacement=replacement,
        )

        if (
            type(result) is not root.ProtectedRootReference
            or result != reference
        ):
            raise ValueError("Protected root transition receipt mismatch.")

        if self._read_root() != replacement:
            raise ValueError("Protected root transition state mismatch.")

        return replacement

    def _load_and_observe(self, connection, state):

        if state.durable_state.prepared is not None:
            raise ValueError("Explicit protected publication recovery required.")

        history = persistent._load_history(
            connection,
            self._pins,
            anchor=state.durable_state.anchor.pair(),
        )

        current = durable._reference(history.current)

        if current != state.durable_state.anchor:

            state = self._replace_root(
                state,
                durable._stable(current),
            )

        return history, state

    def current_policy_reference(self):

        with durable._operation("protected reference read"):

            with self._root.exclusive():

                state = self._read_root()

                with persistent._transaction(self._pins) as connection:

                    _, observed = self._load_and_observe(connection, state)

                    return observed.durable_state.anchor.pair()

    def retired_writer_keys(self):

        with durable._operation("protected retirement read"):

            with self._root.exclusive():

                state = self._read_root()

                with persistent._transaction(self._pins) as connection:

                    history, _ = self._load_and_observe(connection, state)

                    return tuple(sorted(history.retired))

    def publish_policy(self, *, signed_policy):

        with durable._operation("protected publication"):

            with self._root.exclusive():

                state = self._read_root()
                pins = self._pins

                if state.durable_state.prepared is not None:
                    raise ValueError("Recover existing preparation first.")

                with persistent._transaction(pins) as connection:

                    history, state = self._load_and_observe(
                        connection,
                        state,
                    )

                    candidate = persistent._parse_policy(
                        pins,
                        signed_policy,
                    )

                    persistent._validate_transition(
                        current=history.current,
                        candidate=candidate,
                        retired=history.retired,
                    )

                    prepared = PreparedPolicyPublication(
                        predecessor=state.durable_state.anchor,
                        candidate=durable._reference(candidate),
                        signed_policy=signed_policy,
                    )

                    # The authoritative root retains PREPARED before
                    # the policy database may commit any mutation.

                    pending = self._replace_root(
                        state,
                        DurablePolicyHighWaterState(
                            anchor=state.durable_state.anchor,
                            prepared=prepared,
                        ),
                    )

                    durable._append_policy(
                        connection,
                        pins,
                        history,
                        candidate,
                        signed_policy,
                    )

                # The policy transaction completed.
                # An exception above leaves PREPARED retained.

                finalized = self._replace_root(
                    pending,
                    durable._stable(prepared.candidate),
                )

                return finalized.durable_state.anchor.pair()

    def recover_publication(self):

        with durable._operation("protected publication recovery"):

            with self._root.exclusive():

                state = self._read_root()
                pins = self._pins
                prepared = state.durable_state.prepared

                with persistent._transaction(pins) as connection:

                    if prepared is None:

                        _, observed = self._load_and_observe(
                            connection,
                            state,
                        )

                        return observed.durable_state.anchor.pair()

                    history = persistent._load_history(
                        connection,
                        pins,
                        anchor=prepared.predecessor.pair(),
                    )

                    candidate = self._parse_prepared(prepared)
                    current = durable._reference(history.current)

                    if current == prepared.predecessor:

                        history = durable._append_policy(
                            connection,
                            pins,
                            history,
                            candidate,
                            prepared.signed_policy,
                        )

                    else:

                        history = persistent._load_history(
                            connection,
                            pins,
                            anchor=prepared.candidate.pair(),
                        )

                        rows = connection.execute(
                            "SELECT message, signature "
                            "FROM writer_policy_history "
                            "WHERE policy_epoch = ?",
                            (prepared.candidate.epoch,),
                        ).fetchall()

                        if rows != [prepared.signed_policy]:
                            raise ValueError(
                                "Exact protected candidate missing."
                            )

                    recovered_head = durable._reference(history.current)

                # Finalize the exact candidate first. A later
                # authenticated descendant is a separate revision.

                finalized = self._replace_root(
                    state,
                    durable._stable(prepared.candidate),
                )

                if recovered_head != prepared.candidate:

                    finalized = self._replace_root(
                        finalized,
                        durable._stable(recovered_head),
                    )

                return finalized.durable_state.anchor.pair()

    def exchange(self, request):

        with durable._operation("protected exchange"):

            document = remote._parse(
                request,
                maximum=versioned._MAX_WIRE_BYTES,
            )

            operation = document.get("operation")

            if operation in ("read", "lookup"):

                # Public signed recovery is independent of
                # root and policy availability.

                return (
                    persistent.SQLitePersistentWriterPolicyAuthority
                    ._public_read_or_lookup(self, document)
                )

            if set(document) != versioned._CAS_FIELDS:
                raise ValueError("Expected versioned writer CAS envelope.")

            with self._root.exclusive():

                state = self._read_root()

                if state.durable_state.prepared is not None:
                    raise ValueError("CAS blocked by protected preparation.")

                pins = self._pins

                with persistent._transaction(pins) as connection:

                    history, observed = self._load_and_observe(
                        connection,
                        state,
                    )

                    current = history.current

                    if (
                        observed.durable_state.anchor
                        != durable._reference(current)
                    ):
                        raise ValueError("Protected observation mismatch.")

                    # Observation remains committed even when
                    # authorization or the floor backend fails.

                    verifier = (
                        versioned.VersionedWriterPolicyAuthority
                        .from_signed_policy(
                            backend=pins.backend,
                            expected_policy_id=pins.policy_id,
                            expected_policy_public_key=pins.policy_public_key,
                            signed_policy=history.signed_current,
                            minimum_policy_epoch=current.epoch,
                            expected_policy_sha256=current.sha256,
                        )
                    )

                    response = verifier.exchange(request)

                return response


@dataclass(frozen=True, slots=True, eq=False)
class ProtectedDurableWriterPolicyGateway:

    _authority: ProtectedDurableWriterPolicyAuthority = field(repr=False)

    def __post_init__(self):

        authority = self._authority

        if (
            type(authority) is not ProtectedDurableWriterPolicyAuthority
            or not hasattr(authority, "_pins")
            or not hasattr(authority, "_root")
            or not hasattr(authority, "_identity")
        ):
            raise ValueError("Expected initialized protected authority.")

    @classmethod
    def from_authority(cls, *, authority):
        return cls(_authority=authority)

    def exchange(self, request):
        return self._authority.exchange(request)
