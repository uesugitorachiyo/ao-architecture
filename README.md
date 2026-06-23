# AO Architecture Documentation

![AO stack overview](images/ao-stack-overview.svg)

This repository is a colleague-facing architecture guide for the active AO agent orchestration stack. It explains how the repositories interact, which repository owns each authority boundary, how governed agent work flows through the system, and where to inspect workflows, agents, skills, contracts, and evidence.

## Architecture Video

[![AO Architecture video walkthrough](https://img.youtube.com/vi/P0JbsTKItEA/maxresdefault.jpg)](https://youtu.be/P0JbsTKItEA?si=KYaWmZbymO4kRMlK)

Watch the video walkthrough: [AO Architecture on YouTube](https://youtu.be/P0JbsTKItEA?si=KYaWmZbymO4kRMlK)

## Start Here

1. [Overview](overview/README.md) explains how all repositories interact.
2. [Production Readiness Checklist](overview/PRODUCTION-READINESS.md) explains the quality bar for this documentation pack.
3. Read individual repository guides when you need implementation detail:

| Folder | Guide |
| --- | --- |
| `ao-command` | [AO Command Architecture](ao-command/README.md) |
| `ao-covenant` | [AO Covenant Architecture](ao-covenant/README.md) |
| `ao-forge` | [AO Forge Architecture](ao-forge/README.md) |
| `ao-foundry` | [AO Foundry Architecture](ao-foundry/README.md) |
| `ao2` | [AO2 Architecture](ao2/README.md) |
| `ao2-control-plane` | [ao2-control-plane Architecture](ao2-control-plane/README.md) |

## Visual Map

Shared images are stored in [images](images/). Each repository guide references at least one diagram from this shared folder.

![Evidence-first workflow](images/evidence-flow.svg)

## Documentation Scope

These docs describe the target folders as architecture documentation mirrors. The source repositories inspected are:

| Source repository | Architecture guide |
| --- | --- |
| [ao-command](https://github.com/uesugitorachiyo/ao-command) | [ao-command](ao-command/README.md) |
| [ao-covenant](https://github.com/uesugitorachiyo/ao-covenant) | [ao-covenant](ao-covenant/README.md) |
| [ao-forge](https://github.com/uesugitorachiyo/ao-forge) | [ao-forge](ao-forge/README.md) |
| [ao-foundry](https://github.com/uesugitorachiyo/ao-foundry) | [ao-foundry](ao-foundry/README.md) |
| [ao2](https://github.com/uesugitorachiyo/ao2) | [ao2](ao2/README.md) |
| [ao2-control-plane](https://github.com/uesugitorachiyo/ao2-control-plane) | [ao2-control-plane](ao2-control-plane/README.md) |

The documentation does not copy every source README. It extracts the operational model colleagues need: role, architecture, workflows, agent boundaries, skills or capabilities, contracts, evidence, and production-readiness expectations.
