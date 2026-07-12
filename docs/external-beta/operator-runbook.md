# External-Beta Operator Runbook

1. Create an empty parent directory for the fourteen repositories.
2. Clone each repository and check out the exact `tested_commit` from the
   [manifest](../../stack/external-beta-tested-stack.json).
3. Run `python3 scripts/verify_external_beta_preflight.py --workspace-root <parent>`
   from AO Architecture.
4. Run the local install and quickstart verification listed by each component.
5. Record failures without changing pinned commits or weakening checks.
6. Run the installation and rollback rehearsals in this package.
7. Read the Sentinel, Promoter, and Command closure artifacts.

Stop on a digest mismatch, dirty checkout, missing repository, failed test,
unexpected side effect, authority request, provider request, or wording that
implies a launched beta. Preserve the workspace for diagnosis.

