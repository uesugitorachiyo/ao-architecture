# Assemble The AO Stack

This guide explains how the independently released AO components fit together.
AO is a governed product composed of focused repositories, not one binary or one
installer. Use the component README for platform-specific commands and use this
page for the package-level order, version pairing, and verification boundary.

## Current Supported Releases

Pin the immutable tags below before assembling a reproducible environment. The
full release evidence and asset digests are in [Current Public Releases](current-release.md).

| Package role | Repository | Release | What it provides |
| --- | --- | --- | --- |
| Execution | [AO2](https://github.com/uesugitorachiyo/ao2) | [v0.5.10](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.10) | Bounded local workflows, approvals, verification, and evidence capture |
| Observation | [AO2 Control Plane](https://github.com/uesugitorachiyo/ao2-control-plane) | [v0.1.19](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.19) | Read-only evidence ingest, storage, metrics, and operator readback |
| Mission control | [AO Mission](https://github.com/uesugitorachiyo/ao-mission) | [v0.1.3](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.3) | Objective intake, routing, durable lifecycle state, and continuation |
| Operator status | [AO Command](https://github.com/uesugitorachiyo/ao-command) | [v0.1.2](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.2) | Read-only status and evidence inspection |
| Run coordination | [AO Forge](https://github.com/uesugitorachiyo/ao-forge) | [v0.1.4](https://github.com/uesugitorachiyo/ao-forge/releases/tag/v0.1.4) | GoalRun state, factory plans, release gates, and retained run evidence |
| Policy and trust | [AO Covenant](https://github.com/uesugitorachiyo/ao-covenant) | [v0.1.1](https://github.com/uesugitorachiyo/ao-covenant/releases/tag/v0.1.1) | Policy, approval, side-effect, and evidence-contract gates |

AO Blueprint, AO Atlas, AO Foundry, AO Arena, AO Crucible, AO Sentinel, and AO
Promoter remain maintained source repositories in the stack. They were
classified `no_release_needed` for this release cycle, so use their verified
source heads and repository READMEs when assembling development or qualification
workflows. AO Architecture is the documentation and contract map; it does not
publish a binary.

## Assembly Order

1. **Choose immutable inputs.** Select the release tags above and record the
   source heads. Do not treat a moving `main` branch as the package identity.
2. **Install AO2.** Follow [First 30 Minutes With AO2](https://github.com/uesugitorachiyo/ao2/blob/main/docs/FIRST-30-MINUTES.md).
   Download only the supported platform archive, verify `SHA256SUMS`, run the
   doctor check, and complete the credential-free fixture demo.
   AO2 does not publish a Linux aarch64 archive. Linux aarch64 hosts may use
   the Linux x86_64 archive only under explicit Docker emulation.
3. **Add observation when needed.** Pair AO2 with AO2 Control Plane `v0.1.19`
   when durable evidence ingest, dashboards, or authenticated read-only APIs are
   required. Keep the Control Plane observer-only; it does not approve or apply
   AO2 changes.
4. **Add operator control.** Install AO Mission and AO Command for durable
   objectives, continuation, and read-only status. Mission records and routes
   work; it does not execute repository mutation or grant approval.
5. **Add governed coordination.** Use AO Blueprint for requirements, AO Atlas
   for bounded workgraphs, AO Foundry and AO Forge for run coordination, and AO
   Covenant for policy and side-effect gates. Follow each source repository's
   README for its own build or fixture setup.
6. **Add assurance paths as needed.** Use Arena for benchmark evidence,
   Crucible for adversarial hardening, Sentinel for regression monitoring, and
   Promoter for evidence-gated activation and rollback planning.

The normal evidence flow is:

```text
Mission intake
  -> Blueprint authorization
  -> Atlas workgraph and context pack
  -> Foundry / Forge coordination
  -> Covenant policy gates
  -> AO2 bounded execution
  -> Control Plane observation
  -> Command and Mission readback
  -> Arena / Crucible / Sentinel assurance
  -> Promoter activation plan
```

The arrows describe contracts and evidence flow, not automatic authority. A
readback, readiness result, or promotion plan never authorizes publication or a
live side effect by itself.

## Verification Checklist

For a reproducible package setup:

- Verify every downloaded archive against the checksums in
  [Current Public Releases](current-release.md).
- Confirm the executable reports the intended version and the release tag points
  to the recorded immutable source head.
- Complete AO2's credential-free fixture and doctor checks.
- Run the read-only Mission and Command status/readback paths described in their
  [source documentation](https://github.com/uesugitorachiyo/ao-mission) and
  [Command README](https://github.com/uesugitorachiyo/ao-command).
- Use the credential-free AO2 fixture and the sealed Click repair-qualification
  replay for a public, no-provider package check.
- If using the Control Plane, verify imported evidence by digest and preserve
  the original artifact for audit.
- Keep the package's version matrix and evidence manifest together with the
  operator record.

The [AO Stack Operator Workflow](operator-workflow.md) describes the detailed
contract path. [Evidence Freshness](evidence-freshness.md) explains how to
interpret current and historical evidence; the compatibility matrix remains a
proposed gate until its own activation criteria are met.

For a credential-free, offline check of a completed third-party repair bundle,
follow [Replay A Repair Qualification](repair-qualification-replay.md). The
procedure verifies exact source and evidence digests, RED/GREEN and full-suite
results, independent review, draft state, AO2's strict verdict, and Mission's
four terminal views. A passing verdict remains evidence only.

## Upgrade And Recovery

Upgrade one pinned component at a time, rerun its source-owned verification,
then rerun the package-level readback checks. Treat a changed source head,
asset digest, or compatibility edge as a new qualification input. Do not mix an
unverified AO2/Control Plane pair, and do not overwrite prior evidence when a
readback disagrees.

For interrupted work, resume from the durable Mission or Forge record and the
latest validated checkpoint. Use the component rollback instructions before
retrying. Recovery evidence is diagnostic and does not grant mutation,
promotion, provider, credential, or release authority.

## Release Boundary

This page documents how to assemble the current public package. It does not
create a tag, publish a release, upload an artifact, deploy a service, launch an
external beta, or authorize promotion. Those actions require their own frozen
inputs, gates, and explicit authority.
