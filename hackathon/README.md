# AO Stack

AO Stack helps developers run Codex through explicit scope, policy gates,
verification, evidence, and stop conditions.

**OpenAI Build Week category:** Developer Tools

**Demo video:** <https://youtu.be/pGhPooqC3hQ>

## Why it exists

Long-running software agents can produce useful code quickly, but operators
still need a reliable answer to five questions: what was authorized, what ran,
what changed, what passed, and why the system stopped. AO Stack turns those
questions into executable contracts and durable evidence.

## What judges can test

1. **Five-to-ten-minute core test.** Download the released AO2
   `0.5.3` archive, verify its checksum, run a credential-free
   [disposable fixture](fixtures/disposable-judge-demo), and inspect the
   retained execution evidence. AO2
   Control Plane `0.1.18`, AO Mission `0.1.0`, and AO Command
   `0.1.1` are published Tier 1 companion tools; the shortest quick test
   does not require installing them.
2. **Optional full-stack audit.** Give Codex the read-only audit prompt and let
   it inspect all fourteen public repositories, the current-release manifest,
   sixteen compatibility vectors, and their consumer tests.

The quick test exercises the execution-and-observation core. It does not start
all fourteen repositories or prove every production environment.

## Fourteen-repository platform

| Repository | Role |
|---|---|
| [ao-architecture](https://github.com/uesugitorachiyo/ao-architecture) | Source-of-truth contracts, release manifest, and compatibility map |
| [ao-mission](https://github.com/uesugitorachiyo/ao-mission) | Supervises bounded goals and closure |
| [ao-blueprint](https://github.com/uesugitorachiyo/ao-blueprint) | Converts objectives into structured specifications |
| [ao-atlas](https://github.com/uesugitorachiyo/ao-atlas) | Builds and tracks dependency-aware workgraphs |
| [ao-foundry](https://github.com/uesugitorachiyo/ao-foundry) | Selects safe next work from graph state |
| [ao-forge](https://github.com/uesugitorachiyo/ao-forge) | Executes bounded implementation work |
| [ao-covenant](https://github.com/uesugitorachiyo/ao-covenant) | Evaluates authority and policy contracts |
| [ao2](https://github.com/uesugitorachiyo/ao2) | Runs governed local workflows and records evidence |
| [ao2-control-plane](https://github.com/uesugitorachiyo/ao2-control-plane) | Observes and indexes evidence and task-board state |
| [ao-command](https://github.com/uesugitorachiyo/ao-command) | Presents operator-facing readback |
| [ao-arena](https://github.com/uesugitorachiyo/ao-arena) | Supplies evaluation fixtures |
| [ao-crucible](https://github.com/uesugitorachiyo/ao-crucible) | Supplies adversarial and recovery fixtures |
| [ao-sentinel](https://github.com/uesugitorachiyo/ao-sentinel) | Detects unsupported safety and readiness claims |
| [ao-promoter](https://github.com/uesugitorachiyo/ao-promoter) | Records promotion decisions without granting its own authority |

## Build Week extension

AO Stack existed before the submission period. The submitted extension is
bounded by the four released versions below and the immutable AO Architecture
commit linked from Devpost. Work includes stable releases, native Windows
repair and qualification, cross-repository compatibility vectors, operator
workflows, evidence maintenance, controlled dry-run and rollback fixtures, and
an issue-to-draft-PR workflow. Later repository development continues normally
and is not retroactively included in the submitted Build Week delta.

## Releases and platforms

- AO2: `0.5.3` — [release](https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.3)
- AO2 Control Plane: `0.1.18` —
  [release](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18)
- AO Mission: `0.1.0` —
  [release](https://github.com/uesugitorachiyo/ao-mission/releases/tag/v0.1.0)
- AO Command: `0.1.1` —
  [release](https://github.com/uesugitorachiyo/ao-command/releases/tag/v0.1.1)
- Supported judge archives: macOS aarch64, Linux x86_64, and Windows x86_64.
  Linux aarch64 hosts may use the Linux x86_64 archive under explicit Docker
  emulation; AO2 v0.5.3 does not publish a Linux aarch64 archive.
- Quick test credentials: none.

## Judge documents

- [Quick test](JUDGE-QUICKSTART.md)
- [Packaged fixture verification](FIXTURE-VERIFICATION.md)
- [Codex full-stack audit prompt](JUDGE-CODEX-PROMPT.md)
- [Build Week delta](BUILD-WEEK-DELTA.md)
- [How Codex and GPT-5.6 were used](CODEX-AND-GPT-5.6.md)
- [Evidence index](EVIDENCE-INDEX.md)

## Limitations

AO Stack does not independently authorize releases, credential access,
deployment, policy expansion, or external contact. The compatibility evidence
tests defined contracts; it is not a claim that every possible deployment has
been tested. The project does not claim unrestricted self-improvement.
