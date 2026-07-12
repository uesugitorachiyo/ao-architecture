# External-Beta Preflight Checklist

- [ ] Clone each repository at the manifest's `tested_commit` in an isolated directory.
- [ ] Verify the Month 6 launch-readiness SHA-256 digest.
- [ ] Run every repository's documented native verification command.
- [ ] Run the cross-repository documentation verifier.
- [ ] Confirm install and rollback rehearsals produce no live side effects.
- [ ] Confirm Sentinel reports clear public wording.
- [ ] Confirm Promoter reports `no_promotion_requested`.
- [ ] Confirm Command reports `readback_agrees_no_promotion`.
- [ ] Confirm `external_beta_launched=false` and `rsi_remains_denied=true`.

Completion of this checklist permits review of beta readiness. It does not
permit release, deployment, publication, provider use, or beta enrollment.

