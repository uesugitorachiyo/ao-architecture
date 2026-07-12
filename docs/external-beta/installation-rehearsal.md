# Installation Rehearsal

1. Use a disposable directory with no AO environment variables or credentials.
2. Clone the exact manifest heads.
3. Build with repository-native Go, Rust, or Python tooling already declared by
   each repository. Do not update dependencies.
4. Run help, version, fixture, and dry-run commands only.
5. Run the cross-repository preflight verifier.
6. Delete the disposable directory after recording command status and duration.

Pass means clean checkouts build and local verification succeeds without live
provider, release, deployment, publication, or credential behavior.

