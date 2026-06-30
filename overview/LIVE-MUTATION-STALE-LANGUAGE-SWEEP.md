# Live Mutation Stale Language Sweep

This sweep checks public AO stack wording after the mutation-class ladder work.
The current public boundary remains:

- the highest proven live mutation class is `test_only`;
- `docs_only_single_file`, `docs_only_multi_file`, `docs_config_only`,
  `test_only`, `low_risk_code`, `multi_repo_low_risk`, and
  `complex_repo_mutation` are separate authority classes;
- `safe_to_execute=true` is valid only when the exact class scope and all class
  gates pass;
- `low_risk_code` remains `safe_to_execute=false`;
- `multi_repo_low_risk` remains dry-run-only;
- `complex_repo_mutation` remains dry-run-only;
- fully unsupervised complex live repository mutation remains out of scope;
- fully unsupervised complex repository mutation remains denied;
- fully unsupervised RSI remains denied;
- no AO component grants ungated live mutation authority.

## Sweep Commands

Run these from the AO workspace root:

```sh
rg -n -i "six active|6 active|six repositories|6 repositories|six active repos|6 active repos" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "safe_to_execute(=|:| true)|safe to execute|production ready for live mutation|fully autonomous live mutation|ungated live mutation authority|grant[s]? ungated|claims? ungated|fully unsupervised complex" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
rg -n -i "self-mutating RSI|full autonomous self-mutating RSI" ao-architecture ao-foundry ao-covenant ao-command ao-forge ao2 ao-sentinel ao-promoter ao-atlas ao-blueprint --glob '*.md' --glob '*.json' --glob '*.sh' --glob '*.go' --glob '!target/**' --glob '!tmp/**' --glob '!node_modules/**'
```

## Result Interpretation

The sweep should treat these as acceptable hits:

- denial language for `full_autonomous_self_mutating_rsi`;
- `claim.publish` fixtures that prove fail-closed RSI claim behavior;
- invalid fixtures where `ungated_live_mutation_claim=true` is expected to fail;
- `safe_to_execute=true` only when paired with exact class scope, exact
  approval, and all class gates;
- `low_risk_code` denial language that says `safe_to_execute=false`;
- dry-run-only language for `multi_repo_low_risk` and `complex_repo_mutation`;
- statements that the stack does not grant ungated or fully unsupervised live
  mutation authority.

The sweep should treat these as stale or unsafe:

- any claim that the stack is production-ready for broad live mutation;
- any claim that `safe_to_execute=true` can exist without exact-scope operator
  approval;
- any claim that `low_risk_code`, `multi_repo_low_risk`, or
  `complex_repo_mutation` has live execution authority;
- any statement that Blueprint, Atlas, Command, Sentinel, or Promoter can
  approve or execute live repository mutation;
- stale active-stack counts such as "six active repos" when Atlas is included;
- any statement that fully unsupervised complex live repo mutation is proven.

As of this sweep, no stale active-stack count or broad live-mutation approval
claim is expected to remain in the public documentation.
