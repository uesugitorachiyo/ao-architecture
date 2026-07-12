# Rollback Rehearsal

1. Begin from the completed installation rehearsal in a disposable directory.
2. Record every repository HEAD and the manifest digest.
3. Introduce only a local, uncommitted documentation fixture change.
4. Confirm the verifier detects the mismatch or dirty state expected by the
   owning repository's checks.
5. Remove the disposable checkout rather than resetting a shared workspace.
6. Re-clone the pinned heads and rerun verification.

Pass means the clean pinned state is reproducible and no external state changed.
This rehearsal does not test or authorize a production rollback.

