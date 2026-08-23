# Development Baseline Final Qualification Design

## Purpose

S06 runs the complete reviewed baseline on clean native macOS and Windows
hosts from merged `main`, compares the retained workflow evidence, and closes
one self-contained evidence inventory. It is a read-only qualification; it
does not publish, release, deploy, promote, call a provider, use credentials,
or grant mutation authority.

## Workflow

The existing bootstrap workflow becomes a local reusable workflow while
retaining its manual diagnostic entry point. The final qualification workflow
calls it with the fixed `full` scope under `contents: read`, so both native jobs
materialize 14 detached exact commits, execute all 59 repository-owned gates,
run the 14-stage credential-free fixture, upload raw results, remove only the
run-owned root, and produce the existing independent rehash report.

A final Ubuntu comparison job downloads the artifacts from that same run,
executes the reviewed S05 comparator against the distinct macOS and Windows
workflow results, verifies the complete downloaded package, and uploads the
parity verdict and evidence-closure record. It receives no token beyond the
read-only workflow default and no AO/provider secrets.

## Evidence Closure

`scripts/verify_development_baseline_evidence.py` walks one explicit proof root
without following links. It rejects non-regular files, duplicate case-folded
paths, absolute or escaping manifest paths, files outside bounded size/count
limits, and unclassified extras. It independently hashes every retained file.

The verifier requires exactly two host results, two gate results and their
bounded logs, two workflow results, two cleanup results, one prior rehash
report, and one parity verdict. It verifies the exact merged source commit,
baseline and correlation identities, runner/platform pair, identical
14-repository host sets, 59/59 gates per host, 14/14 workflow stages, all-false
authority, root-absent cleanup, a passing zero-mismatch rehash report, distinct
parity inputs bound to the downloaded workflow bytes, and zero differences.

The output records only relative paths, sizes, and SHA-256 values. It contains
no source-root paths or host transcripts. Writing the output never changes the
proof root it inventories.

## Review Decision

The operator's standing campaign approval accepts this final qualification
design. It authorizes only the credential-free hosted proof and private
evidence import; every denied authority remains false.
