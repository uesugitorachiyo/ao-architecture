# AO Stack Current Public Releases

This is the independently verified seven-component public binary stack.

| Component | Release | Tag target | Public assets |
| --- | --- | --- | ---: |
| AO2 | [v0.5.11](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.11) | `8307795b3434af920f6cef088e56ca8fcc76775b` | 5 |
| AO2 Control Plane | [v0.1.19](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.19) | `5de3541e9007e12d95b125e7f911c02932e21479` | 7 |
| AO Mission | [v0.1.5](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.5) | `5d4562578a4751d56910ef108b930fbb8dc91e7d` | 3 |
| AO Command | [v0.1.3](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.3) | `ffef6d76306e892c3e7a7f39734433d5a832006a` | 3 |
| AO Atlas | [v0.2.1](https://github.com/uesugitorachiyo/ao-atlas/releases/tag/v0.2.1) | `3603a2bb8af5adafcd9ff17b807ab89f32283d18` | 15 |
| AO Forge | [v0.1.5](https://github.com/uesugitorachiyo/ao-forge/releases/tag/v0.1.5) | `d1723769949269dcd0589916d83769dcb7275f98` | 16 |
| AO Covenant | [v0.1.1](https://github.com/uesugitorachiyo/ao-covenant/releases/tag/v0.1.1) | `2fd72a0426a747868826581612fa1dc9727b53b9` | 13 |

Exact workflow identities and asset SHA-256 values are recorded in
`stack/current-release-manifest.json`. AO2 publication run
[`31619411288`](https://github.com/uesugitorachiyo/ao2/actions/runs/31619411288)
and native public verification run
[`31622142672`](https://github.com/uesugitorachiyo/ao2/actions/runs/31622142672)
bind v0.5.11. Mission publication run
[`32532729277`](https://github.com/uesugitorachiyo/ao-mission/actions/runs/32532729277)
binds v0.1.5. Command publication and public verification run
[`32536659576`](https://github.com/uesugitorachiyo/ao-command/actions/runs/32536659576)
binds v0.1.3. Atlas publication run
[`32537720561`](https://github.com/uesugitorachiyo/ao-atlas/actions/runs/32537720561)
created release `374742316` from the exact v0.2.1 source; PR
[#771](https://github.com/uesugitorachiyo/ao-atlas/pull/771) repaired portable
post-public verification without replacing the released assets. Forge
finalizer run
[`32539072103`](https://github.com/uesugitorachiyo/ao-forge/actions/runs/32539072103)
published the signed, rehearsed v0.1.5 draft.

## Three-platform public canary

Architecture run
[`32540433860`](https://github.com/uesugitorachiyo/ao-architecture/actions/runs/32540433860)
installed the seven pinned public releases on Linux x86_64, macOS arm64, and
Windows x86_64. It ran 21 credential-free commands per platform, reconciled the
same Mission identity through Atlas, Mission, and Command, and retained zero
provider, credential, publication, deployment, or repository-mutation counts.
All platforms produced canonical terminal-index digest
`sha256:431a9ec58bdb47b2c9fcd6cdf8df5c112621ac1183c20e12e68e96916a0ce74d`.

Canary artifact SHA-256 values:

- Linux: `35652deb5e14671c8e9838541f5e529cc1919430dfa18ed2b1159e0edf0e0995`
- macOS: `1e77918269a20aa00a70688477fb10f117933137737caea417818f781666dfef`
- Windows: `6ebb61dc243abddc9e91c58f2b9966b8e91effce40af0d531dbc0f82e9b9b6f3`

AO Covenant v0.1.1 has no Darwin arm64 asset. The macOS arm64 canary therefore
ran its Darwin amd64 binary through Rosetta 2; this is an explicit architecture
boundary, not a native-arm64 claim.

## Compatibility and authority boundaries

The unchanged-contract bridge binds AO2 v0.5.11 to the native v0.5.10
execution-receipt vector and Control Plane v0.1.19 consumer test. The broader
compatibility matrix remains `proposed`; `compatibility_gate_complete` remains
false. These releases and canary results do not activate compatibility,
external beta, provider execution, promotion, RSI, or any live authority.
