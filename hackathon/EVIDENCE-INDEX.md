# Evidence Index

This short index favors representative public evidence over a raw log dump.

## Public release anchors

- AO2 `0.5.3`: `https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.3`
- AO2 tag target: `947e566bd3f54ed902f3c14fc0c90e21a24359bc`
- AO2 approved manifest: `6f9da69f76b07dc2181f50a411a4350ec1bef0a31b006cb6a57a5fdad7c71a97`
- AO2 Control Plane `0.1.18`:
  `https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18`
- Control Plane tag target: `6257ec23fde726d4a0133c5b62231881fb6aaa9a`
- Control Plane approved manifest: `a2f159896eea954e43d6e19914f4ef6b43aa5686ace72016dffdf0ef0ed4f455`
- AO Mission `0.1.0`: `https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.0`
- AO Mission tag target: `2901a9cb887b72296a56b70a5a3be7350b28fe65`
- AO Command `0.1.1`: `https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.1`
- AO Command tag target: `0bcadf5701fdac88f9fd792cba3a9a6686de16e5`

## Architecture and compatibility

- [AO Architecture](https://github.com/uesugitorachiyo/ao-architecture)
- [Current-release manifest](https://github.com/uesugitorachiyo/ao-architecture/blob/main/stack/current-release-manifest.json)
- [Compatibility matrix](https://github.com/uesugitorachiyo/ao-architecture/blob/main/stack/contract-compatibility-matrix.json)
- [Stack lock](https://github.com/uesugitorachiyo/ao-architecture/blob/main/stack/ao-stack.lock.json)

The preparation snapshot contains sixteen compatibility edges with canonical
vectors and consumer-test references. The top-level matrix status remains
`proposed`; judges should read the exact fields rather than treating the
count as a production-readiness claim.

## Representative implementation

- [AO2 pull requests](https://github.com/uesugitorachiyo/ao2/pulls?q=is%3Apr+is%3Amerged)
- [Control Plane pull requests](https://github.com/uesugitorachiyo/ao2-control-plane/pulls?q=is%3Apr+is%3Amerged)
- [AO Mission pull requests](https://github.com/uesugitorachiyo/ao-mission/pulls?q=is%3Apr+is%3Amerged)
- [AO Command pull requests](https://github.com/uesugitorachiyo/ao-command/pulls?q=is%3Apr+is%3Amerged)
- [AO Atlas pull requests](https://github.com/uesugitorachiyo/ao-atlas/pulls?q=is%3Apr+is%3Amerged)
- [AO Sentinel pull requests](https://github.com/uesugitorachiyo/ao-sentinel/pulls?q=is%3Apr+is%3Amerged)

## Judge-local evidence

- Quick-test result: `macOS native passed; Linux x86_64 Docker emulation passed; hosted Ubuntu/macOS/Windows public release consumer smoke run 29809470476 passed`
- Judge ZIP: `ao-stack-openai-build-week-judge-package.zip`
- Judge ZIP SHA-256: `recorded in excluded finalizer evidence after deterministic ZIP build`
- Public video: `https://youtu.be/pGhPooqC3hQ`

The finalizer adds exact PR links for the final release, public verification
runs, and the frozen Build Week inventory.
