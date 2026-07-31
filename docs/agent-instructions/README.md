# AO Stack Agent Instruction Layout

This directory defines the versioned, provider-neutral repository instruction contract accepted in [the source-of-truth ADR](../adr/2026-07-30-agent-instruction-source-of-truth.md).

The layers are:

```text
executable contracts, schemas, policy, tests, and CI
                            |
                            v
             AGENTS.md canonical guidance
                            |
                            v
         CLAUDE.md exact @AGENTS.md adapter
                            |
                            v
          skills and runbooks used on demand
```

## Contract Files

- `layout-v1.json` enumerates all 21 repositories, lifecycle states, remote expectations, required root files, approved nested scopes, and the excluded-stub fingerprint.
- `layout-v1.schema.json` describes the closed JSON shape.
- `../../scripts/verify_agent_instruction_layout.py` performs the fail-closed static checks.
- `../../scripts/test_verify_agent_instruction_layout.py` contains positive and negative fixtures for every rejection class.

The validator uses only the Python standard library. It is read-only, does not call a model or provider, does not access the network, emits deterministic JSON, and returns nonzero for any conflict.

## Commands

From an AO workspace whose children are the repository checkouts:

```sh
python3 ao-architecture/scripts/verify_agent_instruction_layout.py \
  --workspace-root .
```

During a bounded repository rollout, validate one repository while still validating the complete manifest:

```sh
python3 ao-architecture/scripts/verify_agent_instruction_layout.py \
  --workspace-root . \
  --repository ao-architecture
```

Run the regression matrix from the AO Architecture checkout:

```sh
python3 -m unittest scripts.test_verify_agent_instruction_layout
```

The full-workspace command intentionally requires sibling checkouts. It is not part of the standalone AO Architecture clone contract.

## Conflict Semantics

Output contains a stable top-level status, conflict count, sorted repository results, and sorted conflict records. Conflict codes distinguish manifest, lifecycle, path, pair, byte, size, ignore, secret/path safety, and excluded-repository failures. Consumers must treat any unknown or nonzero result as a failed gate.

The manifest is strict: duplicate keys, unknown fields, malformed or trailing JSON, unknown repositories or lifecycles, unsafe paths, and unexpected instruction locations are rejected rather than ignored.
