# Compact Evidence Contract

Status: proposed. AO Architecture owns the canonical compact evidence contract;
AO Foundry owns future generation and verification integrations, and AO Atlas
owns workgraph/node-evidence consumption.

The source of truth is `stack/compact-evidence-contract.json`. Compact evidence
uses a versioned manifest, ordered bounded JSONL chunks, stable lexicographic
`record_id` ordering, per-chunk SHA-256 digests, record counts and first/last
record ranges, and an aggregate manifest digest. Chunk paths must be safe
relative paths, never absolute machine-local paths or traversal paths.

Legacy per-file evidence remains supported until every in-scope consumer proves
compact compatibility. Generators may prefer compact output only after compact
and legacy evidence are verified to produce equivalent logical records.

Large scale fixtures for 100, 1,000, 10,000, and 9,000-plus record evidence
classes must be generated in the excluded evidence directory instead of being
committed as thousands of files. Reports must include file count, byte count,
verifier memory, and verification time before and after.

Run:

```sh
python3 scripts/verify_compact_evidence_contract.py
```
