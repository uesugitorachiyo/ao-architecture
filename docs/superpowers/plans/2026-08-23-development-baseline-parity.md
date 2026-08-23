# Development Baseline Semantic Parity Implementation Plan

1. Add failing tests for retained evidence rehashing and each allowed
   normalization's positive and negative boundary.
2. Extend the S04 result with bounded, digest-bound evidence bytes and exact
   host normalization metadata; keep component execution unchanged.
3. Add strict result, parity, and normalization-policy contracts plus the
   independent comparator.
4. Cover missing/extra evidence, manifest/profile mismatch, reused input,
   invalid self-pass, cleanup disagreement, authority widening, and semantic
   drift.
5. Pass focused tests, Architecture verification, public-safety scanning,
   instruction-layout validation, and diff checks; merge through normal review.
6. Produce fresh clean macOS and Windows S04 results, compare them, independently
   rehash the verdict inputs/output, and checkpoint S05 only on parity pass.
