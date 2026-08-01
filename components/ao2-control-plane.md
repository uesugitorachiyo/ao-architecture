# AO2 Control Plane

**Role:** Observer-only evidence ingest, indexed storage, verification, metrics, and read APIs.

**Maturity:** Late beta for single-node operation. `implemented`, `executable-tested`, `clean-room-rehearsed`.

**Boundary:** Stored evidence is not approval or activation authority.

**Repository:** [uesugitorachiyo/ao2-control-plane](https://github.com/uesugitorachiyo/ao2-control-plane)

**Current public release:** [v0.1.18](https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18), tag target `6257ec23fde726d4a0133c5b62231881fb6aaa9a`.

**Pairing:** AO2 Control Plane v0.1.18 is the supported observer companion for
AO2 v0.5.7. Its published native archives are Linux x86_64, macOS aarch64, and
Windows x86_64. The Control Plane remains optional for the canonical
credential-free AO2 first-use path and never becomes execution or approval
authority.
