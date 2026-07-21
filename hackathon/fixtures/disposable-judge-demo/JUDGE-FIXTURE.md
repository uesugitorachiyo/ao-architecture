# Disposable Judge Fixture

Objective: add input validation to `calculate_discount` and extend its tests.

Expected changed files:

- `discount_service/discounts.py`
- `tests/test_discounts.py`

Expected behavior:

- ordinary prices and rates calculate correctly;
- negative prices are rejected;
- rates below zero or above one are rejected;
- `python -m pytest` passes after the repair.

Expected evidence: AO2 run state, patch and exact-action digest, approval
record if required, verifier output, replay integrity, changed-file list, and
local report paths.

Safety boundary: this fixture contains no credentials, network calls, model
files, provider calls, external repository writes, or deployment steps. Run
it only in a newly created disposable directory.

Cleanup: remove the complete disposable directory after reviewing or
retaining its evidence.

Finalizer requirement: run this copied fixture with the downloaded public
AO2 archive on each supported quick-test path selected for publication. Do
not claim success from a source build or an unpublished candidate.
