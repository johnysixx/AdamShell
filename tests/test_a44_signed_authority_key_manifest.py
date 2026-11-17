"""A44 signed authority-key provisioning contract.

The manifest is signed by an offline/bootstrap root.
Its raw root public key must be authenticated and supplied
through an independent trust channel.

The caller-provided root is NOT automatically trusted.
Minimum epoch must eventually come from a protected,
rollback-resistant state source.

All private keys in these tests are ephemeral.
"""

import dataclasses
import importlib
import json
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from core.existence import (
    history_receipt_trust_independent_authority_contract
    as contract,
)

from core.existence.history_receipt_trust_authority_evidence import (
    canonical_authority_reply_bytes,
)

from test_a44_independent_authority_contract import (
    AUTHORITY,
    make_intent,
    make_reply,
)


DOMAIN = "adam-shell.receipt-trust.authority-key-manifest"
VERSION = 1
ROOT_ID = "offline-bootstrap-root"


def api():
    return importlib.import_module(
        "core.existence."
        "history_receipt_trust_key_provisioning"
    )


def raw_public(private_key):
    return private_key.public_key().public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )


def entry(authority_id, public_key):
    return {
        "authority_id": authority_id,
        "public_key_hex": public_key.hex(),
    }


def manifest_bytes(
    entries,
    *,
    root_id=ROOT_ID,
    epoch=1,
    domain=DOMAIN,
    version=VERSION,
    extra=None,
):
    document = {
        "domain": domain,
        "version": version,
        "root_id": root_id,
        "epoch": epoch,
        "keys": entries,
    }

    if extra:
        document.update(extra)

    return json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def provision(
    root_private,
    message,
    *,
    signature=None,
    trusted_root_id=ROOT_ID,
    trusted_root_public_key=None,
    minimum_epoch=0,
):
    if signature is None:
        signature = root_private.sign(message)

    if trusted_root_public_key is None:
        trusted_root_public_key = raw_public(
            root_private
        )

    return api().VerifiedAuthorityKeyCatalog.from_signed_manifest(
        message,
        signature,
        trusted_root_id=trusted_root_id,
        trusted_root_public_key=trusted_root_public_key,
        minimum_epoch=minimum_epoch,
    )


def signed_authority_reply(private_key):
    intent = make_intent(contract)

    template = make_reply(
        contract,
        intent,
        prepared=False,
    )

    reply = dataclasses.replace(
        template,
        evidence=private_key.sign(
            canonical_authority_reply_bytes(template)
        ),
    )

    return intent, reply


class A44SignedAuthorityKeyManifestTests(unittest.TestCase):

    def test_valid_signed_manifest_builds_usable_verifier(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message = manifest_bytes([
            entry(AUTHORITY, raw_public(authority))
        ])

        catalog = provision(root, message)

        self.assertEqual(catalog.root_id, ROOT_ID)
        self.assertEqual(catalog.epoch, 1)
        self.assertEqual(
            catalog.pinned_keys,
            ((AUTHORITY, raw_public(authority)),),
        )

        verifier = catalog.make_verifier()

        _, reply = signed_authority_reply(authority)

        self.assertIs(
            verifier.verify_attestation(reply),
            True,
        )

        self.assertEqual(
            message,
            json.dumps(
                json.loads(message),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii"),
        )

    def test_wrong_root_key_and_root_identity_rejected(self):
        trusted = Ed25519PrivateKey.generate()
        unrelated = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message = manifest_bytes([
            entry(AUTHORITY, raw_public(authority))
        ])

        with self.assertRaises(ValueError):
            provision(
                trusted,
                message,
                trusted_root_public_key=raw_public(
                    unrelated
                ),
            )

        with self.assertRaises(ValueError):
            provision(
                trusted,
                message,
                trusted_root_id="another-root",
            )

    def test_forged_or_tampered_manifest_rejected(self):
        root = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message = manifest_bytes([
            entry(AUTHORITY, raw_public(authority))
        ])

        signature = root.sign(message)

        with self.assertRaises(ValueError):
            provision(
                root,
                message,
                signature=attacker.sign(message),
            )

        changed = manifest_bytes([
            entry(AUTHORITY, raw_public(attacker))
        ])

        with self.assertRaises(ValueError):
            provision(
                root,
                changed,
                signature=signature,
            )

        corrupted = (
            signature[:-1]
            + bytes([signature[-1] ^ 1])
        )

        with self.assertRaises(ValueError):
            provision(
                root,
                message,
                signature=corrupted,
            )

    def test_malformed_signature_and_root_inputs_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message = manifest_bytes([
            entry(AUTHORITY, raw_public(authority))
        ])

        signature = root.sign(message)

        for invalid in (
            b"",
            bytes(63),
            bytes(65),
            bytearray(signature),
            memoryview(signature),
            "not-a-signature",
            {},
        ):
            with self.subTest(signature=repr(invalid)):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        message,
                        signature=invalid,
                    )

        for key in (
            b"",
            bytes(31),
            bytes(33),
            bytearray(raw_public(root)),
            "text-public-key",
        ):
            with self.subTest(root_key=repr(key)):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        message,
                        signature=signature,
                        trusted_root_public_key=key,
                    )

        for value in (
            None,
            " root ",
            "",
            "bad" + chr(10) + "root",
        ):
            with self.subTest(root_id=repr(value)):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        message,
                        trusted_root_id=value,
                    )

    def test_noncanonical_and_duplicate_json_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        normal = manifest_bytes([
            entry(AUTHORITY, raw_public(authority))
        ])

        decoded = json.loads(normal)

        pretty = json.dumps(
            decoded,
            indent=2,
            sort_keys=True,
        ).encode("ascii")

        duplicate = normal.replace(
            b'"epoch":1',
            b'"epoch":1,"epoch":1',
            1,
        )

        self.assertNotEqual(duplicate, normal)

        for message in (
            pretty,
            normal + b"\n",
            b" " + normal,
            duplicate,
            b"\xef\xbb\xbf" + normal,
        ):
            with self.subTest(message=repr(message[:50])):
                with self.assertRaises(ValueError):
                    provision(root, message)

    def test_wrong_domain_version_and_embedded_root_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()
        keys = [entry(AUTHORITY, raw_public(authority))]

        invalid = (
            manifest_bytes(
                keys,
                domain="unrelated.protocol",
            ),
            manifest_bytes(
                keys,
                version=2,
            ),
            manifest_bytes(
                keys,
                version=True,
            ),
            manifest_bytes(
                keys,
                extra={"unexpected_field": "value"},
            ),
            manifest_bytes(
                keys,
                extra={
                    "root_public_key_hex":
                    raw_public(root).hex(),
                },
            ),
        )

        for message in invalid:
            with self.subTest(message=repr(message[:80])):
                with self.assertRaises(ValueError):
                    provision(root, message)

    def test_epoch_and_monotonic_floor_are_strict(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()
        keys = [entry(AUTHORITY, raw_public(authority))]

        message = manifest_bytes(
            keys,
            epoch=3,
        )

        catalog = provision(
            root,
            message,
            minimum_epoch=2,
        )

        self.assertEqual(catalog.epoch, 3)

        for floor in (3, 4, True, -1, 2.5, "2"):
            with self.subTest(floor=repr(floor)):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        message,
                        minimum_epoch=floor,
                    )

        for epoch in (0, -1, True, 1.5, "3"):
            with self.subTest(epoch=repr(epoch)):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        manifest_bytes(
                            keys,
                            epoch=epoch,
                        ),
                    )

    def test_keyset_must_be_nonempty_sorted_and_unique(self):
        root = Ed25519PrivateKey.generate()
        first = Ed25519PrivateKey.generate()
        second = Ed25519PrivateKey.generate()

        alpha = entry("authority-a", raw_public(first))
        omega = entry("authority-z", raw_public(second))

        valid = provision(
            root,
            manifest_bytes([alpha, omega]),
        )

        self.assertEqual(len(valid.pinned_keys), 2)

        invalid = (
            [],
            [omega, alpha],
            [alpha, alpha],
            [alpha, omega, alpha],
        )

        for entries in invalid:
            with self.subTest(entries=repr(entries)):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        manifest_bytes(entries),
                    )

    def test_malformed_authority_entries_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()
        key_hex = raw_public(authority).hex()

        invalid = (
            {"authority_id": "", "public_key_hex": key_hex},
            {"authority_id": " padded ", "public_key_hex": key_hex},
            {
                "authority_id": "bad" + chr(10) + "id",
                "public_key_hex": key_hex,
            },
            {"authority_id": "x" * 257, "public_key_hex": key_hex},
            {"authority_id": 17, "public_key_hex": key_hex},
            {"public_key_hex": key_hex},
            {
                "authority_id": AUTHORITY,
                "public_key_hex": key_hex,
                "extra": "unsupported",
            },
            [AUTHORITY, key_hex],
            None,
        )

        for value in invalid:
            with self.subTest(entry=repr(value)):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        manifest_bytes([value]),
                    )

    def test_invalid_public_key_encodings_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()
        key_hex = raw_public(authority).hex()

        invalid = (
            "",
            "not-hex",
            "0" * 63,
            "0" * 66,
            key_hex.upper() if any(
                ch in "abcdef" for ch in key_hex
            ) else "A" * 64,
            123,
            None,
            True,
        )

        for candidate in invalid:
            with self.subTest(key=repr(candidate)):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        manifest_bytes([{
                            "authority_id": AUTHORITY,
                            "public_key_hex": candidate,
                        }]),
                    )

    def test_rotation_requires_new_epoch_and_replaces_pins(self):
        root = Ed25519PrivateKey.generate()
        old_key = Ed25519PrivateKey.generate()
        new_key = Ed25519PrivateKey.generate()

        old_message = manifest_bytes(
            [entry(AUTHORITY, raw_public(old_key))],
            epoch=1,
        )

        new_message = manifest_bytes(
            [entry(AUTHORITY, raw_public(new_key))],
            epoch=2,
        )

        old_catalog = provision(
            root,
            old_message,
            minimum_epoch=0,
        )

        new_catalog = provision(
            root,
            new_message,
            minimum_epoch=1,
        )

        self.assertIs(type(new_catalog.pinned_keys), tuple)

        with self.assertRaises(AttributeError):
            new_catalog.pinned_keys = (
                (AUTHORITY, raw_public(old_key)),
            )

        _, old_reply = signed_authority_reply(old_key)
        _, new_reply = signed_authority_reply(new_key)

        self.assertIs(
            old_catalog.make_verifier().verify_attestation(
                old_reply
            ),
            True,
        )

        self.assertIs(
            new_catalog.make_verifier().verify_attestation(
                old_reply
            ),
            False,
        )

        self.assertIs(
            new_catalog.make_verifier().verify_attestation(
                new_reply
            ),
            True,
        )

        with self.assertRaises(ValueError):
            provision(
                root,
                old_message,
                minimum_epoch=1,
            )

        # The caller must provide a truly trusted floor.
        # This test does not establish durable revocation.

    def test_attacker_supplied_root_exposes_trust_boundary(self):
        approved_root = Ed25519PrivateKey.generate()
        attacker_root = Ed25519PrivateKey.generate()
        attacker_authority = Ed25519PrivateKey.generate()

        malicious_message = manifest_bytes([
            entry(
                AUTHORITY,
                raw_public(attacker_authority),
            )
        ])

        malicious_signature = attacker_root.sign(
            malicious_message
        )

        with self.assertRaises(ValueError):
            provision(
                approved_root,
                malicious_message,
                signature=malicious_signature,
            )

        attacker_catalog = provision(
            attacker_root,
            malicious_message,
            signature=malicious_signature,
        )

        _, forged_reply = signed_authority_reply(
            attacker_authority
        )

        self.assertIs(
            attacker_catalog.make_verifier().verify_attestation(
                forged_reply
            ),
            True,
        )

        # Expected observation:
        # A caller-controlled trust root is not secure
        # provisioning, even when signatures are valid.


class A44SignedManifestAdversarialTests(unittest.TestCase):

    def test_root_substitution_with_matching_identity(self):
        approved = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message = manifest_bytes([
            entry(AUTHORITY, raw_public(authority))
        ])

        forged_signature = attacker.sign(message)

        # An attacker may use the same root identity
        # string, but not the approved root private key.
        with self.assertRaises(ValueError):
            provision(
                approved,
                message,
                signature=forged_signature,
            )

        # Supplying the attacker's root as the
        # supposedly trusted root defeats provisioning.
        compromised = provision(
            attacker,
            message,
            signature=forged_signature,
        )

        self.assertEqual(compromised.root_id, ROOT_ID)
        self.assertEqual(compromised.epoch, 1)

    def test_authority_key_swap_without_resigning(self):
        root = Ed25519PrivateKey.generate()
        approved = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()

        original = manifest_bytes([
            entry(AUTHORITY, raw_public(approved))
        ])

        signature = root.sign(original)

        substituted = manifest_bytes([
            entry(AUTHORITY, raw_public(attacker))
        ])

        self.assertNotEqual(original, substituted)

        with self.assertRaises(ValueError):
            provision(
                root,
                substituted,
                signature=signature,
            )

        catalog = provision(
            root,
            original,
            signature=signature,
        )

        verifier = catalog.make_verifier()

        _, approved_reply = signed_authority_reply(
            approved
        )

        _, attacker_reply = signed_authority_reply(
            attacker
        )

        self.assertIs(
            verifier.verify_attestation(approved_reply),
            True,
        )

        self.assertIs(
            verifier.verify_attestation(attacker_reply),
            False,
        )

    def test_multiple_authorities_have_distinct_signatures(self):
        root = Ed25519PrivateKey.generate()
        first = Ed25519PrivateKey.generate()
        second = Ed25519PrivateKey.generate()

        second_id = AUTHORITY + "-secondary"

        entries = [
            entry(AUTHORITY, raw_public(first)),
            entry(second_id, raw_public(second)),
        ]

        catalog = provision(
            root,
            manifest_bytes(entries),
        )

        verifier = catalog.make_verifier()

        _, first_reply = signed_authority_reply(first)

        second_template = dataclasses.replace(
            first_reply,
            authority_id=second_id,
            evidence=b"",
        )

        second_reply = dataclasses.replace(
            second_template,
            evidence=second.sign(
                canonical_authority_reply_bytes(
                    second_template
                )
            ),
        )

        self.assertIs(
            verifier.verify_attestation(first_reply),
            True,
        )

        self.assertIs(
            verifier.verify_attestation(second_reply),
            True,
        )

        relabeled = dataclasses.replace(
            first_reply,
            authority_id=second_id,
        )

        self.assertIs(
            verifier.verify_attestation(relabeled),
            False,
        )

        swapped = dataclasses.replace(
            first_reply,
            evidence=second_reply.evidence,
        )

        self.assertIs(
            verifier.verify_attestation(swapped),
            False,
        )

    def test_signed_duplicate_json_properties_fail_closed(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        normal = manifest_bytes([
            entry(AUTHORITY, raw_public(authority))
        ])

        identity = (
            b'"authority_id":'
            + json.dumps(AUTHORITY).encode("ascii")
        )

        encoded_key = (
            b'"public_key_hex":'
            + json.dumps(
                raw_public(authority).hex()
            ).encode("ascii")
        )

        variants = (
            normal.replace(
                b'"epoch":1',
                b'"epoch":1,"epoch":1',
                1,
            ),
            normal.replace(
                identity,
                identity + b"," + identity,
                1,
            ),
            normal.replace(
                encoded_key,
                encoded_key + b"," + encoded_key,
                1,
            ),
        )

        for changed in variants:
            self.assertNotEqual(changed, normal)

            # These malformed messages have valid
            # cryptographic signatures from the root.
            # Parsing still has to reject them.
            with self.subTest(message=repr(changed[:90])):
                with self.assertRaises(ValueError):
                    provision(root, changed)

    def test_signed_noncanonical_and_malformed_json_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        normal = manifest_bytes([
            entry(AUTHORITY, raw_public(authority))
        ])

        variants = (
            b" " + normal,
            normal + b"\n",
            json.dumps(
                json.loads(normal),
                indent=2,
                sort_keys=True,
            ).encode("ascii"),
            normal.replace(
                b'"epoch":1',
                b'"epoch":NaN',
                1,
            ),
            normal.replace(
                b'"epoch":1',
                b'"epoch":Infinity',
                1,
            ),
            normal.replace(
                b'"version":1',
                b'"version":1.0',
                1,
            ),
            normal[:1] + b"\xff" + normal[1:],
        )

        for changed in variants:
            self.assertNotEqual(changed, normal)

            with self.subTest(message=repr(changed[:90])):
                with self.assertRaises(ValueError):
                    provision(root, changed)

    def test_manifest_size_and_catalog_count_limits(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        oversized = b"{" + b" " * 1_048_576 + b"}"

        with self.assertRaises(ValueError):
            provision(root, oversized)

        key = raw_public(authority)

        excessive_entries = [
            entry(f"authority-{i:04d}", key)
            for i in range(4097)
        ]

        large_manifest = manifest_bytes(
            excessive_entries
        )

        self.assertLessEqual(
            len(large_manifest),
            1_048_576,
        )

        with self.assertRaises(ValueError):
            provision(root, large_manifest)

        # The second case reaches the key-count
        # rule rather than the manifest-byte cap.

    def test_untrusted_container_and_signature_types_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message = manifest_bytes([
            entry(AUTHORITY, raw_public(authority))
        ])

        signature = root.sign(message)

        class BytesSubclass(bytes):
            pass

        invalid_messages = (
            None,
            "text",
            [],
            {},
            bytearray(message),
            memoryview(message),
            BytesSubclass(message),
        )

        for candidate in invalid_messages:
            with self.subTest(
                message_type=type(candidate).__name__
            ):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        candidate,
                        signature=signature,
                    )

        invalid_signatures = (
            bytearray(signature),
            memoryview(signature),
            BytesSubclass(signature),
        )

        for candidate in invalid_signatures:
            with self.subTest(
                signature_type=type(candidate).__name__
            ):
                with self.assertRaises(ValueError):
                    provision(
                        root,
                        message,
                        signature=candidate,
                    )

    def test_reduced_epoch_floor_reenables_old_manifest(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()
        keys = [
            entry(AUTHORITY, raw_public(authority))
        ]

        old_message = manifest_bytes(
            keys,
            epoch=1,
        )

        new_message = manifest_bytes(
            keys,
            epoch=2,
        )

        current = provision(
            root,
            new_message,
            minimum_epoch=1,
        )

        self.assertEqual(current.epoch, 2)

        with self.assertRaises(ValueError):
            provision(
                root,
                old_message,
                minimum_epoch=1,
            )

        # Documented vulnerability if the trusted
        # external high-water mark can be rolled back.
        replayed = provision(
            root,
            old_message,
            minimum_epoch=0,
        )

        self.assertEqual(replayed.epoch, 1)

    def test_direct_catalog_creation_is_not_provenance(self):
        attacker = Ed25519PrivateKey.generate()

        catalog = api().VerifiedAuthorityKeyCatalog(
            root_id=ROOT_ID,
            epoch=99,
            pinned_keys=(
                (AUTHORITY, raw_public(attacker)),
            ),
        )

        _, forged_reply = signed_authority_reply(
            attacker
        )

        self.assertIs(
            catalog.make_verifier().verify_attestation(
                forged_reply
            ),
            True,
        )

        with self.assertRaises(AttributeError):
            catalog.epoch = 100

        # Frozen dataclass fields do NOT establish
        # that a signed manifest was ever checked.
        # A future protected entrypoint must reject
        # caller-constructed catalogs as trust roots.

    def test_signed_structural_substitutions_rejected(self):
        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        valid_entry = entry(
            AUTHORITY,
            raw_public(authority),
        )

        invalid_messages = (
            manifest_bytes(
                "not-a-key-list",
            ),
            manifest_bytes(
                {"authority_id": AUTHORITY},
            ),
            manifest_bytes(
                [valid_entry],
                extra={
                    "root_public_key_hex":
                    raw_public(root).hex(),
                },
            ),
            manifest_bytes(
                [valid_entry],
                domain="other-manifest-domain",
            ),
            manifest_bytes(
                [{
                    **valid_entry,
                    "unrecognized": True,
                }],
            ),
            manifest_bytes(
                [valid_entry],
                version=1.0,
            ),
            manifest_bytes(
                [valid_entry],
                epoch=True,
            ),
        )

        for message in invalid_messages:
            with self.subTest(message=repr(message[:90])):
                with self.assertRaises(ValueError):
                    provision(root, message)


if __name__ == "__main__":
    unittest.main()
