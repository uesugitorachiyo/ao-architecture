# Documentation Production Readiness

This page reports documentation and clean-room external-beta preflight status.
It does not certify runtime or product readiness, certify a production release,
or state that an external beta has launched.

The canonical repository heads and capability labels are in the
[tested-stack manifest](../stack/external-beta-tested-stack.json).

| Component | Maturity | Current evidence | External-beta boundary |
| --- | --- | --- | --- |
| Architecture | Documentation source of truth | executable-tested | Describes status; grants no authority. |
| Mission | Alpha | executable-tested, clean-room-rehearsed | No policy approval or mutation. |
| Blueprint | Early alpha | executable-tested, fixture-only cross-stack authorization | No scheduling or execution. |
| Atlas | Late alpha | executable-tested, clean-room-rehearsed | No authorization creation or execution. |
| Foundry | Pre-alpha orchestrator | executable-tested, fixture-only Pulse closure | No policy or provider authority. |
| Forge | Alpha | executable-tested, clean-room-rehearsed | GoalRun remains gated. |
| Covenant | Local beta | executable-tested, clean-room-rehearsed | Canonical policy and contract authority. |
| AO2 | Advanced alpha | executable-tested, clean-room-rehearsed | Provider use is unauthorized in this preflight. |
| AO2 Control Plane | Late beta, single node | executable-tested, clean-room-rehearsed | Observer only. |
| Command | Alpha/early beta | executable-tested, clean-room-rehearsed | Read-only presentation. |
| Arena | Prototype | executable-tested, fixture-only | No real benchmark claim. |
| Crucible | Prototype | executable-tested, fixture-only | No production attack target. |
| Sentinel | Alpha | executable-tested, fixture-only continuous monitoring | Reports risk; does not promote. |
| Promoter | Alpha | executable-tested, fixture-only activation | No promotion requested; no activation. |

## Preflight Gates

- All component READMEs link to Architecture and their component page.
- The manifest, topology, component pages, and diagrams use the same roles and
  maturity labels.
- Local Markdown and image links pass the conformance verifier.
- Installation and rollback procedures are rehearsals from pinned clean
  checkouts.
- Sentinel wording is clear, Promoter says no promotion requested, Command
  agrees, and RSI remains denied.

Run:

## Documentation Checks

```sh
python3 scripts/verify_architecture.py
python3 scripts/verify_external_beta_preflight.py --repository-only
```
