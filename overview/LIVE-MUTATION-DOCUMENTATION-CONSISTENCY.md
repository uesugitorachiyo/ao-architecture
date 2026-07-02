# Live Mutation Documentation Consistency Proof

This checklist verifies that public AO stack documentation consistently describes
the governed live-mutation boundary after the mutation-class ladder work.

## Public Boundary Statement

- The highest proven live class is
  `public_safe_bounded_recursive_improvement_review_durability_evidence`.
- `docs_only_single_file`, `docs_only_multi_file`, `docs_config_only`,
  `test_only`, `low_risk_code`, `multi_repo_low_risk`, and
  `complex_repo_mutation` are distinct lower authority classes.
- `low_risk_code`, `multi_repo_low_risk`, and `complex_repo_mutation` are
  proven only inside their governed rehearsal boundaries.
- `fully_unsupervised_complex_mutation` is proven only inside the governed
  26-node first non-planning rehearsal boundary.
- `bounded_rsi_evidence_rehearsal` is live-proven only as a bounded evidence
  rehearsal state and does not prove broad RSI.
- `bounded_rsi_self_improvement_application` is proven only for the exact
  private readback/eval rubric rehearsal.
- `exact_safe_public_claim_wording_conservative_readback_evidence` remains proven prior evidence for conservative public-safe tracked
  readback evidence around bounded improvement-claim review and retraction
  rehearsal.
- `public_safe_bounded_improvement_evidence_expansion_four_attempts` is proven
  only for four public-safe bounded evidence expansion attempts with
  reproducibility runbooks.
- `public_safe_reviewed_causal_chain_boundary_generalization_evidence` is proven
  only for public-safe reviewed causal-chain boundary generalization evidence
  across multiple independent claim-review roles.
- `public_safe_intermediate_causal_review_claim_evidence` is proven only for
  public-safe intermediate causal-review evidence that bounded improvement
  evidence can guide and constrain later claim review across independent roles.
- `public_safe_causal_review_evidence_selection_guidance` is proven only for
  public-safe causal-review evidence that prior bounded evidence can guide later
  evidence-selection and blocker prioritization under independent review gates.
- `public_safe_guided_evidence_application_four_attempts` is proven only for
  public-safe guided evidence-application evidence showing causal-review guidance
  can select and prioritize later bounded evidence attempts under independent
  gates.
- `public_safe_reviewer_approved_bounded_recursive_improvement_wording_evidence` remains prior evidence for exact public-safe reviewer-approved bounded recursive-improvement wording evidence.
- `public_safe_bounded_recursive_improvement_wording_generality_evidence` remains prior evidence for public-safe bounded recursive-improvement wording generality evidence.
- `public_safe_bounded_recursive_improvement_review_durability_evidence` is proven only for public-safe bounded recursive-improvement review durability evidence.
- The approved public wording is exactly: "AO has public-safe bounded recursive-improvement review durability evidence showing bounded recursive-improvement wording remains stable across delayed re-review, adversarial drift checks, stale-language sweeps, and reproducibility retests under independent gates; broad_RSI remains denied."
- Dry-run readiness, approved live docs mutation, approved test-only mutation,
  approved low-risk code mutation, multi-repo rehearsal, complex mutation, and
  bounded RSI application are separate public claim levels.
- `broad_RSI` remains denied.
- Broad RSI, unrestricted self-modification, hidden instruction mutation, and
  policy/auth/secret/provider/deploy/release/config/dependency expansion remain
  denied.
- Policy-changing autonomy remains denied.
- Stronger recursive-improvement claims remain denied.
- No component claims ungated live mutation authority.

## Updated Source Docs

| Repo | Public doc to inspect | Boundary covered |
| --- | --- | --- |
| `ao-architecture` | `README.md`, `overview/README.md`, `overview/MUTATION-AUTHORITY-LADDER.md`, `overview/LIVE-MUTATION-STALE-LANGUAGE-SWEEP.md` | Stack-wide public boundary, mutation-class ladder, stale-language sweep, diagrams, and source-of-truth wording. |
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
rg -n -i "RSI is proven|broad RSI is proven|broad_RSI is proven|unrestricted self-modification|hidden instruction mutation allowed|policy-changing autonomy allowed|policy-changing autonomy|stronger recursive-improvement claims are proven|stronger recursive-improvement wording approved|fully autonomous RSI|highest proven live class|next denied class" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
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
- ladder wording names
  `public_safe_bounded_recursive_improvement_review_durability_evidence` as the
  current highest proven live class and keeps `broad_RSI` denied unless its own
  gates pass;
- bounded RSI wording says only `bounded_rsi_evidence_rehearsal` is live-proven
  and keeps broad RSI, hidden instruction mutation, unrestricted
  self-modification, and policy-changing self-modification denied;
- bounded application wording says only the exact private readback/eval rubric
  rehearsal is proven;
- exact safe public claim wording says only conservative public-safe tracked
  readback evidence is proven and quotes the approved wording exactly;
- stale-language sweeps treat positive claims that broad_RSI, RSI, unrestricted
  self-modification, hidden instruction mutation, policy-changing autonomy,
  unbounded stronger recursive-improvement claims, or broad recursive-
  improvement wording are proven as unsafe unless they are explicit denial
  examples;
- every public repo page states its own authority boundary;
- operator review remains the next step before any approval request is acted on.
