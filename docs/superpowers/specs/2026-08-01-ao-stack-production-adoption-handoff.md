# AO Stack Six-Month Production Adoption Handoff

## Execution Mode

Create exactly one new goal for this handoff. Keep that goal active across the
entire August 1, 2026 through January 31, 2027 program. Do not create a new goal
for each month and do not mark the goal complete at an intermediate checkpoint.

Execute the six-month roadmap end to end from the Codex application. Continue
automatically through portfolio inventory, bounded implementation, pull
requests, hosted CI, merges, post-merge verification, approved pilot evidence,
hardening, adoption reconciliation, release recommendation, and cleanup unless
a stated approval gate or stop condition is reached.

Use thread continuation, scheduled monitoring, or task wakeups when evidence
requires real elapsed time. Do not compress calendar observation windows,
simulate pilot participation, or invent adoption evidence. Monthly boundaries
are evidence checkpoints within one program goal.

Roadmap source:

`docs/superpowers/specs/2026-08-01-ao-stack-production-adoption-roadmap.md`

This handoff authorizes execution of all six roadmap months within the
boundaries below. It does not authorize pilot contact, credentials, provider
calls, deployment, repository migration, or publication without the separate
approval specified for that action.

## Program Objective

Make the active AO stack installable, understandable, supportable, and useful
for platform and engineering teams running governed AI-assisted
software-engineering workflows.

AO2 is the reference product and integration proof. AO Architecture owns the
portfolio topology and current-state contract map. Every source repository
retains its documented implementation authority.

By program closure:

1. The canonical 14-repository stack must have truthful lifecycle, ownership,
   release, compatibility, and readiness records.
2. A platform team must be able to complete the supported journey from clean
   installation through governed AO2 execution, observation, assurance,
   support export, and closure.
3. Three to five approved teams must enter a pilot, at least three must
   complete a first governed workflow in their own repository, and at least two
   must repeat the workflow without live maintainer intervention.
4. Median clean-host time to first verified governed run must be 30 minutes or
   less across the measured pilot sample.
5. Every blocker must have an owner, severity, disposition, and regression or
   exact operator action.
6. Supported install, doctor, CI, upgrade, rollback, recovery, compatibility,
   security, and assurance gates must pass against final merged sources.
7. Month 6 must record either `release_candidate_recommended` or
   `no_release_recommended` from exact evidence. This handoff does not publish
   the candidate.

## Canonical Repository Scope

Use the active repository set in AO Architecture's current authority
inventory:

- `ao-architecture`
- `ao-mission`
- `ao-blueprint`
- `ao-atlas`
- `ao-foundry`
- `ao-forge`
- `ao-command`
- `ao-covenant`
- `ao2`
- `ao2-control-plane`
- `ao-arena`
- `ao-crucible`
- `ao-sentinel`
- `ao-promoter`

Do not add local repositories, legacy implementations, stubs, mirrors, or
experiments because they exist in the workspace. Record them as out-of-scope
discoveries when relevant. Repository membership changes require a reviewed
lifecycle or migration decision and are outside this handoff.

## Product Tracks

Coordinate work through these tracks without merging their authority:

| Track | Repositories | Responsibility |
| --- | --- | --- |
| Portfolio truth | `ao-architecture` | Topology, lifecycle, contract ownership, compatibility, release truth, and roadmap evidence |
| Control | `ao-mission`, `ao-blueprint`, `ao-atlas`, `ao-foundry`, `ao-forge`, `ao-command` | Intake, requirements, workgraphs, scheduling, run state, and operator readback |
| Policy | `ao-covenant` | Policy, approval, trust, revocation, and side-effect authority |
| Execution | `ao2` | Bounded local execution, adapters, run evidence, and the reference journey |
| Observation | `ao2-control-plane` | Read-only evidence ingest, verification, storage, metrics, and APIs |
| Assurance | `ao-arena`, `ao-crucible`, `ao-sentinel`, `ao-promoter` | Benchmarking, adversarial checks, monitoring, readiness decisions, and rollback planning |

The accepted consolidation ADR remains a proposed target topology. Do not
start migration into `ao-control` or `ao-assurance` under this handoff.

## Verified Starting Context

Verify every starting fact independently before relying on it:

- AO2 `v0.5.7` is the current public stable release and was published from
  `a3d8d19cef8f3aa69ea14e46ef94cc9706a502a7`.
- AO2 Control Plane `v0.1.18` is its supported companion.
- AO2 and AO2 Control Plane source-owned release-train manifests identify
  `v0.5.7/v0.1.18` as stable.
- AO Architecture current-release and release-classification material may
  still identify AO2 `v0.5.6` or older component heads. Treat each occurrence
  according to its current-state or historical role.
- The active authority inventory contains 14 repositories and records
  migration as not started.

## Program Authority

Authorized:

- read-only inspection of the 14 repositories, their public GitHub state,
  workflows, releases, tags, issues, and source-owned contracts;
- one private program evidence root outside public repositories, containing
  one subdirectory per monthly campaign and one final program index;
- bounded `codex/` branches, commits, pull requests, hosted CI, merges, and
  cleanup in active repositories when a monthly phase explicitly requires a
  source-owner change;
- at most one pull request per affected repository per monthly campaign unless
  a stop condition requires a smaller separately reviewed corrective PR;
- source-owned tests, documentation, contract fixtures, default verification
  workflows, packaging, diagnostics, compatibility, security, performance,
  recovery, and operator improvements directly required by the roadmap;
- credential-free clean-host and fixture-backed integration runs;
- read-only verification of existing public releases and packages;
- approved, minimized, de-identified pilot evidence supplied within the pilot
  data contract;
- recurring read-only monitoring needed to measure real adoption and
  reliability windows.

Separately gated and not authorized until the user explicitly approves the
specific action:

- contacting, inviting, enrolling, or messaging a pilot team;
- accessing a pilot repository or accepting pilot-provided private material;
- using credentials, secrets, provider APIs, paid services, or private
  infrastructure;
- deploying or changing an environment, runner, permission, identity,
  retention policy, or network boundary;
- starting a repository migration, retirement, archive, transfer, or package
  consolidation;
- preparing, tagging, publishing, editing, deleting, redrafting, or replacing
  a release or release asset;
- publishing to a package registry or changing a public support commitment.

Never authorized:

- direct pushes to `main`, force pushes, history rewrites, hidden instruction
  changes, credential disclosure, fabricated evidence, or historical evidence
  rewrites;
- widening Covenant policy or another component's authority merely to keep a
  workflow moving;
- declaring a future version or release candidate before the Month 6 evidence
  decision.

## Cross-Campaign Operating Contract

At the beginning of every monthly campaign:

1. Record the current date, objective, authority, source heads, public state,
   dependencies, workgraph, success criteria, and stop conditions.
2. Verify every affected repository is clean on `main`, `HEAD == origin/main`,
   and free of overlapping branches, worktrees, pull requests, and workflows.
3. Read all applicable repository instructions.
4. Reconcile the prior checkpoint and independently rehash its evidence
   manifest.
5. Confirm the proposed changes still belong to the current month and owning
   repositories.

For every repository mutation:

1. Use a task branch prefixed `codex/` and an isolated task worktree when the
   repository workflow requires it.
2. Add a failing regression before changing behavior when the work is a feature
   or defect fix.
3. Keep source-owner changes separate from portfolio documentation changes.
4. Run focused checks, the complete applicable local gate, formatting, linting,
   builds, and `git diff --check`.
5. Open one bounded pull request, wait for all required hosted CI, and merge
   only when green.
6. Synchronize `main`, remove local and remote task branches, remove task
   worktrees, and verify no overlapping workflow remains active.

At the end of every month:

1. Re-run cross-repository checks against merged heads.
2. Bind source heads, workflow runs, metrics, blockers, and public-state
   readbacks.
3. Build and independently verify a monthly evidence manifest.
4. Reconcile the checkpoint through Atlas, Mission, and Command.
5. Preserve a recommended next-month workgraph without using it to widen the
   current month's authority.
6. Keep the single program goal active.

## Month 1: Stack Truth and Adoption Baseline

Window: August 1–31, 2026

### Required Work

1. Verify the canonical active set and record exact source heads for all 14
   repositories.
2. Inventory every additional AO-named workspace directory and classify it as
   canonical active, historical, stub, excluded legacy, successor proposal, or
   unknown.
3. Verify public release, package, tag, asset, supported-platform, lifecycle,
   maturity, and current-source claims.
4. Reconcile stale current-state AO Architecture records, including confirmed
   AO2 `v0.5.6` references, without modifying historical Month 6 evidence.
5. Bind every gate-critical contract to one producer, its consumers, fixtures,
   compatibility window, negative tests, and authority boundary.
6. Run the existing credential-free clean-room platform-team journey and
   measure elapsed time and operator interventions per stage.
7. Create the adoption metric definitions, privacy boundary, pilot eligibility
   criteria, consent requirements, severity model, and blocker taxonomy.
8. Publish a prioritized Month 2 workgraph with exact source owners and
   acceptance criteria.

### Mutation Boundary

Month 1 permits one bounded AO Architecture pull request. Other repositories
remain read-only. Source defects become owner-scoped Month 2 tasks unless an
existing public claim is unsafe; in that case stop and report the smallest
corrective action.

### Exit Gate

- Current-state Architecture records agree with independently verified source
  and public state.
- Every gate-critical contract has one owner or a precise blocking finding.
- The clean-room journey has replayable evidence or an exact owner-scoped
  blocker.
- Every Month 2 task has authority, dependencies, acceptance tests, and stop
  conditions.

Checkpoint classification:

`AO_STACK_PRODUCTION_ADOPTION_MONTH1_BASELINE_COMPLETE`

Continue into Month 2 when the exit gate passes. Do not close the program goal.

## Month 2: Installable Team Path

Window: September 1–30, 2026

### Required Work

1. Implement one canonical supported installation and repository-bootstrap
   path centered on AO2 and its required operator surfaces.
2. Make component discovery and ordering explicit so a platform team does not
   need repository archaeology.
3. Exercise install, doctor, configuration, upgrade, rollback, interrupted-run
   recovery, and support-bundle export on every declared native platform.
4. Provide a reproducible CI and pull-request integration from a public sample
   repository.
5. Align Mission, Command, AO2, and Control Plane identity, status, error, and
   next-action terminology while retaining separate authority.
6. Add regression coverage for stale commands, unsupported platform claims,
   missing rollback steps, ambiguous ownership, and mismatched cross-surface
   identities.
7. Run clean-host trials until the complete credential-free reference journey
   reaches a measured median of 30 minutes or less, or record the bounded
   product blockers that prevent it.
8. Produce a pilot-ready onboarding pack, data contract, consent record,
   support runbook, escalation path, and operator checklist.

### Mutation Boundary

Change only repositories that own confirmed Month 1 blockers. Use at most one
bounded pull request per affected repository. Update AO Architecture only after
source-owner changes merge and their current-state readbacks are available.

### Exit Gate

- Install, doctor, CI, upgrade, rollback, recovery, and support paths have
  executable regressions.
- The canonical journey reaches the 30-minute target or has no unresolved
  blocker suitable for a pilot.
- Pilot materials pass privacy, security, authority, and support-readiness
  review.
- No pilot has been contacted without explicit approval.

Checkpoint classification:

`AO_STACK_PRODUCTION_ADOPTION_MONTH2_INSTALLABLE_PATH_COMPLETE`

Continue into Month 3 only after the user approves the named pilot cohort and
the permitted contact, data, repository, credential, and provider boundaries.
That approval does not authorize a release.

## Month 3: First Controlled Pilots

Window: October 1–31, 2026

### Approval Gate

Before external action, present:

- the proposed one or two pilot teams and contacts;
- the exact message or onboarding request;
- repository visibility and data-handling boundaries;
- whether the team or operator supplies provider execution;
- allowed metrics and retention;
- support responsibilities;
- stop and withdrawal procedure.

Proceed only after explicit user approval. Codex must not request, receive, or
use pilot credentials. A pilot team may run provider-backed work in its own
environment and provide only approved, minimized evidence.

### Required Work

1. Enroll one or two approved platform teams.
2. Verify consent and preflight before receiving pilot evidence.
3. Support one governed workflow per team in a repository they control.
4. Record time to first verified run, stage timings, failures, interventions,
   support requests, and structured feedback under the approved data contract.
5. Triage each blocker to its source owner and severity.
6. Fix high-severity adoption blockers through bounded source-owner pull
   requests with regression coverage.
7. Re-run the affected pilot path or an approved replay against exact merged
   sources.
8. Produce a Month 3 pilot evidence packet that contains no credentials,
   proprietary source, private logs, or unapproved identifiers.

### Exit Gate

- At least one team completes the supported journey, or an exact product
  blocker and smallest corrective campaign are recorded.
- Every observed blocker has an owner and disposition.
- No authority or privacy boundary was widened to keep a pilot moving.
- Public release state remains unchanged.

Checkpoint classification:

`AO_STACK_PRODUCTION_ADOPTION_MONTH3_FIRST_PILOTS_COMPLETE`

Continue into Month 4 only if the first pilots are safe, supportable, and
approved for expansion.

## Month 4: Repeat Use and Operator Convergence

Window: November 1–30, 2026

### Required Work

1. Expand to three to five total approved pilot teams within the Month 3 data
   and authority boundaries, or obtain explicit approval for any change.
2. Ask completed teams to repeat the supported workflow without live maintainer
   intervention.
3. Measure repeat-run completion, time, error recovery, evidence retrieval, and
   support demand.
4. Reconcile Workbench, AO2 Control Plane, Command, and Mission status into one
   comprehensible operator journey without merging authority.
5. Improve failure diagnosis, evidence search, interrupted-run recovery,
   support reproduction, and owner routing.
6. Add end-to-end regressions for every repaired adoption blocker.
7. Verify compatibility across all exact component versions used by pilots.
8. Publish a truthful adoption checkpoint, including shortfalls and withdrawn
   or incomplete pilots.

### Exit Gate

- Three teams complete a first run and two teams complete a repeat run without
  live maintainer intervention, or the checkpoint records the exact shortfall
  and smallest corrective action.
- Operator surfaces share canonical run identity and compatible status
  semantics.
- A support operator can identify the owning repository without searching
  unrelated implementation history.

Checkpoint classification:

`AO_STACK_PRODUCTION_ADOPTION_MONTH4_REPEAT_USE_COMPLETE`

Continue into Month 5 after all critical pilot findings are fixed or safely
contained with an accepted owner and follow-up.

## Month 5: Production Hardening

Window: December 1–31, 2026

### Required Work

1. Run a scoped security review of the supported journey, trust boundaries,
   artifact handling, operator surfaces, update path, and recovery path.
2. Validate plausible findings and fix confirmed in-scope vulnerabilities
   through source-owner pull requests.
3. Establish representative performance and resource baselines for clean-host,
   first-run, repeat-run, evidence-ingest, and readback paths.
4. Exercise interrupted-run recovery, retention, version skew, contract
   rollback, revoked approval, corrupted evidence, and Control Plane rebuild
   from retained public-safe evidence.
5. Run Arena, Crucible, Sentinel, and Promoter against the same canonical
   journey and reconcile their readbacks.
6. Verify assurance components report or recommend without approving,
   executing, activating, publishing, or overriding policy.
7. Close every critical finding and close or explicitly defer every high
   finding with owner, containment, rationale, and dated follow-up.
8. Re-run the pilot journeys or approved deterministic replays after hardening.

### Exit Gate

- No unresolved critical security, authority, or data-integrity finding
  remains.
- Performance baselines bind exact sources, inputs, host classes, and variance.
- Recovery and compatibility tests pass without promotion or release side
  effects.
- High-severity deferrals are explicit and do not invalidate the supported
  journey.

Checkpoint classification:

`AO_STACK_PRODUCTION_ADOPTION_MONTH5_HARDENING_COMPLETE`

Continue into Month 6 when the final evidence set is stable enough for an
adoption and release-readiness decision.

## Month 6: Adoption Proof and Release Decision

Window: January 1–31, 2027

### Required Work

1. Freeze the Month 6 evaluation inputs without freezing repository
   development outside the bounded evaluation scope.
2. Verify all affected repositories are clean, synchronized, and free of
   overlapping work.
3. Re-run clean-host installation, doctor, CI, upgrade, rollback, recovery,
   support export, and the full credential-free reference journey against final
   merged heads.
4. Re-run the agreed pilot workflows or approved de-identified replays and bind
   exact sources and component versions.
5. Evaluate every six-month success criterion with exact evidence and no
   inferred success.
6. Reconcile adoption, support, compatibility, security, performance,
   recovery, and assurance evidence into one canonical program index.
7. Update current documentation and machine-readable contracts in their source
   repositories when they do not match verified behavior.
8. Assign every active repository one final disposition: `ready`,
   `conditionally_ready`, `internal_only`, `migration_blocked`, or
   `historical_reclassification_required`.
9. Record a release decision for each publishable boundary as
   `release_candidate_recommended` or `no_release_recommended`.
10. If a candidate is recommended, produce a separate release-qualification
    handoff draft. Do not bump versions, prepare tags, publish assets, or start
    qualification under this program handoff.

### Exit Gate

- The full success contract has an itemized pass or truthful failure.
- Current public claims and source-owned contracts match final verified state.
- Mission, Atlas, Command, AO2, Control Plane, and assurance surfaces reconcile
  canonical run identity while retaining distinct state and authority.
- The release decision is evidence-backed and non-publishing.
- All repositories and workflows satisfy final cleanup.

## Required Evidence

Create one program evidence root with a subdirectory for each month. Each month
must contain at least:

- `objective.json`
- `authority.json`
- `preflight.json`
- `source-heads.json`
- `workgraph.json`
- `reference-inventory.json`
- `changes-and-pull-requests.json`
- `local-verification.json`
- `hosted-ci.json`
- `post-merge-readback.json`
- `metrics.json`
- `blocker-dispositions.json`
- `terminal-index.json`
- `campaign-manifest.json`
- `final-report.md`

Program-level evidence must include:

- `program-objective.json`
- `program-authority.json`
- `canonical-repository-registry.json`
- `contract-owner-baseline.json`
- `compatibility-history.json`
- `public-release-immutability-history.json`
- `reference-journey-history.json`
- `pilot-consent-index.json`
- `pilot-evidence-index.json`
- `adoption-metrics-history.json`
- `security-findings-disposition.json`
- `performance-baseline.json`
- `recovery-and-rollback.json`
- `assurance-reconciliation.json`
- `component-readiness-dispositions.json`
- `release-recommendations.json`
- `monthly-checkpoint-index.json`
- `terminal-index.json`
- `program-manifest.json`
- `final-report.md`

Do not place credentials, proprietary source, private logs, private worker
material, unapproved personal identifiers, or raw pilot content in the evidence
root. Store only approved summaries and digests needed by the data contract.

Every monthly campaign manifest and the final program manifest must enumerate
all durable public-safe artifacts in scope, exclude itself, bind a SHA-256 for
every entry, and pass an independent rehash.

## Mission, Atlas, and Command Reconciliation

Build a canonical Atlas terminal index at every monthly checkpoint and at final
closure. Import each index through AO Mission. Mission inspect, checkpoint,
event-index, and Command readbacks must share the canonical payload and index
digest while retaining distinct surface-specific state digests.

Monthly reconciliation does not complete the program goal. Final Mission and
Atlas completion must bind the six monthly checkpoint indexes and the final
program manifest.

## Public-State Immutability

Record public release, tag, asset, digest, timestamp, and download-URL state at
program preflight, each monthly checkpoint, and final closure. Treat an
unexpected mutation as a stop condition.

Authorized source PRs may change `main`. They may not modify public tags,
releases, assets, package registry objects, or historical evidence. A separately
approved later release task owns any publication.

## Final Cleanup

Before final classification:

- all 14 repositories are clean on `main` and `HEAD == origin/main`;
- all program task branches are removed locally and remotely;
- all program task worktrees are removed;
- every program pull request is merged or closed with disposition;
- no overlapping program workflow remains queued or running;
- pilot access is withdrawn or handed back according to the approved consent
  contract;
- no credential or private pilot material remains in campaign evidence;
- public release objects match their last authorized state;
- no repository lifecycle, migration, deployment, provider, permission,
  environment, runner, release, or authority mutation occurred without its
  explicit approval.

## Stop Conditions

Stop with exact evidence if:

- canonical active-stack membership or authority ownership cannot be
  reconciled;
- a public release, tag, asset, digest, or publication timestamp changes
  unexpectedly;
- truthful work requires a repository, migration, authority, credential,
  provider, deployment, or publication action outside approved scope;
- a pilot team cannot provide informed consent or the required privacy boundary;
- pilot evidence contains material that cannot be safely minimized;
- a contract change cannot remain backward compatible and reversible;
- required hosted CI cannot become green without unrelated changes;
- a product, security, authority, or data-integrity defect requires a broader
  response;
- the 30-minute target, first-run target, or repeat-run target fails and cannot
  be truthfully repaired inside the current month;
- a release recommendation would require inventing a version, adoption result,
  performance result, or safety claim;
- the calendar window ends before required real-world evidence exists.

Report the exact month, repository, source SHA, file or workflow, pull request
or run ID, failed assertion, pilot boundary when applicable, public state, and
smallest operator action. Keep the single program goal active unless the task
is genuinely blocked under the goal protocol.

## Terminal Classification

Use exactly:

`AO_STACK_SIX_MONTH_PRODUCTION_ADOPTION_COMPLETE`

Use it only when all six monthly checkpoints are complete, the platform-team
success contract passes, every required PR and hosted check is reconciled,
public state is unchanged except for separately approved actions, Mission and
Atlas reconcile the complete program, the program manifest independently
verifies, final cleanup passes, and the release decision remains a
non-publishing recommendation.

Do not return after a monthly checkpoint, pilot launch, PR merge, workflow
dispatch, hardening pass, or release recommendation alone. Continue through
complete six-month closure unless an approval gate or stop condition requires
the user.
