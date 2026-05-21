# Agent Gate Core

Agent Gate Core is the public evidence layer for AI-agent incident replay
runtimes such as Agent Gate Incident Replay.

It consumes existing runtime and audit evidence, normalizes it into a stable
`agent.gate.result.v0` shape, and emits deterministic PASS/FAIL verdicts. It is
not a policy engine, agent runtime, credential broker, or product lifecycle
manager.

Core owns the evidence schema and verdict reducer. Replay runtimes own the
browser, VM, incident module, savestate, and transcript surfaces that produce
the evidence consumed by Core.

## Commands

```text
agent-gate-policy-result policy-events.jsonl
agent-gate-run ...
agent-gate-decide *.json
```

`agent-gate-policy-result` normalizes existing runtime, policy, or ledger event
JSONL into `policy-result.json`.

`agent-gate-run` runs one agent or tool command through the existing audit path
and emits one normalized `agent.gate.result.v0` gate result.

`agent-gate-decide` reduces one or more normalized result files into one
deterministic verdict.

## Evidence Flow

```text
runtime / policy / ledger events
  -> agent-gate-policy-result
  -> policy-result.json
  -> agent-gate-run
  -> gate-result.json
  -> agent-gate-decide
  -> VERDICT: PASS / VERDICT: FAIL
```

Gate v0 fails closed when evidence is missing, malformed, has an invalid schema,
has invalid audit evidence, or contains a CRITICAL policy violation. Otherwise
it emits PASS.

## Quick Check

From this repository root:

```bash
python3 -m unittest discover -s tests -p 'agent_gate_v0_test.py'
```

Run the smallest replay fixture:

```bash
scripts/agent-gate-policy-result examples/agent-gate-replay/events-fail.jsonl
```

Run the smallest end-to-end PASS/FAIL replay:

```bash
cat examples/agent-gate-replay/README.md
```

That fixture shows how policy events become `policy-result.json`, how
`agent-gate-run` emits a normalized gate result, and how `agent-gate-decide`
returns the final verdict.

## Integration Contract

Downstream replay runtimes may call these CLI scripts directly or package them
into a VM image. They must treat this repository as the source of truth for:

* `agent.gate.result.v0`
* policy evidence normalization
* deterministic PASS/FAIL reducer behavior

If a replay runtime or incident module needs new evidence fields or verdict
semantics, update Agent Gate Core first instead of redefining reducer behavior
inside the replay runtime.

The current `signature` field and verdict output line are reserved placeholders
for a later provenance layer. They must not be represented as production
cryptographic identity proof in v0.

## Repository Boundary

Agent Gate Core owns evidence schemas, normalization, deterministic verdict
rules, CLI fixture tests, and examples.

Agent Gate Core does not own browser replay, v86, VM savestates, incident
catalog publication, AI Workforce OS internals, credential broker internals, or
third-party certification claims.
