# Agent Gate Core Domain

## Ubiquitous Language

| Term | Definition |
|---|---|
| Gate result | A normalized `agent.gate.result.v0` JSON object containing execution and policy evidence for one node/tool run. |
| Policy result | A normalized JSON object containing policy violations derived from existing runtime or ledger events. |
| Verdict reducer | The deterministic logic that converts one or more gate results into PASS or FAIL. |
| Audit evidence | Execution evidence produced by an external audit runner and report flow. |
| Runtime event | Existing policy/runtime/ledger event material consumed by `agent-gate-policy-result`. |
| Replay consumer | A downstream project, such as `agent-gate-incident-replay`, that uses Agent Gate Core inside a larger replay runtime. |

## Domain Boundary

This repository owns: `agent.gate.result.v0`, `agent-gate-policy-result`, `agent-gate-run`, `agent-gate-decide`, deterministic verdict reducer behavior, fixture tests, evidence normalization contracts, and public examples for PASS/FAIL replay.

This repository does NOT own: AI Workforce OS runtime behavior, credential broker internals, policy engine authoring, browser VM loading, v86 savestates, incident module catalogs, package lifecycle governance, enterprise certification scoring, or protected-branch/release approval.

## Integration Contract

Downstream runtimes may call the CLI scripts or package them into a VM image. They must treat this repository as the source of truth for schema and reducer behavior.

If a downstream incident replay needs new verdict semantics, it should update this repository first rather than redefining rules in the replay runtime.
