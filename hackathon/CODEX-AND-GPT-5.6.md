# How Codex and GPT-5.6 Were Used

AO Stack was developed through long-running Codex goals supervised by the
human operator. GPT-5.6-powered agents converted bounded objectives into
implementation and verification work across the fourteen repositories.

Verified uses include:

- cross-repository implementation and contract updates;
- regression tests and repair of authentic failures;
- native Windows diagnosis and portability fixes;
- release qualification across macOS, Linux, and Windows;
- user-facing installation, troubleshooting, and operator documentation;
- evidence reconciliation when an earlier closure was invalid;
- AO Atlas dependency-aware workgraph execution;
- recovery after interruption, worker timeout, and machine-access failures;
- GitHub issue classification and controlled issue-to-draft-PR fixtures;
- preparation of judge instructions, evidence selection, and integrity
  manifests.

Codex did not supply its own authority. The human operator chose roadmaps,
approved bounded scopes, authorized merges and releases, supplied machine
access, and rejected unwanted work. AO Covenant encoded policy boundaries;
AO Mission supervised closure; AO Sentinel checked overclaims; AO Promoter
recorded decisions without granting them.

The result is not “an agent said it passed.” The intended result is a chain
of inspectable objectives, patches, tests, CI results, digests, release
readbacks, and explicit stop conditions.
