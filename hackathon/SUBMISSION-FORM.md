# Devpost Submission Answers

## Fixed fields

- Submitter Type: `Individual`
- Country of Residence: `United States`
- Category: `Developer Tools`
- Project name: `AO Stack`
- Public code repository:
  `https://github.com/uesugitorachiyo/ao-architecture`
- Judge landing page:
  `https://github.com/uesugitorachiyo/ao-architecture/tree/main/hackathon`
- Feedback Session ID: `pPCxHdag21JtfP1MjP7cIA`

## Testing instructions

Open the [AO Stack judge landing page](https://github.com/uesugitorachiyo/ao-architecture/tree/main/hackathon).
Start with `JUDGE-QUICKSTART.md`. It downloads the public AO2
`0.5.3` archive, verifies its published checksum, extracts it into a
disposable directory, runs `version` and `doctor`, and exercises a bundled
credential-free fixture. It does not rebuild source or modify an existing
repository. The optional `JUDGE-CODEX-PROMPT.md` performs a read-only audit of
all fourteen repositories and their compatibility contracts.

## Installation and supported platforms

AO2 `0.5.3` provides public archives for macOS aarch64, Linux
x86_64, and Windows x86_64. Follow the platform block in
`JUDGE-QUICKSTART.md`; it verifies published checksums before execution.
AO2 Control Plane `0.1.18` is an optional observer and is
not required for the shortest test.

## Credentials

No credentials are required for the quick test. Do not add provider tokens.
The optional public-repository audit uses only public GitHub reads.

## Additional judge upload

Upload `ao-stack-openai-build-week-judge-package.zip`. Its SHA-256 is
`recorded in excluded finalizer evidence after deterministic ZIP build`. It contains the judge documents, disposable
fixture, selected architecture media, integrity manifest, and no credentials
or build artifacts.

## Public video

`https://youtu.be/pGhPooqC3hQ`

The operator supplied this updated public YouTube URL. The finalizer verified
that the URL resolves before this answer is submitted.

## Personal or consent fields

Only the supplied submitter type and country are prepared here. Any other
legal, demographic, consent, or organizer-only answer remains a direct
operator decision.
