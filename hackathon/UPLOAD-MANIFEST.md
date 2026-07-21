# Judge Upload Manifest

Planned archive: `ao-stack-openai-build-week-judge-package.zip`

SHA-256: `recorded in excluded finalizer evidence after deterministic ZIP build`

Maximum Devpost upload size: 35 MB.

Include:

- judge landing and all judge documents;
- disposable discount-service fixture;
- three selected AO Stack images;
- frozen public release metadata and checksums;
- final Build Week inventory;
- link and integrity manifests.

Exclude:

- `.git` directories and worktrees;
- source repository build outputs or caches;
- binary release archives;
- model files, frameworks, and generated dependencies;
- Devpost source HTML or form authenticity values;
- credentials, tokens, private paths, machine identifiers, and raw local
  evidence dumps.

The finalizer must build the ZIP from a sanitized copy, confirm it is below
35 MB, enumerate every file and SHA-256, scan extracted contents, and verify
that every release binding except an explicitly operator-pending public video
URL has been removed.
