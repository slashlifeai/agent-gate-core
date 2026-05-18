# Docs And Specs Cycle Runbook

Use this runbook when a change updates Agent Gate Core contracts, schemas,
verdict behavior, or public examples.

## Classification Rule

Use `specs/` for current contract authority.

Use `docs/plans/` for lifecycle artifacts:

- design;
- implementation plan;
- review;
- verification;
- historical design references.

## Current Spec Authority

The current authority set is:

```text
specs/domain.md
specs/decisions.md
specs/agent-gate-result-v0.md
```

## Validation

Run before proposing completion:

```bash
python3 -m unittest discover -s tests -p 'agent_gate_v0_test.py'
git diff --check
test -f specs/domain.md
test -f specs/decisions.md
test -f specs/agent-gate-result-v0.md
```

If changing reducer behavior, add or update tests before changing scripts.
