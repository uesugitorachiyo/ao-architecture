# Development Baseline Final Qualification Implementation Plan

1. Add failing evidence-verifier tests for duplicate, missing, extra, size,
   digest, unsafe path, authority, runner, identity, residue, and host-set drift.
2. Implement bounded evidence discovery, independent hashing, semantic closure,
   and deterministic relative-path output.
3. Expose the existing full bootstrap as a local reusable workflow and add the
   read-only final qualification workflow with one comparison/closure job.
4. Update baseline documentation and Architecture instructions for the final
   command and evidence boundary.
5. Pass focused tests, Architecture/public-safety/instruction validation, and
   diff checks; merge through normal review.
6. Dispatch the merged-main final workflow, independently download and rehash
   every artifact, validate the closure record, and checkpoint S06 only on a
   complete green result.
