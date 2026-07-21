# Packaged Fixture Verification

Verified on 2026-07-21 using the fixture copied from the final judge-package
layout and the published AO2 `0.5.3` release archives. No AO2 source build,
credential, external AI provider, or existing development repository was
used.

## Results

| Check | macOS aarch64 native | Linux x86_64 Docker emulation |
|---|---|---|
| Public archive SHA-256 | `ef89f159fd7d3521c89fe7588e7fee5d32664905c1a3bb1373ce5887a95140ad` | `f0a14b739625f45ec2364681f82047a65381502f8d370952feaf7c17aa7c2c58` |
| Offline release verifier | `verified` | `verified` |
| AO2 version | `0.5.3` | `0.5.3` |
| Release source commit | `947e566bd3f54ed902f3c14fc0c90e21a24359bc` | `947e566bd3f54ed902f3c14fc0c90e21a24359bc` |
| AO2 run verdict | `accepted` | `accepted` |
| Replay digest failures | `0` | `0` |
| Fixture tests | `4 passed` | `4 passed` |
| Expected tracked files changed | `2 of 2` | `2 of 2` |

The two tracked changes were limited to:

- `discount_service/discounts.py`
- `tests/test_discounts.py`

The resulting implementation rejected negative prices and discount rates
outside the inclusive range from zero to one. The original valid-discount
test and all three added validation tests passed. AO2 also retained its local
run record, artifacts, approval record, evidence pack, event log, and HTML
report.

## Scorecard interpretation

This fixture deliberately uses AO2's credential-free built-in scripted
provider. `runs show` therefore reports an optional provider-evidence
scorecard of `40/fail`: no external provider transcript exists from which to
score provider summaries or provider-reported changed files. The authoritative
workflow verdict and replay verdict are both `accepted`, the fixture verifier
passed, and replay reported zero digest failures.

## Reproduction boundary

The macOS run used the released macOS aarch64 archive. The Linux run used the
released Linux x86_64 archive in an Ubuntu 24.04 container launched with
`--platform linux/amd64`; `git`, `python3`, and `python-is-python3` were
installed in that disposable container. Both runs copied the fixture from
`hackathon/fixtures/disposable-judge-demo` after extracting the judge package.
