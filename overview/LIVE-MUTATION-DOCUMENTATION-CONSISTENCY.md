# Live Mutation Documentation Consistency Proof

This checklist verifies that public AO stack documentation consistently describes
the governed live-mutation boundary after the first-live-docs readiness work.

## Public Boundary Statement

- First tiny docs-only live mutation is safe to request.
- Execution is safe only when explicit exact-scope operator approval exists and
  all gates pass.
- Dry-run governed live mutation readiness is ready for the first docs-only
  class.
- Fully unsupervised complex live repository mutation remains out of scope.
- No component claims ungated live mutation authority.

## Updated Source Docs

| Repo | Public doc to inspect | Boundary covered |
| --- | --- | --- |
| `ao-architecture` | `README.md`, `overview/README.md`, `overview/LIVE-MUTATION-STALE-LANGUAGE-SWEEP.md` | Stack-wide public boundary, stale-language sweep, diagrams, and source-of-truth wording. |
| `ao-foundry` | `README.md`, `docs/operations/OVERNIGHT-REFRACTOR-REHEARSAL-RUNBOOK.md` | First-live-docs readiness rollup, approval request, PR rehearsal gate, and no broad automatic execution. |
| `ao-covenant` | `README.md` | Exact-scope approval ticket matching and fail-closed denied/stale/mismatched behavior. |
| `ao-command` | `README.md` | Read-only approval and PR rehearsal readback; no approval or execution authority. |
| `ao-forge` | `README.md` | Live-docs execution guard as eligibility evidence only. |
| `ao2` | `README.md` | Docs-only patch packet, dry-run apply, exact changed-file list, rollback patch, forbidden-path checks. |
| `ao-sentinel` | `README.md`, `docs/sdd/AO-SENTINEL-SAFETY.md` | Hold behavior for missing approval, rollback, public-safety, verification, or kill-switch evidence. |
| `ao-promoter` | `README.md`, `docs/sdd/AO-PROMOTER-GATES.md` | Promotion boundary requiring Covenant, Foundry, Forge, AO2, Sentinel, rollback, and Command evidence. |
| `ao-atlas` | `README.md`, `docs/sdd/AO-ATLAS-FOUNDRY-HANDOFF.md` | Oversized task decomposition and context/import evidence without mutation authority. |
| `ao-blueprint` | `README.md`, `docs/sdd/AO-BLUEPRINT-READINESS.md` | Build authorization is not live mutation approval. |

## Verification Commands

Run from `ao-architecture`:

```sh
python3 scripts/verify_architecture.py
git diff --check
```

Run stale-claim scans from the AO workspace root:

```sh
rg -n -i "six active|6 active|six repositories|6 repositories|six active repos|6 active repos" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "production ready for live mutation|fully autonomous live mutation|ungated live mutation authority|fully unsupervised complex live repo mutation is proven" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "safe_to_execute=true" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
```

The `safe_to_execute=true` scan may return expected hits when the same line or
nearby text states that the value is limited to the exact approved first
docs-only PR rehearsal scope. It must not appear as broad execution readiness.

## Closure Criteria

This documentation set is consistent when:

- `ao-architecture` verification passes;
- stale active-stack count scans find no stale "six active" wording;
- broad live-mutation overclaim scans find no positive claim;
- remaining `safe_to_execute=true` mentions are tied to exact approval and all
  gates;
- every public repo page states its own authority boundary;
- operator review remains the next step before any approval request is acted on.
