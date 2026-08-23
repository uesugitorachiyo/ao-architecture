# Development Baseline v1 Credential-Free Fixture

This manifest orders one source-owned command from each component in the S04 AO
contract path. Run it only from the Architecture checkout inside the exact
14-repository baseline workspace:

```sh
python scripts/run_development_baseline_workflow.py \
  --fixture stack/fixtures/development-baseline-v1/fixture-manifest.json \
  --output .ao-baseline/workflow-result.json
```

The runner creates a new temporary root, passes no provider or user credential,
invokes argv without a shell, verifies every repository source head, hashes each
component-owned output, and removes only its temporary root. Generated results
remain private beneath `.ao-baseline/` and must not be committed.

Crucible, Sentinel, and Promoter binaries are built into their run-owned stage
roots and execute there so their repository-owned `tmp` output policy is
preserved without creating generated files in a source checkout.

The result proves a terminal credential-free fixture path and preserves a
Promoter `no_promotion` outcome. It grants no execution, approval, repository
mutation, provider, credential, release, publication, deployment, promotion,
compatibility, external-beta, or RSI authority. The macOS and Windows results
remain separate S04 evidence; semantic parity is decided only by S05.
