# AO Stack Current Public Releases

This is the independently verified seven-component public binary stack.

| Component | Release | Tag target | Public assets |
| --- | --- | --- | ---: |
| AO2 | [v0.5.11](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.11) | `8307795b3434af920f6cef088e56ca8fcc76775b` | 5 |
| AO2 Control Plane | [v0.1.19](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.19) | `5de3541e9007e12d95b125e7f911c02932e21479` | 7 |
| AO Mission | [v0.1.4](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.4) | `cee287597024b5a1e990c6e272518236bc9e32fa` | 3 |
| AO Command | [v0.1.2](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.2) | `a728d90077c1340e295468e5017b5e166bc5bc7a` | 3 |
| AO Atlas | [v0.2.0](https://github.com/uesugitorachiyo/ao-atlas/releases/tag/v0.2.0) | `2bf243ce8d8c71d845754398238b14d1ab77d0e6` | 15 |
| AO Forge | [v0.1.4](https://github.com/uesugitorachiyo/ao-forge/releases/tag/v0.1.4) | `e104b47c2e14b6c0927b885e137907ad227aeb5c` | 16 |
| AO Covenant | [v0.1.1](https://github.com/uesugitorachiyo/ao-covenant/releases/tag/v0.1.1) | `2fd72a0426a747868826581612fa1dc9727b53b9` | 13 |

Exact workflow identities and asset SHA-256 values are recorded in
`stack/current-release-manifest.json`. AO2 publication run
[`31619411288`](https://github.com/uesugitorachiyo/ao2/actions/runs/31619411288)
and native public verification run
[`31622142672`](https://github.com/uesugitorachiyo/ao2/actions/runs/31622142672)
bind v0.5.11. Mission publication run
[`31630701637`](https://github.com/uesugitorachiyo/ao-mission/actions/runs/31630701637)
binds v0.1.4; metadata-only release-note repair run
[`31639664541`](https://github.com/uesugitorachiyo/ao-mission/actions/runs/31639664541)
preserved its tag and assets. Atlas publication run
[`31641906614`](https://github.com/uesugitorachiyo/ao-atlas/actions/runs/31641906614)
created release `369536120` from the exact v0.2.0 source. Its publish job
succeeded; the overall run failed only because the Windows post-public note
comparison converted LF to CRLF. [PR #765](https://github.com/uesugitorachiyo/ao-atlas/pull/765)
repaired that verifier without rewriting the published release.

## Three-platform public canary

Architecture run
[`31647446543`](https://github.com/uesugitorachiyo/ao-architecture/actions/runs/31647446543)
installed the seven pinned public releases on Linux x86_64, macOS arm64, and
Windows x86_64. It ran 21 credential-free commands per platform, reconciled the
same Mission identity through Atlas, Mission, and Command, and retained zero
provider, credential, publication, deployment, or repository-mutation counts.
All platforms produced canonical terminal-index digest
`sha256:431a9ec58bdb47b2c9fcd6cdf8df5c112621ac1183c20e12e68e96916a0ce74d`.

Canary artifact SHA-256 values:

- Linux: `a246c82378b654c539b1023029a0b9661266a9399faf144a0996523a28ceddf7`
- macOS: `fbe295e4c4d269a92d4f93a3f4f49914916d119317be0e663c7ca56c6871b2fd`
- Windows: `b2db6263d1ad184961afdf3bcf83a947ab77cbadc32e77bfd619d7d09138611e`

AO Covenant v0.1.1 has no Darwin arm64 asset. The macOS arm64 canary therefore
ran its Darwin amd64 binary through Rosetta 2; this is an explicit architecture
boundary, not a native-arm64 claim.

## Compatibility and authority boundaries

The unchanged-contract bridge binds AO2 v0.5.11 to the native v0.5.10
execution-receipt vector and Control Plane v0.1.19 consumer test. The broader
compatibility matrix remains `proposed`; `compatibility_gate_complete` remains
false. These releases and canary results do not activate compatibility,
external beta, provider execution, promotion, RSI, or any live authority.
