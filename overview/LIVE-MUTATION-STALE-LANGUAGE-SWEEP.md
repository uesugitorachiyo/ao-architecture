# Live Mutation Stale Language Sweep

This sweep checks public AO stack wording after the mutation-class ladder work.
The current public boundary remains:

- the highest proven live mutation class is
  `fully_unsupervised_complex_mutation`;
- `docs_only_single_file`, `docs_only_multi_file`, `docs_config_only`,
  `test_only`, `low_risk_code`, `multi_repo_low_risk`, and
  `complex_repo_mutation` are separate lower authority classes;
- `safe_to_execute=true` is valid only when the exact class scope and all class
  gates pass;
- `low_risk_code`, `multi_repo_low_risk`, and `complex_repo_mutation` are
  proven only inside their governed rehearsal boundaries;
- `fully_unsupervised_complex_mutation` is proven only inside the governed
  26-node first non-planning rehearsal boundary;
- `bounded_rsi_evidence_rehearsal` is live-proven only as a bounded evidence
  rehearsal state;
- fully unsupervised RSI remains denied;
- broad RSI, unrestricted self-modification, hidden instruction mutation, and
  policy/auth/secret/provider/deploy/release/config/dependency expansion remain
  denied;
- no AO component grants ungated live mutation authority.

## Sweep Commands

Run these from the AO workspace root:

```sh
rg -n -i "six active|6 active|six repositories|6 repositories|six active repos|6 active repos" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "safe_to_execute(=|:| true)|safe to execute|production ready for live mutation|fully autonomous live mutation|ungated live mutation authority|grant[s]? ungated|claims? ungated|fully unsupervised complex" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "self-mutating RSI|full autonomous self-mutating RSI" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "RSI proven|broad RSI|unrestricted self-modification|hidden instruction mutation|fully autonomous RSI|highest proven live class|next denied class" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
```

## Result Interpretation

The sweep should treat these as acceptable hits:

- denial language for `full_autonomous_self_mutating_rsi`;
- `claim.publish` fixtures that prove fail-closed RSI claim behavior;
- invalid fixtures where `ungated_live_mutation_claim=true` is expected to fail;
- `safe_to_execute=true` only when paired with exact class scope, exact
  approval, and all class gates;
- `low_risk_code` denial language that says `safe_to_execute=false`;
- stale dry-run-only language for `multi_repo_low_risk` and
  `complex_repo_mutation`;
- statements that the stack does not grant ungated or fully unsupervised live
  mutation authority.
- statements that broad RSI, unrestricted self-modification, and hidden
  instruction mutation remain denied;
- statements that the highest proven live class remains
  `fully_unsupervised_complex_mutation` and the next denied class remains `RSI`.

The sweep should treat these as stale or unsafe:

- any claim that the stack is production-ready for broad live mutation;
- any claim that `safe_to_execute=true` can exist without exact-scope operator
  approval;
- any claim that `low_risk_code`, `multi_repo_low_risk`, or
  `complex_repo_mutation` has live execution authority beyond its governed
  rehearsal boundary;
- any statement that Blueprint, Atlas, Command, Sentinel, or Promoter can
  approve or execute live repository mutation;
- stale active-stack counts such as "six active repos" when Atlas is included;
- any statement that claims fully unsupervised RSI has passed its own gates;
- any statement that treats RSI as proven without the bounded
  evidence-rehearsal qualifier;
- any statement that claims unrestricted self-improvement;
- any statement that hidden instructions or policy/auth/secret/provider/deploy/
  release/config/dependency surfaces may be mutated by the bounded RSI evidence
  rehearsal.

As of this sweep, no stale active-stack count or broad live-mutation approval
claim is expected to remain in the public documentation.
