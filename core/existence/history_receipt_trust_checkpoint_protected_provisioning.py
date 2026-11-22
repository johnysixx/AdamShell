"""A44 protected high-water provisioning binding.

Binds a caller-supplied trusted pin snapshot to a verified
signed enrollment manifest and a pinned high-water client.

SECURITY LIMITS:
- The caller must independently authenticate the pin source.
- An arbitrary Python source is not a protected trust root.
- The store signing key and trusted signer key are not provisioned here.
- Refresh is immutable and monotonic only relative to the
  previous binding retained by the caller.
- Discarding the binding can discard its previous minima.
- No durable storage, TPM, HSM or remote monotonic service.
- No cross-store atomicity, checkpoint repair or republication.
"""

from dataclasses import InitVar, dataclass

from core.existence.history_receipt_trust_checkpoint_anchor_trusted_enrollment import (
    TrustedSignedCheckpointAnchorEnrollment,
)

from core.existence.history_receipt_trust_checkpoint_protected_high_water import (
    PinnedSignedProtectedHighWaterClient,
)

from core.existence import (
    history_receipt_trust_checkpoint_protected_high_water
    as high_water
)


_FACTORY_TOKEN = object()


def _identity(value, label):
    return high_water._identity(value, label)


def _key(value, label):
    return high_water._key(value, label)


def _counter(value, label):
    return high_water._counter(value, label)


@dataclass(frozen=True, slots=True)
class TrustedProvisioningPins:
    """Immutable caller-supplied pins, not proof of a trusted source."""

    trusted_signer_id: str
    trusted_signer_public_key: bytes

    expected_anchor_id: str
    expected_authority_id: str
    expected_root_id: str

    expected_store_id: str
    expected_store_public_key: bytes

    minimum_enrollment_epoch: int
    minimum_revision: int
    minimum_generation: int
    minimum_fence_token: int

    provisioning_generation: int

    def __post_init__(self):
        for label, value in (
            ("trusted provisioning signer", self.trusted_signer_id),
            ("anchor", self.expected_anchor_id),
            ("authority", self.expected_authority_id),
            ("root", self.expected_root_id),
            ("high-water store", self.expected_store_id),
        ):
            _identity(value, label)

        for label, value in (
            (
                "trusted provisioning signer public key",
                self.trusted_signer_public_key,
            ),
            (
                "high-water store signing public key",
                self.expected_store_public_key,
            ),
        ):
            _key(value, label)

        for label, value in (
            (
                "minimum enrollment epoch",
                self.minimum_enrollment_epoch,
            ),
            (
                "minimum revision",
                self.minimum_revision,
            ),
            (
                "minimum generation",
                self.minimum_generation,
            ),
            (
                "minimum fencing token",
                self.minimum_fence_token,
            ),
            (
                "provisioning generation",
                self.provisioning_generation,
            ),
        ):
            _counter(value, label)


@dataclass(frozen=True, slots=True)
class PinnedHighWaterProvisioning:
    """Verified binding, not independent protection of pin origin."""

    source: object
    pins: TrustedProvisioningPins
    enrollment: TrustedSignedCheckpointAnchorEnrollment

    _factory_token: InitVar[object] = None

    def __post_init__(self, _factory_token):
        if _factory_token is not _FACTORY_TOKEN:
            raise ValueError(
                "Provisioning binding requires signed verification."
            )

        if type(self.pins) is not TrustedProvisioningPins:
            raise ValueError(
                "Expected canonical provisioning pins."
            )

        self.pins.__post_init__()

        if type(self.enrollment) is not (
            TrustedSignedCheckpointAnchorEnrollment
        ):
            raise ValueError(
                "Expected canonical verified enrollment."
            )

        self.enrollment._client_pins()

        if not callable(
            getattr(self.source, "read_pins", None)
        ):
            raise ValueError(
                "Trusted provisioning source reader unavailable."
            )

        pins = self.pins
        enrollment = self.enrollment

        if (
            enrollment.trusted_signer_id
            != pins.trusted_signer_id
            or enrollment.trusted_signer_public_key
            != pins.trusted_signer_public_key
            or enrollment.expected_anchor_id
            != pins.expected_anchor_id
            or enrollment.expected_authority_id
            != pins.expected_authority_id
            or enrollment.expected_root_id
            != pins.expected_root_id
        ):
            raise ValueError(
                "Provisioning binding identity mismatch."
            )

        if (
            enrollment.expected_enrollment_epoch
            < pins.minimum_enrollment_epoch
            or enrollment.minimum_revision
            < pins.minimum_revision
            or enrollment.minimum_generation
            < pins.minimum_generation
            or enrollment.minimum_fence_token
            < pins.minimum_fence_token
        ):
            raise ValueError(
                "Enrollment below trusted provisioning minima."
            )

    @classmethod
    def from_trusted_source(
        cls,
        *,
        source,
        manifest,
        signature,
    ):
        """Read one caller-trusted pin snapshot and verify manifest."""

        try:
            reader = getattr(
                source,
                "read_pins",
                None,
            )

            if not callable(reader):
                raise ValueError(
                    "Trusted provisioning source reader unavailable."
                )

            pins = reader()

            if type(pins) is not TrustedProvisioningPins:
                raise ValueError(
                    "Trusted source returned noncanonical pins."
                )

            pins.__post_init__()

            enrollment = (
                TrustedSignedCheckpointAnchorEnrollment
                .from_signed_manifest(
                    manifest=manifest,
                    signature=signature,
                    trusted_signer_id=(
                        pins.trusted_signer_id
                    ),
                    trusted_signer_public_key=(
                        pins.trusted_signer_public_key
                    ),
                    expected_anchor_id=(
                        pins.expected_anchor_id
                    ),
                    expected_authority_id=(
                        pins.expected_authority_id
                    ),
                    expected_root_id=(
                        pins.expected_root_id
                    ),
                    minimum_enrollment_epoch=(
                        pins.minimum_enrollment_epoch
                    ),
                    minimum_revision=(
                        pins.minimum_revision
                    ),
                    minimum_generation=(
                        pins.minimum_generation
                    ),
                    minimum_fence_token=(
                        pins.minimum_fence_token
                    ),
                )
            )

            return cls(
                source=source,
                pins=pins,
                enrollment=enrollment,
                _factory_token=_FACTORY_TOKEN,
            )

        except Exception as exc:
            raise ValueError(
                "Protected provisioning binding failed."
            ) from exc

    def high_water_client(self, provider):
        """Bind a provider exclusively to verified stored pins."""

        try:
            self.__post_init__(_FACTORY_TOKEN)

            return (
                PinnedSignedProtectedHighWaterClient
                .from_provider(
                    provider=provider,
                    enrollment=self.enrollment,
                    expected_store_id=(
                        self.pins.expected_store_id
                    ),
                    expected_store_public_key=(
                        self.pins.expected_store_public_key
                    ),
                    minimum_revision=(
                        self.enrollment.minimum_revision
                    ),
                    minimum_generation=(
                        self.enrollment.minimum_generation
                    ),
                    minimum_fence_token=(
                        self.enrollment.minimum_fence_token
                    ),
                )
            )

        except Exception as exc:
            raise ValueError(
                "Provisioned high-water client binding failed."
            ) from exc

    def refresh(
        self,
        *,
        manifest,
        signature,
    ):
        """Return a new binding, never rotate trust keys silently."""

        try:
            self.__post_init__(_FACTORY_TOKEN)

            candidate = type(self).from_trusted_source(
                source=self.source,
                manifest=manifest,
                signature=signature,
            )

            old = self.pins
            new = candidate.pins

            immutable_names = (
                "trusted_signer_id",
                "trusted_signer_public_key",
                "expected_anchor_id",
                "expected_authority_id",
                "expected_root_id",
                "expected_store_id",
                "expected_store_public_key",
            )

            if any(
                getattr(old, name) != getattr(new, name)
                for name in immutable_names
            ):
                raise ValueError(
                    "Provisioning trust identity or key changed."
                )

            monotonic_names = (
                "minimum_enrollment_epoch",
                "minimum_revision",
                "minimum_generation",
                "minimum_fence_token",
                "provisioning_generation",
            )

            if any(
                getattr(new, name) < getattr(old, name)
                for name in monotonic_names
            ):
                raise ValueError(
                    "Trusted provisioning snapshot rolled back."
                )

            if (
                new != old
                and new.provisioning_generation
                <= old.provisioning_generation
            ):
                raise ValueError(
                    "Changed provisioning pins require new generation."
                )

            prior = self.enrollment
            updated = candidate.enrollment

            if (
                updated.expected_enrollment_epoch
                < prior.expected_enrollment_epoch
                or updated.minimum_revision
                < prior.minimum_revision
                or updated.minimum_generation
                < prior.minimum_generation
                or updated.minimum_fence_token
                < prior.minimum_fence_token
            ):
                raise ValueError(
                    "Verified enrollment state rolled back."
                )

            return candidate

        except Exception as exc:
            raise ValueError(
                "Protected provisioning refresh rejected."
            ) from exc
