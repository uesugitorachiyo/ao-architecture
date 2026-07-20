# Contract Evolution Policy

`stack/contract-evolution-policy.json` binds every edge in the compatibility
matrix to the canonical-vector bytes and consumer test recorded at immutable
merge commits. The digest is over the vector at that recorded commit, not
whatever may occupy the same path on a later branch.

The existing matrix proves current producer and consumer pairs. It does not
document predecessor versions, so the policy labels all sixteen edges
`current_pair_only`. It deliberately records no `v0 -> v1` migrations and
does not convert prose or self-asserted statuses into compatibility evidence.

A declared version change must name one documented predecessor and provide
executable test evidence at immutable commits for:

- old producer to new consumer;
- new producer to old consumer;
- current producer to current consumer; and
- rollback to the previous supported contract.

Each proof must bind its repository, fixture path and SHA-256, test selector,
and merge commit. Until all four proofs exist, the edge cannot claim
`two_version_evidence_complete`. New contracts with no predecessor remain
current-pair evidence and do not satisfy the two-version gate.

The verifier pins a trusted digest for every complete current-pair evidence
record. Each record includes the vector metadata plus the exact consumer test
selector, test-file SHA-256, and byte length at its recorded merge commit.
Valid-looking replacement hashes or selectors therefore fail validation.
The trusted declared-change registry is empty; a change declaration fails
closed until review adds the complete executable proof record to that registry.

Additive optional fields may be ignored. Unknown required fields must fail
with a bounded error. Removal requires a deprecation notice plus executable
migration and rollback evidence, and the old version remains supported for at
least two releases after a version change.

Run:

```sh
python3 scripts/verify_contract_evolution_policy.py
python3 -m unittest scripts/test_verify_contract_evolution_policy.py
```

The policy is read-only. It grants no repository mutation, promotion,
release, or RSI authority.
