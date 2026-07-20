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

## Month 3 non-edge changes

Month 3 records six contract changes that do not alter the sixteen
producer-consumer edges:

- Mission commit `b02666e7df36ea1d8f325dacedcc22d2a95099e4`
  adds optional correlation and workflow fields to existing lifecycle
  documents relative to
  `d10bc1986fe1ea5d9ac58454db4fffc08ab76bdd`. Its executable Mission tests
  preserve legacy output, exercise correlated current lifecycle output, and
  bind the rollback projection. They neither consume an immutable old-producer
  artifact nor prove that an old consumer accepts populated optional fields,
  so both cross-version directions remain `not_demonstrated`.
  The evidence record pins the test source and the old and current projection
  source SHA-256 values.
- `ao.mission.objective-workflow-contract.v0.1` is a new strict contract with
  no predecessor. Its current/current fixture and validator test are bound at
  the Mission merge commit. Legacy `ao-mission start` is an operational
  fallback, not a fictional predecessor contract.
- The AO2 GitHub draft-PR family is a new public contract family with no
  predecessor. Its current pair is bound to merged AO2 commit
  `aaa36fb13675396b60ed9a63bd94aa665be9eb5c` and the 29-test publisher
  suite. The `ao2.local-draft-pr-fixture-*` messages remain private
  executable fixture protocols and are not public stack contracts.
- Mission commit `7e7de94af5f2f463fb18a7d2fdf829e66787167f`
  introduces the strict correlation-chain, validation, and reference
  contracts. This is a new family with no predecessor; its current pair
  evidence binds all three schemas and the deterministic build, neutral
  import, and final reconciliation tests.
- The same Mission commit adds optional correlation state to the existing
  Mission record, import readback, final reconciliation packet, and archive
  contracts. Four-direction evidence preserves the uncorrelated projection
  from `b02666e7df36ea1d8f325dacedcc22d2a95099e4` and exercises current
  correlation state through archive export and import. The old-consumer
  direction and old-producer direction remain `not_demonstrated`; a current
  uncorrelated projection is not treated as an immutable old artifact, and
  legacy projection evidence is not treated as proof that populated optional
  state is accepted.
- Command commit `7cda85e56c2aa0dbf2e3772a11a6d2c93ba86303`
  adds optional `correlation_id` readback to
  `ao.command.mission-status.v0.1`. The unchanged legacy fixture is
  byte-identical at old commit `822345d718b1c660530ac91343b494a6c463a81f`
  and the merged tests prove legacy omission, current preservation, strict
  validation, and rollback projection. The old consumer is only proven against
  the unchanged fixture, so populated `correlation_id` compatibility remains
  `not_demonstrated`.

These records live outside `edges`; they do not change the compatibility
matrix, contract inventory, owner registry, trusted edge evidence, or
`TRUSTED_CHANGE_EVIDENCE_DIGESTS`.

`stack/contract-compatibility-window.json` records the four directional
outcomes and the two-release retirement rule.
`stack/contract-migration-and-rollback-results.json` binds executable evidence
to immutable source paths and digests. New families explicitly use
`not_applicable_no_predecessor` for predecessor directions. No old fixture is
invented. An additive change cannot claim four-direction completeness until an
old consumer executable accepts the populated new optional field.

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
python3 scripts/verify_contract_compatibility_window.py
python3 -m unittest scripts/test_verify_contract_compatibility_window.py
python3 scripts/verify_contract_migration_and_rollback_results.py
python3 -m unittest scripts/test_verify_contract_migration_and_rollback_results.py
python3 scripts/verify_github_issue_workflow_contracts.py
python3 -m unittest scripts/test_verify_github_issue_workflow_contracts.py
```

The policy is read-only. It grants no repository mutation, promotion,
release, or RSI authority.
