# AO Stack Operator Workflow

Status: current operator workflow source of truth.

Scope: current public release pair, compatibility evidence, governed-pool
lifecycle, controlled external-beta boundaries, support evidence, and next safe
action readback.

## Current Stack State

The current public release pair is:

- AO2 v0.5.10, tag target
  `9f4f8a8cf596127a982627b4af25c90a9a842095`.
- AO2 Control Plane v0.1.19, tag target
  `5de3541e9007e12d95b125e7f911c02932e21479`.

The Architecture compatibility matrix records 16 tested edges, 16 canonical
vectors, and 16 consumer tests. All 16 edges are fresh; the native AO2 v0.5.10
execution-to-observation vector and Control Plane v0.1.19 consumer test bind the
current public pair.
The compatibility gate is ready, not active. No external beta
launch, promotion, or RSI authority follows from this evidence.

Current tested source heads include AO2 `8fd6d6867e5a29010673c931cb566a84b9c91fb2`,
Control Plane `247719d219bb797e005358347c0269e69b3ea5d3`, and AO Mission
`c2dc4791f59173ffc61dca4e4655e0301924406c`. Mission's tested head is the
unreleased v0.1.4 candidate; its rehearsal and finalize dry run passed, but no
tag, release, deployment, publication, or public upload was attempted. These
unreleased deltas do not replace the public versions listed above.

The governed Windows V3 pool consumes this pair at the operator-local root
`%USERPROFILE%\AI Agent Teams\ao2-public-instances-v3`. Its public worker
identity is the `physical_windows_v3` role on `windows/amd64`; private machine
names and addresses are not public evidence. The accepted master prompt,
instance overlay, operating mode, source pins, and accessory tree hashes must
all pass the pool guard before a claim.

One controlled external-beta canary completed under separate authority. It
claimed and released one V3 instance, repaired one real third-party issue only
on an operator-owned fork, opened one draft fork pull request, and left the
third-party upstream repository unchanged. This result does not activate a
standing external-beta program or widen future mutation authority.

Month 4 dry-run evidence defines the controlled self-improvement boundary:
fixture-only, human-approved, rollback-verified, observed, read back to the
operator, and denied by Promoter for RSI or promotion activation.

## Denied States

- RSI remains denied.
- Live self-modification is denied.
- Provider pilot did not run.
- No standing or unrestricted external-beta program is launched. The completed
  controlled canary does not authorize another issue, fork mutation, or upstream
  submission.
- Promotion is not requested or granted.
- Release, tag, upload, deployment, and new binary publication are not part of
  the operator workflow.
- Credentials are not inspected.

## Gates

### Release Gate

The operator starts by reading the current public release pair. A workflow that
requires a new release, tag, upload, deployment, or binary publication is not a
Month 5 operator workflow item.

### Compatibility Evidence Gate

The operator checks the Architecture matrix readback. The current matrix has 16
tested edges, 0 remaining proposed edges, and 0 stale edges. The compatibility
gate is ready, not active.

### Policy Approval Gate

The operator inspects Covenant policy readback before work starts. Missing
human approval remains denied. Provider-backed work, live repository mutation,
and RSI authority remain denied.

### Dry-Run/Self-Improvement Gate

Self-improvement work is fixture-only and dry-run only. The operator reads the
dry-run evidence and confirms rollback proof before considering any follow-up.

### Observation/Readback Gate

Control Plane observation and Command readback must show the same state:
dry-run only, rollback verified, approval required, no provider execution, no
RSI, and no promotion.

### Promotion/No-RSI Gate

Promoter readback must show `promotion_requested=false`,
`promotion_granted=false`, and `rsi_authorized=false`. Sentinel wording checks
must reject any claim that changes the denied RSI, live self-modification,
external beta, promotion, or provider-pilot states.

### Governed Pool Lifecycle Gate

1. Run the V3 guard and verify the accepted prompt, overlay, mode, source pins,
   and accessory state.
2. Read status and claim exactly one free instance. Keep the printed instance
   root and lease identity through the complete task.
3. Run only the authorized credential-free validation in that claimed instance.
4. Release the exact lease, rerun status and hygiene, and require all five
   instances to be free with zero violations.

Readiness, a free instance, or a successful lifecycle canary does not authorize
repository mutation.

### Controlled External-Beta Gate

A controlled beta uses a real public issue only after read-only eligibility and
source-identity checks. Repair execution remains network-disabled and
oracle-free until the candidate is digest-sealed. Mutation is limited to one
operator-owned fork branch, one commit, and one draft pull request. No upstream
issue comment, branch, pull request, release, deployment, or publication is
allowed.

The operator must checkpoint after the draft pull request, restart from the
same Mission source, resume the same mission and correlation identities,
compact and replay readbacks, and prove that restart created no duplicate
lease, branch, commit, pull request, or issue interaction. The lifecycle canary
has a 60-minute hard maximum; the repair segment has a 240-minute hard maximum.
The completed campaign evidence identity is
`ao-mission-governed-pool-external-beta-20260807T011024Z`; raw machine evidence
remains operator-local and outside public repositories.

## Operator Workflow

1. Read current state from Architecture current-release and compatibility
   evidence.
2. Choose safe next work from Foundry safe-next-work readback.
3. Inspect policy gates in Covenant readback.
4. Run or read dry-run evidence from AO2 when a dry-run is in scope.
5. Inspect rollback and observation through AO2 and AO2 Control Plane evidence.
6. Review Sentinel and Promoter boundaries before communicating status.
7. Collect support evidence if a workflow blocks or fails.

## Support Evidence

When filing or triaging an operator workflow issue, collect public-safe evidence:

- AO2 version.
- Platform.
- Exact command.
- Expected result.
- Actual result.
- Evidence path.
- Approval status.
- Manifest or checksum state.
- Rollback status.
- Observation status.
- Sanitized logs.

Do not paste credentials, tokens, provider secrets, private repository contents,
or raw private logs into support evidence.

## Next Safe Action

Review the retained draft fork pull request and campaign evidence. Any upstream
submission, merge, additional issue, release, deployment, publication, or new
beta requires separate authority and fresh exact-head qualification.
