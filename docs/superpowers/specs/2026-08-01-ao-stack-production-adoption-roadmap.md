# AO Stack Production Adoption Roadmap

- Status: approved program design
- Roadmap window: August 1, 2026 through January 31, 2027
- Primary audience: platform and engineering teams
- Execution model: sequential Codex-led campaigns
- Release model: evidence-driven

## Execution Ownership

This document owns the portfolio design, active scope, success contract, and
monthly product gates. The canonical executable program handoff and long-run
operator procedure are owned by AO Mission:

- [AO Stack Six-Month Production Adoption Handoff](https://github.com/uesugitorachiyo/ao-mission/blob/main/docs/ao-stack-six-month-roadmap-handoff-prompt.md)
- [AO Mission Long-Run Operator Runbook](https://github.com/uesugitorachiyo/ao-mission/blob/main/docs/long-run-operator-runbook.md)

Run the program from a clean AO Mission source context. Use the common parent
workspace only to expose sibling repositories, and keep durable Mission state
outside every source checkout. AO Mission owns the single six-month record and
monthly checkpoints; AO Atlas owns one fresh workgraph per month. This roadmap
does not duplicate the operational prompt and does not grant repository
mutation, provider, pilot, deployment, or publication authority.

## Objective

Make the active AO stack installable, understandable, supportable, and useful
for platform teams running governed AI-assisted software-engineering workflows.
AO2 is the reference product and integration proof. Each component retains its
documented authority and owns its implementation contracts.

The roadmap targets 3–5 opt-in pilot teams. External contact, credentials,
provider execution, deployment, publication, and release activity require
separate approval. Calendar dates organize the work; they do not authorize a
release.

## Active Stack Scope

The canonical scope is the 14 repositories in AO Architecture's current
authority inventory:

| Roadmap track | Current repositories | Adoption responsibility |
| --- | --- | --- |
| Architecture | `ao-architecture` | Public topology, lifecycle truth, contract ownership, compatibility, and roadmap evidence |
| Control | `ao-mission`, `ao-blueprint`, `ao-atlas`, `ao-foundry`, `ao-forge`, `ao-command` | Objective intake, requirements, decomposition, scheduling, governed run state, and operator readback |
| Policy | `ao-covenant` | Policy, approval, trust, revocation, and side-effect authority |
| Execution | `ao2` | Bounded local execution, provider adapters, run evidence, and the reference user journey |
| Observation | `ao2-control-plane` | Read-only evidence ingest, verification, storage, metrics, and operator APIs |
| Assurance | `ao-arena`, `ao-crucible`, `ao-sentinel`, `ao-promoter` | Benchmarking, adversarial checks, monitoring, readiness decisions, and rollback planning |

Local directories that are absent from the canonical authority inventory are
outside this roadmap. A repository enters the active stack only through a
reviewed lifecycle or migration decision. Historical stubs and fixtures remain
historical.

## Current Baseline

- AO2 `v0.5.7` and AO2 Control Plane `v0.1.18` are the verified current public
  pair.
- AO2 provides the strongest end-to-end adoption surface: public archives,
  installation and doctor checks, governed workflows, CI integration, evidence
  export, and a companion observer.
- AO Architecture already owns authority, contract, compatibility, maturity,
  and release-classification indexes for the active stack.
- Some AO Architecture current-release material still identifies AO2
  `v0.5.6`. Month 1 must inventory this discrepancy and reconcile it through
  the owning source contract before using that material as current evidence.
- The accepted consolidation ADR proposes five product boundaries. It does not
  assert that migrations have started or authorize repository moves.

## Operating Rules

1. Execute one bounded monthly campaign at a time.
2. Start each campaign from clean, synchronized repositories and a recorded
   source-head inventory.
3. Use AO2 as the end-to-end reference journey. A component milestone is
   incomplete until AO2 or the canonical stack fixture consumes its contract.
4. Preserve repository authority. Architecture documents ownership; source
   repositories implement and verify behavior.
5. Record machine-readable evidence and a human-readable closure report for
   every campaign.
6. Open separate repository PRs for separate authority boundaries. Do not hide
   multi-repository changes in one unreviewable diff.
7. Require hosted CI and post-merge readback before closing a source change.
8. Treat pilot data as opt-in, minimal, and non-secret. Store no credentials,
   proprietary source, or private worker material in public evidence.
9. Keep releases evidence-driven. Roadmap dates, pilot completion, and merged
   features do not grant publication authority.
10. Stop when required work exceeds the current campaign's authority. Record
    the smallest follow-up instead of silently widening scope.

## Adoption Success Contract

The six-month program succeeds when all of these conditions hold:

- The 14 active repositories have current lifecycle, owner, maturity, source,
  release, and compatibility records.
- A platform team can follow one canonical path from installation through
  objective intake, authorization, AO2 execution, evidence observation,
  assurance readback, and closure.
- Median time from a clean supported host to the first verified governed AO2
  run is 30 minutes or less across the measured pilot sample.
- Three to five approved teams enter a pilot; at least three complete a first
  governed workflow in their own repository.
- At least two pilot teams repeat the workflow without live maintainer
  intervention.
- Every pilot blocker has an owning repository, severity, disposition, and
  regression or documented operator action.
- Supported installation, doctor, upgrade, rollback, recovery, and CI paths
  pass on their declared platforms.
- Gate-critical producer and consumer contracts have canonical fixtures,
  compatibility coverage, and fail-closed negative tests.
- Mission, Atlas, Command, AO2, Control Plane, and assurance readbacks agree on
  canonical run identity while retaining their separate authority-specific
  state.
- No unresolved critical security or data-integrity finding remains in the
  supported journey.
- Current documentation contains only tested commands and truthful supported
  claims.
- A final readiness review records either `release_candidate_recommended` or
  `no_release_recommended` with exact evidence. Publication remains separately
  authorized.

## Workstreams

### 1. Portfolio Truth and Ownership

Maintain the active-repository registry, source heads, lifecycle labels,
authority map, product-boundary mapping, contract owners, public releases, and
compatibility state. Detect stale current-state documentation and distinguish
it from immutable historical evidence.

### 2. Reference Platform-Team Journey

Define one supported journey that begins on a clean host and ends with a
verified, inspectable closure. The journey must cover installation, repository
bootstrap, policy selection, objective intake, plan and workgraph creation,
approval, AO2 execution, Control Plane observation, assurance readback,
support export, and rollback.

### 3. Packaging and Operations

Harden installation, upgrades, rollback, recovery, platform support,
configuration, CI integration, diagnostics, and support reproduction. Avoid
requiring users to understand the internal repository graph for the normal
path.

### 4. Contract Convergence

Verify interfaces across control, policy, execution, observation, and
assurance. Consolidation may proceed only through compatibility wrappers,
rollback plans, source-owner tests, and accepted migration decisions.

### 5. Pilot Adoption

Recruit and operate 3–5 opt-in pilots after explicit approval. Capture only the
minimum permitted operational metrics and structured feedback. Convert each
blocker into a bounded source-owner task, then re-run the reference journey.

### 6. Assurance and Readiness

Apply deterministic evaluation, adversarial checks, regression monitoring,
promotion-readiness analysis, security review, performance measurement, and
recovery exercises to the supported journey. Assurance components report and
recommend; they do not execute, approve, publish, or activate.

## Monthly Campaigns

### Month 1: Stack Truth and Adoption Baseline

Dates: August 1–31, 2026

Deliverables:

1. Verify the active 14-repository set and record clean, synchronized source
   heads.
2. Reconcile current release and lifecycle truth, including the stale AO2
   version references already visible in AO Architecture.
3. Bind every gate-critical contract to one producer, its consumers, fixtures,
   compatibility window, and authority boundary.
4. Execute the current clean-room platform-team journey without provider
   credentials and measure each stage.
5. Publish a prioritized adoption-friction inventory with owning repositories.
6. Establish metric definitions, privacy rules, pilot eligibility, consent,
   and stop conditions.

Exit gate:

- Current-state records agree across Architecture and source owners.
- The reference journey has a replayable baseline or an exact blocker.
- Every Month 2 task has one owner, acceptance criteria, and bounded authority.

### Month 2: Installable Team Path

Dates: September 1–30, 2026

Deliverables:

7. Provide one canonical installation and repository-bootstrap path for the
   supported platform matrix.
8. Rehearse upgrade, rollback, recovery, and support-bundle export from clean
   environments.
9. Make CI and pull-request integration reproducible from a documented example
   repository.
10. Align Mission, Command, AO2, and Control Plane operator terminology and
    next-action readbacks.
11. Remove onboarding defects that force users to infer internal component
    ordering or locate undocumented commands.

Exit gate:

- The complete credential-free reference journey finishes in 30 minutes or
  less on the supported native hosts, or the evidence identifies a bounded
  exception and owner.
- Install, upgrade, rollback, doctor, CI, and support paths have executable
  regressions.
- Pilot intake is ready but no team is contacted without approval.

### Month 3: First Controlled Pilots

Dates: October 1–31, 2026

Deliverables:

12. After explicit approval, onboard one or two eligible platform teams.
13. Run one governed workflow per team in a repository they control.
14. Capture time-to-first-run, stage failures, support interventions, and
    operator feedback under the approved data boundary.
15. Repair high-severity adoption blockers in their source repositories with
    regression coverage and post-merge pilot readback.

Exit gate:

- At least one team completes the journey, or an exact product blocker and the
  smallest corrective campaign are recorded.
- No credential, proprietary-source, or private-worker material enters public
  evidence.
- No authority boundary is widened to keep a pilot moving.

### Month 4: Repeat Use and Operator Convergence

Dates: November 1–30, 2026

Deliverables:

16. Expand to three to five approved pilots if Month 3 is safe and supportable.
17. Require completed teams to repeat the workflow without live maintainer
    intervention.
18. Reconcile Workbench, Control Plane, Command, and Mission status into one
    comprehensible operator journey without merging their authority.
19. Improve failure diagnosis, evidence search, support reproduction, and
    recovery from interrupted runs.

Exit gate:

- At least three teams have completed a first run and at least two have
  completed a repeat run, or the roadmap records truthful shortfalls.
- Operator surfaces share canonical identity and status semantics.
- The support path identifies the owning component without repository
  archaeology.

### Month 5: Production Hardening

Dates: December 1–31, 2026

Deliverables:

20. Run a scoped security and trust-boundary review of the supported journey.
21. Establish performance and resource baselines for representative runs.
22. Exercise interrupted-run recovery, evidence retention, version skew,
    contract rollback, and Control Plane rebuild from retained evidence.
23. Run Arena, Crucible, Sentinel, and Promoter checks against the same
    canonical journey and reconcile their readbacks.
24. Close or explicitly defer every high-severity pilot and assurance finding.

Exit gate:

- No unresolved critical finding remains.
- High-severity deferrals have owner, rationale, containment, and a dated
  follow-up.
- Recovery and compatibility checks pass without promotion or release side
  effects.

### Month 6: Adoption Proof and Release Decision

Dates: January 1–31, 2027

Deliverables:

25. Re-run the clean-host journey and the agreed pilot workflows against final
    merged heads.
26. Reconcile adoption, support, security, performance, recovery,
    compatibility, and assurance evidence into one canonical index.
27. Update public documentation and current-state contracts to match verified
    behavior.
28. Produce a package-by-package disposition: ready, conditionally ready,
    internal-only, migration-blocked, or historical.
29. Record an evidence-driven release recommendation for each publishable
    product boundary.

Exit gate:

- The six-month success contract is evaluated item by item.
- Mission, Atlas, Command, and the canonical evidence index reconcile.
- The final decision recommends a separately authorized candidate or records
  no release. The roadmap itself never publishes.

## Verification Model

Each campaign uses four layers:

1. Source-owner focused tests and fail-closed negative cases.
2. Complete applicable local gates, formatting, linting, and build checks.
3. Hosted CI and cross-repository compatibility workflows.
4. Post-merge clean-host or pilot readback against exact merged sources.

Every durable artifact receives a SHA-256 entry in a campaign manifest. The
manifest excludes itself and credential or private-worker material, then
passes an independent rehash. Historical evidence remains immutable.

## Program Handoff Cadence

The program uses one master roadmap, one six-month execution handoff, and one
program goal. Six monthly campaigns act as evidence checkpoints inside that
goal. Each month closes with:

- a source-head and authority readback;
- completed PR and hosted-CI records;
- metric results and blocker dispositions;
- a canonical evidence index;
- repository and workflow cleanup;
- a reconciled next-month workgraph.

The executor continues automatically when a monthly exit gate passes and the
next work remains inside the master handoff. The executor pauses at the explicit
approval gates for pilot contact, private data, credentials, provider activity,
deployment, migration, and release activity. Monthly closure never completes
the program goal.

## Program Stop Conditions

Stop and report exact evidence when:

- the canonical active-repository set or authority map cannot be reconciled;
- a required fix belongs to a repository outside the approved campaign;
- a pilot requires unapproved credentials, provider calls, proprietary data,
  deployment, or permission changes;
- a contract migration cannot remain backward compatible and reversible;
- hosted CI cannot become green without unrelated changes;
- a current public release, tag, asset, or published digest changes
  unexpectedly;
- an assurance finding indicates an exploitable product defect that requires a
  wider security response;
- pilot evidence fails the approved privacy boundary;
- the roadmap would need to claim adoption, readiness, performance, or safety
  beyond collected evidence.

## Decisions Preserved for Later Review

- Exact pilot organizations and contacts
- Any provider-backed pilot
- Any deployment or hosted service
- Migration into the proposed `ao-control` or `ao-assurance` boundaries
- Package retirement or repository archival
- Version numbers, candidate scope, tags, releases, assets, and publication
- Commercial terms, pricing, support commitments, or service-level agreements
