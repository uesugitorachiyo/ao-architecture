# AO Stack Evidence Maintenance

Status: current for Adoption/Evidence Cycle Month 3.

AO Architecture records the repeatable evidence maintenance source of truth in
`stack/evidence-maintenance-report.json`.

The maintenance report checks:

- current public AO2 and Control Plane metadata against
  `stack/current-release-manifest.json`;
- compatibility matrix counts against the live edge list;
- canonical vector references for every tested edge;
- consumer test references for every tested edge;
- local AO Architecture vector files;
- operator adoption drill source availability;
- denied authority boundaries.

The compatibility gate remains `ready`, not active. Fresh evidence does not
activate the gate, launch external beta, request or grant promotion, authorize
provider pilots, authorize a release, or authorize RSI.

Run:

```sh
python3 scripts/verify_evidence_maintenance.py
python3 scripts/verify_evidence_freshness.py
python3 scripts/verify_current_release_manifest.py
python3 scripts/verify_compatibility_matrix.py
```

If any check reports `stale`, `blocked`, or `denied`, treat the maintenance
report as not refreshable until the affected metadata, vector, consumer test,
or gate boundary is corrected through the normal PR flow.
