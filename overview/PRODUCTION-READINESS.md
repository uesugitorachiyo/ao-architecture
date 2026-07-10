# Documentation Production Readiness

![Authority boundaries](../images/authority-boundaries.svg)

This checklist defines what "production-ready documentation" means for the `ao-architecture` repository. It is designed for colleagues who need to trust the docs as an explanation of the active AO orchestration stack.

This is a documentation-readiness checklist. It does not certify runtime or product readiness. Runtime behavior, security, contract compatibility, and release readiness must be established by the owning repositories and integrated verification.

## Coverage Scorecard

| Requirement | Status | Evidence |
| --- | --- | --- |
| Top-level entrypoint exists | Complete | `../README.md` |
| Cross-repository overview exists | Complete | `README.md` |
| Every target repository folder has documentation | Complete | `../ao-mission`, `../ao-blueprint`, `../ao-atlas`, `../ao-command`, `../ao-covenant`, `../ao-forge`, `../ao-foundry`, `../ao2`, `../ao2-control-plane`, `../ao-arena`, `../ao-crucible`, `../ao-sentinel`, `../ao-promoter` |
| Every document contains or references an image | Complete | Each README includes an SVG from `../images` or `images` |
| Shared images live in the requested images folder | Complete | `../images/*.svg` |
| Overview explains repository interaction | Complete | `README.md` repository map, practical rule, workflows, and agent roles |
| Repository docs cover architecture | Complete | Each repo guide has an Architecture section |
| Repository docs cover workflows | Complete | Each repo guide has a Workflows section |
| Repository docs cover agents or skills | Complete | Each repo guide has an Agent Roles And Skills section |
| Repository docs cover contracts and evidence | Complete | Each repo guide has a Contracts And Evidence section |
| Repository docs cover boundaries | Complete | Role, interactions, and production-readiness sections |
| Verification commands are listed | Complete | Quick Verification section in each repository guide |

## Quality Bar

Production-ready, for this documentation set, means:

- the docs are grounded in the inspected sibling repositories rather than invented from repository names alone;
- every repository has an explicit role and non-role;
- workflows are described as evidence-first sequences;
- diagrams are stored in `architecture/images`;
- terms are consistent across documents: Command shows, Atlas compiles stack-instance workgraphs, Foundry coordinates, Forge decides factory steps, Covenant gates trust, AO2 executes, control-plane observes, Arena scores, Crucible hardens, Sentinel monitors, Promoter activates;
- every guide gives colleagues enough source paths to continue investigation;
- readiness-loop docs explain the stop-oriented exit gate and keep blockers separate from maintenance suggestions;
- dangerous authority drift is called out directly.

## Known Assumptions

The target folders started as empty documentation folders. The implementation details in these guides were extracted from sibling source repositories and mapped to the public GitHub repositories linked from the top-level README.

Where a guide describes future direction, it uses wording from the source repository docs and keeps the current authority boundary explicit.

## Maintenance Process

When any source repository changes a boundary, release workflow, provider adapter, policy gate, readiness exit condition, or evidence contract:

1. Update the matching repository guide.
2. Update [README.md](README.md) if cross-repository interaction changes.
3. Update or add SVG diagrams in `../images`.
4. Run the verification commands from the changed source repository when practical.
5. Re-run the documentation checks listed below.

## Documentation Checks

Run from `architecture`:

```sh
find . -name '*.md' -print
find images -name '*.svg' -print
grep -R "](../images/" ao-command ao-covenant ao-forge ao-foundry ao2 ao2-control-plane overview
grep -R "](../images/" ao-atlas ao-arena ao-crucible ao-sentinel ao-promoter
grep -R "Agent Roles And Skills" ao-atlas ao-command ao-covenant ao-forge ao-foundry ao2 ao2-control-plane ao-arena ao-crucible ao-sentinel ao-promoter
grep -R "Contracts And Evidence" ao-atlas ao-command ao-covenant ao-forge ao-foundry ao2 ao2-control-plane ao-arena ao-crucible ao-sentinel ao-promoter
grep -R "readiness exit gate" ao-foundry ao2 overview
python3 scripts/verify_architecture.py
```

The final verification pass for this documentation pack should also confirm that every Markdown image target exists and every SVG is parseable XML.
