# AO Stack Quality Gates

Each maintained repository owns a root `ao-quality-gates.json` manifest. The manifest declares its native commit, push, and full commands as direct argument vectors. AO Architecture owns the common schema and lifecycle registry; it does not own or execute repository-specific commands.

The commit level evaluates the exact staged tree and is bounded to ten seconds. The push level evaluates exact outgoing commits and is bounded to one hundred twenty seconds for ordinary changes. Both are network-free and source-read-only. The full level preserves each repository's authoritative checks and hosted CI remains the merge authority.

Validate the current Architecture pilot:

```sh
python3 scripts/verify_quality_gate_registry.py \
  --workspace-root .. \
  --repository ao-architecture \
  --repository-root .
```

Validate portfolio adoption after every maintained repository has adopted the contract:

```sh
python3 scripts/verify_quality_gate_registry.py --workspace-root .. --require-adopted
```

Planned entries make lifecycle scope explicit without fabricating a source-owned manifest. A planned manifest is optional, but any present manifest is validated. An adopted entry must have a valid manifest. Unknown versions, duplicate keys, symlinks, unsafe paths, oversized inputs, shell-evaluated command strings, or fast gates claiming network or source mutation fail closed.

These declarations provide deterministic developer feedback. They do not authorize execution, provider access, repository mutation, approval, release, deployment, publication, or promotion.
