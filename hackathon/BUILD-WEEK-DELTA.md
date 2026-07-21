# Build Week Delta

Cutoff: `2026-07-13T09:00:00-07:00`, equivalent to
`2026-07-13T16:00:00Z`.

AO Stack existed before the submission period. The judged work is the
meaningful extension created with Codex and GPT-5.6 after the cutoff and bound
to the released versions and immutable repository snapshot supplied in the
Devpost submission.

## Submission boundary

| Surface | Judged boundary | Public evidence |
|---|---|---|
| AO2 runtime | `v0.5.3` at `947e566bd3f54ed902f3c14fc0c90e21a24359bc` | [release](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.3) |
| AO2 Control Plane | `v0.1.18` at `6257ec23fde726d4a0133c5b62231881fb6aaa9a` | [release](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18) |
| AO Mission | `v0.1.0` at `2901a9cb887b72296a56b70a5a3be7350b28fe65` | [release](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.0) |
| AO Command | `v0.1.1` at `0bcadf5701fdac88f9fd792cba3a9a6686de16e5` | [release](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.1) |
| Judge documentation | Immutable AO Architecture commit linked from Devpost | [judge landing](README.md) |
| Supporting repositories | Dated public commit and pull-request histories | [evidence index](EVIDENCE-INDEX.md) |

Repository heads are not frozen. Later development may continue normally, but
post-package work, including the AO2 decomposition program, is not attributed
to the submitted Build Week extension.

## Meaningful extensions

- **Runtime and product:** stable AO2 and Control Plane releases, approval and
  replay diagnostics, manifest mismatch diagnostics, Windows-safe rollback,
  native Windows outbound-worker recovery, and issue-to-draft-PR contracts.
- **Tests and fixtures:** cross-platform packaging smokes, controlled
  improvement dry-runs, rollback digests, compatibility vectors, operator
  drills, and adversarial wording fixtures.
- **Architecture and documentation:** fourteen-repository role contracts,
  current-release manifests, judge-facing installation and troubleshooting,
  and operator workflow source-of-truth.
- **Release and evidence:** public asset checksums, provenance, clean-machine
  support drills, evidence freshness automation, and release/no-release
  qualification.
- **Corrections:** invalid closure evidence was explicitly reopened,
  reconciled, reverified, and superseded instead of being counted as a valid
  success.

The submission does not rely on an aggregate pull-request or commit total.
Those counts change as development continues and do not establish eligibility
or quality. The public release tags, immutable judge snapshot, dated histories,
and Codex session evidence define the submitted work instead.
