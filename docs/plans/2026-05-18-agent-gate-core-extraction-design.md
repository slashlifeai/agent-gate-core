# Agent Gate Core Extraction Design

## Problem

The public incident replay runtime needs an auditable verdict core. The current scripts are small and testable, but they were authored inside a broader workforce source tree.

## Design

Extract the scripts, spec, tests, and replay fixture into a standalone `agent-gate-core` project. Keep the scope limited to evidence normalization and deterministic verdict reduction.

## In Scope

- `scripts/agent-gate-policy-result`
- `scripts/agent-gate-run`
- `scripts/agent-gate-decide`
- `specs/agent-gate-result-v0.md`
- `tests/agent_gate_v0_test.py`
- `examples/agent-gate-replay/*`
- repo boundary specs and runbooks

## Out Of Scope

- AI Workforce OS runtime behavior
- browser replay runtime
- v86 savestate handling
- incident module catalog
- private package lifecycle

## Acceptance

- Tests pass from the extracted tree.
- The extracted tree has no required path dependency on the original workforce checkout.
- README and specs define the public boundary clearly.
