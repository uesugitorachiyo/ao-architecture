# AO Next N0/N4/N7 Live Evaluation

Status: `AO_NEXT_LIVE_EVALUATION_PASSED`

This record describes one fixed 27-row comparison. It is evidence for the evaluated bindings below, not a general claim that AO Next is production-ready or authorized to replace the AO Stack.

## Fixed Inputs

- Evaluated AO Next execution candidate: `14c3c8bf96c9a3c8175ba6f4ffea0d45356d9d4e`
- Integrated recovery-evaluator implementation: `530cf9c66336346b3e78f1e96d612f26f64ee793`
- Corpus: `sha256:bec69007369a82303810dced59b4843b651d1d69570ccf1510648d07b6e108f1`
- Model: `gpt-5.6-sol`
- Reasoning effort: `xhigh`
- Trials: three tasks, three variants, three counterbalanced trials per variant
- Valid live rows: 27/27, with nine each for N0, N4, and N7

| Variant | Execution binding | Adapter digest | Runtime digest |
|---|---|---|---|
| N0 | `current-ao-native-v1+ao2-0.5.11+codex-cli-0.147.0` | `sha256:b867159a8236bbf805744da3ae3ee116df2518581d030910c2fb702acc9e149d` | `sha256:e95e157c19f94548196576e8fb8043d3a1f5be22da9b1469ba7d3e06be7e2830` |
| N4 | `native-codex-direct-v1+codex-cli-0.147.0` | `sha256:ae28b7b5d77b225bb04bb8490848780bf624a297dafa229340881f7208c6bc9d` | `sha256:86cb68a244cb688f2130ec50d4aa6ecc6a07a2003957c4d4a5495d3009c05c7a` |
| N7 | `ao-next-process-v1+14c3c8bf96c9+codex-cli-0.147.0` | `sha256:1f94223271862aa376cd32a54ce0c69555dfd0795d34ed47136e125b56507880` | `sha256:8d827f47cab1f2b4ca7aa63036e9af49267c2633ebffb917fa7d60ce4e24cd41` |

N0 represents the exact AO2-backed current-AO execution binding recorded by this evaluation. Earlier N0 measurements remain immutable historical evidence and are not interchangeable with later source, binary, prompt, adapter, tool, or policy bindings.

## Result

| Variant | Median total tokens | Median wall-clock time |
|---|---:|---:|
| N0 | 206,528 | 56,590 ms |
| N4 | 189,993 | 51,495 ms |
| N7 | 12,773 | 20,912 ms |

All 27 task rows succeeded, all hidden-test rates were 100%, and all ten predetermined gates passed. N7 used one worker with no dynamic fan-out and recorded zero unauthorized effects. Its median token use was 93.82% below N0 and 93.28% below N4; median wall-clock time was 63.05% below N0 and 59.39% below N4.

The original immutable live report returned `AO_NEXT_NOT_YET_SUPERIOR` because no measured row exercised recovery. That report was not rewritten. A bounded follow-up repaired the evaluator contract so recovery is not conflated with model repair attempts. The corrected evaluator accepts no caller-authored recovery receipt or digest: it runs deterministic provider-free checkpoint-replay and duplicate-effect probes in-process, binds them to the exact sealed-live corpus and complete N7 adapter set, and emits the derived qualification digest `sha256:759ffd7b8e998f541636eb8b74f9604ee4c93b8aba7449c9808809d5c9436c76`.

The immutable 27 measurements plus that evaluator-owned qualification produce `AO_NEXT_LIVE_EVALUATION_PASSED`. The same comparison without evaluator-owned recovery probes remains `AO_NEXT_NOT_YET_SUPERIOR`.

## Evidence Boundary

- Immutable live-campaign manifest: `sha256:ec28daf282be69eab20e7bbff8892b4c5e20480b7165e4b9358c00809663d807`
- Final repair and integration manifest: `sha256:a9336de4eb811c9a9594bd416559a15dafd249ee5e3e33640c844dea12220b72` (65/65 entries independently verified)
- Provider processes used by the measured comparison: exactly 27
- Provider processes used by repair and reevaluation: zero
- Retries, replacements, extra smoke calls, dynamic fan-out, and unauthorized effects: zero

Raw provider captures, private paths, credentials, and account identifiers remain outside this public repository. This result grants no promotion, release, deployment, publication, migration, production-readiness, or AO replacement authority. A later comparison must mint a new record when any source, binary, model, prompt, adapter, tool, policy, corpus, or verifier binding changes.
