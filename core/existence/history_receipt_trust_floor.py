"""Persistent high-water mark for pinned receipt trust catalogs.

Protects ordinary restarts and concurrent publishers, not against
an attacker who can restore or replace the database file.
Verification must explicitly require the current catalog.
"""

import hashlib
import hmac
import json
import os
import re
import sqlite3

from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from core.existence.history_receipt_proof import (
    ProviderReceiptTrustLifecycle,
)


_CATALOG_DOMAIN = b"adam-shell/a44/provider-trust-catalog/v1\x00"
_SOURCE_DOMAIN = b"adam-shell/a44/provider-sources/v1\x00"
_HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")

_SCHEMA = """
CREATE TABLE trust_floor (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    revision INTEGER NOT NULL CHECK (revision >= 1),
    source_ids_digest TEXT NOT NULL,
    catalog_digest TEXT NOT NULL
)
"""


def _catalog_fingerprints(lifecycle):
    """Fingerprint the validated policy without persisting secrets."""

    if type(lifecycle) is not ProviderReceiptTrustLifecycle:
        raise ValueError(
            "Expected validated provider trust lifecycle."
        )

    providers = []

    for source_id, ring in sorted(lifecycle.registry.providers):
        providers.append({
            "source_id": source_id,
            "legacy_key_id": ring.legacy_key_id,
            "keys": [
                {
                    "key_id": key.key_id,
                    "secret_hex": key.secret.hex(),
                    "status": key.status.value,
                }
                for key in sorted(
                    ring.keys,
                    key=lambda item: item.key_id,
                )
            ],
        })

    sources_canonical = json.dumps(
        sorted(lifecycle.expected_source_ids),
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")

    sources_digest = hashlib.sha256(
        _SOURCE_DOMAIN + sources_canonical
    ).hexdigest()

    canonical = json.dumps(
        {
            "expected_source_ids": sorted(
                lifecycle.expected_source_ids
            ),
            "providers": providers,
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")

    catalog_digest = hashlib.sha256(
        _CATALOG_DOMAIN + canonical
    ).hexdigest()

    return sources_digest, catalog_digest


def _read_floor(connection):
    rows = connection.execute(
        "SELECT singleton_id, revision, "
        "source_ids_digest, catalog_digest "
        "FROM trust_floor"
    ).fetchall()

    if len(rows) != 1:
        raise ValueError(
            "Missing or ambiguous durable trust floor."
        )

    singleton_id, revision, sources_digest, digest = rows[0]

    if (
        type(singleton_id) is not int
        or singleton_id != 1
        or type(revision) is not int
        or revision < 1
        or type(sources_digest) is not str
        or _HEX_SHA256.fullmatch(sources_digest) is None
        or type(digest) is not str
        or _HEX_SHA256.fullmatch(digest) is None
    ):
        raise ValueError("Malformed durable trust floor.")

    return revision, sources_digest, digest


@dataclass(frozen=True, slots=True)
class DurableProviderReceiptTrustFloor:
    """SQLite-backed revision and catalog-identity high-water mark."""

    _path: Path

    def _connect(self, *, readonly):
        try:
            path_uri = self._path.resolve(strict=True).as_uri()
            mode = "ro" if readonly else "rw"

            return sqlite3.connect(
                f"{path_uri}?mode={mode}",
                uri=True,
                isolation_level=None,
                timeout=10.0,
            )

        except (OSError, sqlite3.Error) as exc:
            raise ValueError(
                "Durable trust floor is unavailable."
            ) from exc

    @classmethod
    def bootstrap(cls, path, lifecycle):
        sources_digest, digest = _catalog_fingerprints(
            lifecycle
        )

        target = Path(path)

        # Exclusive creation prevents accidental reinitialization.
        try:
            fd = os.open(
                target,
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
            )

        except OSError as exc:
            raise ValueError(
                "Trust floor already exists or cannot be initialized."
            ) from exc

        else:
            os.close(fd)

        store = cls(target)

        try:
            with closing(
                store._connect(readonly=False)
            ) as connection:

                connection.execute("BEGIN IMMEDIATE")

                try:
                    connection.execute(_SCHEMA)

                    connection.execute(
                        "INSERT INTO trust_floor "
                        "(singleton_id, revision, "
                        "source_ids_digest, catalog_digest) "
                        "VALUES (1, ?, ?, ?)",
                        (
                            lifecycle.revision,
                            sources_digest,
                            digest,
                        ),
                    )

                    connection.commit()

                except BaseException:
                    connection.rollback()
                    raise

        except sqlite3.Error as exc:
            raise ValueError(
                "Failed to initialize durable trust floor."
            ) from exc

        return store

    @classmethod
    def open(cls, path):
        store = cls(Path(path))
        store._read_current()
        return store

    def _read_current(self):
        try:
            with closing(
                self._connect(readonly=True)
            ) as connection:
                return _read_floor(connection)

        except sqlite3.Error as exc:
            raise ValueError(
                "Invalid durable trust floor database."
            ) from exc

    def current_revision(self):
        return self._read_current()[0]

    def require_current(self, lifecycle):
        sources_digest, digest = _catalog_fingerprints(
            lifecycle
        )

        revision, stored_sources, current_digest = (
            self._read_current()
        )

        if (
            lifecycle.revision != revision
            or not hmac.compare_digest(
                sources_digest, stored_sources
            )
            or not hmac.compare_digest(
                digest, current_digest
            )
        ):
            raise ValueError(
                "Catalog is not the current durable trust state."
            )

    def publish(self, lifecycle):
        sources_digest, digest = _catalog_fingerprints(
            lifecycle
        )

        try:
            with closing(
                self._connect(readonly=False)
            ) as connection:

                # Serialize writers before reading current revision.
                connection.execute("BEGIN IMMEDIATE")

                try:
                    revision, stored_sources, _ = _read_floor(
                        connection
                    )

                    if not hmac.compare_digest(
                        sources_digest, stored_sources
                    ):
                        raise ValueError(
                            "Pinned provider identities cannot change."
                        )

                    if lifecycle.revision <= revision:
                        raise ValueError(
                            "Catalog revision must exceed durable trust floor."
                        )

                    cursor = connection.execute(
                        "UPDATE trust_floor "
                        "SET revision=?, catalog_digest=? "
                        "WHERE singleton_id=1 AND revision=?",
                        (
                            lifecycle.revision,
                            digest,
                            revision,
                        ),
                    )

                    if cursor.rowcount != 1:
                        raise ValueError(
                            "Concurrent trust-floor update detected."
                        )

                    connection.commit()

                except BaseException:
                    connection.rollback()
                    raise

        except sqlite3.Error as exc:
            raise ValueError(
                "Failed to publish durable trust floor."
            ) from exc
