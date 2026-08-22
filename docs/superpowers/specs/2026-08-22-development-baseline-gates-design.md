# Development Baseline Repository Gates Design

## Scope

S03 freezes and runs the development gates owned by the fourteen repositories
already bound by the S01 baseline. It does not invent shared gates, execute
release/live-provider commands, alter repository commits, or begin the AO
workflow fixture reserved for S04.

The operator's standing campaign approval accepts this design and the paired
implementation plan. Any failing repository gate remains an owning-repository
defect; Architecture may report it but may not mask or translate it.

## Contract

Each repository manifest entry gains an ordered `development_gates` array.
Every gate has a unique stable `id`, literal argv array, timeout, shell policy,
required disposition, and optional fixed environment. Shell policy is one of:

- `direct`: execute argv without a command shell;
- `posix-script`: execute the declared repository `.sh` through Bash on macOS
  and Git for Windows Bash on Windows. Repository gates use Bash syntax and
  their declared interpreter must be preserved across native hosts.

There is no arbitrary command string, interpolation, conditional skip, or
host-specific replacement argv. Conditional release, publication, deployment,
live-mutation, and instruction-layout gates are excluded because S03 changes
none of their owning surfaces and has no authority to run them.

The frozen inventory uses exact-head `ao-quality-gates.json` full-step argv
where present. For `AGENTS.md` repositories it selects the unconditional full
local development gate and every unconditional per-change policy check. A
focused gate conditioned on a particular changed subsystem is not duplicated
when the full gate strictly covers it.

## Runner

`run_development_baseline_gates.py` has one `run` mode and one
`verify-existing` mode. Both validate the S01/S03 manifest before touching an
output. `run` requires the already materialized exact workspace and an absent
result path outside it. `verify-existing` validates a retained result and
rehashes its bounded log files without executing commands.

Before the first gate for a repository, the runner verifies exact HEAD,
detached state, origin, submodules, and a clean tracked/index state. Before and
after every command it hashes the tracked/index state and fails on drift.
Untracked build outputs are permitted only inside the consumed qualification
root and are removed when the entire root is destroyed by the hosted cleanup
step; they can never be reused by `verify-existing` as source authority.

Commands run sequentially in canonical repository and manifest gate order.
The runner uses explicit argv, fixed noninteractive Git environment, bounded
stdout/stderr capture, per-gate timeout, and no credential discovery. Each log
is written beneath `.ao-baseline/gates/<repository>/<gate>.{stdout,stderr}`
with exclusive creation. The result stores only relative log names, sizes,
SHA-256 values, exit status, and state digests. A failure writes the completed
prefix plus the failing gate and stops; later gates are never represented as
passes or implicit skips.

## Native Qualification

The existing dispatch-only workflow runs the gate controller after successful
materialization on `macos-26` and `windows-2025`. Windows resolves `.cmd`/`.exe`
shims through PATH/PATHEXT and uses Git Bash only for repository-owned `.sh`
gates. Both jobs upload the materialization result, gate result, and cleanup
result before the dependent rehash job accepts the run.

S03 passes only when every required gate on both hosts is terminal pass, the
same regenerated manifest identity is reported, no tracked state changed, both
roots are absent after cleanup, and independent rehash reports zero mismatch.

## Authority

All evidence preserves false values for execution approval, provider calls,
credentials, release, publication, deployment, promotion, compatibility
activation, external beta, and RSI. Running reviewed repository test/build
argv inside a consumed qualification root does not grant any of those
authorities.
