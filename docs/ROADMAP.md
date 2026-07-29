v0.1 -- [DONE] Project scaffolding complete. src layout, pyproject.toml,
        .gitignore, docs/ set up. Core Pydantic DTOs and exception
        hierarchy defined. No working logic yet.

v0.2 -- [DONE] Storage layer works. StorageBackend Protocol defined,
        SQLiteStorage reference implementation complete. Registry
        (hash-based lineage tracking) functional and tested.

v0.3 -- [DONE] First vertical slice, fetch side: API source strategy
        implemented. Fetcher processor calls it, writes to
        phase-1 storage via registry. Unit tests pass.

v0.4 -- [DONE] First vertical slice, decode/extract side: XML decode +
        extract strategy implemented. Data reaches phase-2 storage
        in canonical format. Unit tests pass.

v0.5 -- [DONE] First vertical slice, transform + load side: Transformer
        + Database (SQLAlchemy-based) load strategy implemented.
        End-to-end pipeline runs: API source -> DB target,
        fully working, fully tested.

v0.6 -- ALPHA release: CLI interface complete (interfaces/cli).
        Selector/Factory mechanism generalized (not hardcoded to
        the v0.5 path). Devtools inspect tool functional.

v0.7 -- Second and third strategies added per stage (CSV, JSON
        sources; DB-side fetch strategy), proving the
        "new strategy = new file, not new architecture" claim.
        Test coverage extended for each.

v0.8 -- CI pipeline (GitHub Actions) set up: tests run on push.
        Error handling audited (no bare Exception/ValueError
        anywhere). Logging finalized across all processors.

v0.9 -- BETA release: README complete (setup, architecture,
        rationale). Code review pass for consistency. Optional
        dependency groups (sql, api, dev) verified to work in
        isolation.

v1.0 -- Full release: portfolio-ready. Documented, tested,
        demonstrably extensible. Public-facing polish complete.