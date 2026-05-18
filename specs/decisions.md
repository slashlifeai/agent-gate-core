# Agent Gate Core Decisions

## Current Decisions

### Keep Core As Evidence Normalizer And Reducer

Decision: Agent Gate Core consumes existing runtime and audit evidence; it does not become a policy engine or a new execution runtime.

Rationale: a small deterministic core is easier to audit publicly and easier for incident replay runtimes to depend on.

Consequence: policy enforcement remains upstream. Core only normalizes evidence and reduces results into verdicts.

### Fail Closed On Invalid Evidence

Decision: `agent-gate-decide` emits `FAIL` for missing files, invalid JSON, invalid schema, missing execution evidence, invalid audit evidence, or CRITICAL policy violations.

Rationale: procurement and incident replay use cases should not pass when evidence is absent or malformed.

Consequence: downstream runtimes must produce complete normalized evidence before claiming a PASS.

### Reserve Real Signing For A Later Provenance Layer

Decision: the current demo signature is content-bound and shaped like an Ed25519 signature placeholder, but not a production private-key signature.

Rationale: the v0 core needs stable canonical bytes and clear output now, while production provenance can replace the placeholder later.

Consequence: docs must not represent the v0 signature as cryptographic identity proof.

## Pending Decisions

- Package format for public distribution.
- Whether CLI names remain scripts or become installed console entrypoints.
- JSON schema publication format.
- Production signing/provenance model.
