# Build Week Delta

Cutoff: `2026-07-13T09:00:00-07:00`, equivalent to
`2026-07-13T16:00:00Z`.

The preparation audit counted public pull requests whose GitHub `mergedAt`
timestamp is on or after the cutoff. It separately counted local mainline
commits with Git author/commit time after the cutoff. These are different
measures and are not added together.

## Provisional inventory

| Repository | Merged PRs | Local commits |
|---|---:|---:|
| ao-architecture | 29 | 33 |
| ao-mission | 30 | 39 |
| ao-blueprint | 4 | 5 |
| ao-atlas | 7 | 8 |
| ao-foundry | 6 | 6 |
| ao-forge | 6 | 6 |
| ao-covenant | 7 | 7 |
| ao2 | 44 | 44 |
| ao2-control-plane | 17 | 17 |
| ao-command | 20 | 20 |
| ao-arena | 3 | 4 |
| ao-crucible | 3 | 4 |
| ao-sentinel | 11 | 14 |
| ao-promoter | 11 | 13 |
| **Provisional total** | **198** | **220** |

The release finalizer must replace the totals with
`304` and `346` after
freezing all fourteen public heads. The active release lane may add valid
work after this preparation snapshot.

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

Finalizer method: repeat the GitHub query with `mergedAt >= cutoff`, capture
the final repository heads, repeat the mainline commit query, and preserve
the raw machine-readable inventory in the judge package.
