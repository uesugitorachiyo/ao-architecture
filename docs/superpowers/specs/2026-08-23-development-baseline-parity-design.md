# Development Baseline Semantic Parity Design

## Purpose

S05 independently decides whether the two S04 credential-free journeys are
semantically equivalent. It does not trust a producer's `pass` field or raw
digest assertion. It validates the complete result shape, rehashes every
bounded retained byte sequence, applies only the frozen normalization profile,
and compares the remaining contract-significant value exactly.

## Evidence Repair

The original S04 result retained artifact and stream hashes but discarded the
bytes needed to prove that a hash difference was caused only by an allowed
environmental field. S05 therefore extends the Architecture-owned runner to
retain bounded base64 encodings of each stage artifact, stdout, stderr, and
prepare streams beside their existing byte counts and SHA-256 values. The
runner records the exact absolute workspace and run roots used for that host.
It does not normalize producer output or claim parity.

The comparator decodes and rehashes those values before comparison. Missing,
malformed, oversized, or digest-mismatched evidence fails closed. Raw native
results remain separate; the parity verdict contains only hashes and the
normalization decisions, never the retained transcripts.

## Frozen Normalization Contract

`stack/development-baseline-normalization-v1.json` is a separately hashed
comparison-policy contract. It allows exactly:

- declared absolute workspace and run roots;
- path separators;
- the Windows executable suffix;
- declared native shell names;
- ISO-8601 timestamps;
- values in declared duration fields;
- values in declared process-ID fields; and
- native archive suffixes.

Every rule is independently enabled by name and has positive and negative
tests. A rule never removes an object member, list member, command argument,
identity, outcome, denial, evidence filename stem, or arbitrary numeric value.
Unknown rules and duplicate rules fail closed.

The policy is not appended to `stack/development-baseline-manifest.json`:
changing that already-qualified canonical JSON would create a new baseline
identity after S03/S04. Keeping the comparison policy separately digest-bound
preserves the reviewed `sha256:add6f39f...6429` source baseline while still
making S05 policy immutable and independently reviewable.

## Exact Comparison

The comparator first validates both results independently: schema, baseline
and correlation identities, the exact ordered 14 stages, source commits,
producer edges, terminal outcomes, decoded evidence digests, all-false
authority, and complete cleanup. It then compares normalized artifact and
stream content plus every non-environmental field.

Differences in identities, transitions, policy outcomes, evidence structure,
readbacks, assurance results, denials, or cleanup are never normalizable. A
self-declared pass with invalid content is a failure. Missing or extra evidence,
input reuse, or a baseline/profile mismatch is a failure.

## Output And Authority

The parity verdict binds both raw input digests, the comparison-policy digest,
the baseline and correlation identities, normalized evidence digests, and an
empty difference list. It reports `parity=pass` only after all validations and
exact comparison succeed. All execution, approval, mutation, provider,
credential, release, publication, deployment, promotion, compatibility,
external-beta, and RSI authority remains false.

The operator's standing campaign approval accepts this bounded design and its
necessary S04 evidence repair. It grants no denied authority and does not alter
the frozen baseline identity.
