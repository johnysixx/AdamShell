# A34: Deploying the independent signed witness authority

A33 authenticates **evidence**, not storage. A34 adds a real HTTPS authority
backed by transactional SQLite. It is **optional** and does not change existing
symbolic replay APIs. All authority operations still require an explicit
operator-provisioned universe + immutable outbox batch digest.

## Trust boundary

Deploy the authority as its own process on a **different host/storage and
backup/rollback domain** from the AdamShell inbox/outbox/bootstrap checkpoints.
Never use a database file copied into the local checkpoint directory. Put the
Ed25519 private signing key and write token only on the authority host, outside
the Git repository, with OS-restricted permissions. Never commit either file.

The authority uses SQLite WAL, FULL synchronous commits and serialized
BEGIN IMMEDIATE compare-and-swap updates, then signs the committed result.
Its read endpoint performs a fresh SQLite read. Hardware, filesystem, hosting,
backups and operations must honor these durability assumptions. HTTPS is
mandatory for the client. A private-key compromise or a dishonest signer
can still issue misleading signed responses. Authenticated responses do not
themselves prove freshness or an atomic local/remote transaction.

This is a reference service, **not a hardened public internet endpoint**:
operate behind firewall/rate limits, monitor it, use OS/service supervision,
backups, credential rotation procedures, and approved TLS certificates.

## Installation (authority host)

Install `cryptography` from `requirements-witness-auth.txt`. Use a
separate, protected directory (illustrative path `/srv/adam-witness`).

Generate the Ed25519 signing key, public raw key and random write token,
refusing to overwrite any existing file:

```sh
python -m universe.symbolic_replay_witness_server_cli generate-key \
  --private /srv/adam-witness/signing.pem \
  --public /srv/adam-witness/public.raw \
  --token-file /srv/adam-witness/write-token.txt
```

Provision an immutable batch **before the first witness delivery**. Use the
actual universe ID and 64-character `SymbolicReplayOutboxStore.lineage_digest`
from the canonical outbox, not a placeholder:

```sh
python -m universe.symbolic_replay_witness_server_cli provision \
  --db /srv/adam-witness/authority.sqlite \
  --universe-id YOUR_UNIVERSE_ID --batch-sha256 YOUR_64_CHAR_DIGEST
```

Provisioning the same universe + batch a second time is rejected; the HTTP
service exposes no scope-provisioning endpoint.

Use a trusted certificate whose SAN matches the host. Keep the separate
TLS private key outside the repository. Start the service with a process
supervisor. Default bind is localhost; configure explicit firewall rules if
it must listen remotely:

```sh
python -m universe.symbolic_replay_witness_server_cli serve \
  --db /srv/adam-witness/authority.sqlite \
  --signing-key /srv/adam-witness/signing.pem \
  --token-file /srv/adam-witness/write-token.txt \
  --tls-cert /srv/adam-witness/tls-cert.pem \
  --tls-key /srv/adam-witness/tls-key.pem \
  --host 127.0.0.1 --port 8443
```

The authority offers `POST /v1/read` (read a signed revision) and
`POST /v1/publish` (write-token-authenticated CAS). There is no HTTP
endpoint to generate keys, initialize scopes, or export secrets.

## Trusted client setup

Transfer the **public.raw** key out-of-band from the known operator.
Store a valid signed revision floor independently of the local checkpoint
files. On the authority host, the operator can export an exact signed floor
(repeat after advancing the authority and retain it outside the rollback
domain):

```sh
python -m universe.symbolic_replay_witness_server_cli export-floor \
  --db /srv/adam-witness/authority.sqlite \
  --signing-key /srv/adam-witness/signing.pem \
  --universe-id YOUR_UNIVERSE_ID \
  --batch-sha256 YOUR_64_CHAR_DIGEST > /secure-independent/floor.json
```

The client loads this floor from independently trusted storage, not from the
possibly rolled-back checkpoints. Its write token must also be provisioned
through a secret-management channel, never committed:

```python
from pathlib import Path
from universe.symbolic_replay_authenticated_witness import (
    AuthenticatedSymbolicReplayWitnessAuthority,
)
from universe.symbolic_replay_witness_https import HttpsSignedWitnessSource
from universe.symbolic_replay_witness_wire import signed_from_wire, loads_strict

source = HttpsSignedWitnessSource(
    "https://your-witness-host.example:8443",
    token=YOUR_SECRET_TOKEN_FROM_SECRET_MANAGER,
)
authority = AuthenticatedSymbolicReplayWitnessAuthority(
    source,
    public_key_bytes=Path(PINNED_PUBLIC_KEY_PATH).read_bytes(),
    trusted_signed_floor=signed_from_wire(
        loads_strict(Path(INDEPENDENT_FLOOR_PATH).read_bytes())
    ),
)
```

Now pass `authority` as the existing `witness_authority=` argument to
`SymbolicReplayWitnessDelivery` and `SymbolicReplayBootstrap.recover`.
Both verify the signed responses, and the A31 delivery path performs the
additional read-back before outbox ACK.

**Important:** The Ed25519 signature proves origin/integrity but not actual
durable publication by a malicious keyholder. A signed floor is only a useful
rollback bound if independently retained and sufficiently recent. The inbox
receipt and remote witness are still two separate writes; arbitrary external
side effects are **not exactly once** without receiver-side idempotency or
an external transaction.

## Verification

```sh
python -m pytest -q tests/test_symbolic_replay_witness_remote_authority.py
python -m pytest -q
```

The integration tests start a real localhost TLS service and use real SQLite
transactions, but cannot simulate a physical power loss or validate the
security of your eventual hosting environment.
