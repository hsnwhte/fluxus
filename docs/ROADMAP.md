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

v0.6 -- [DONE] ALPHA release: CLI interface complete (interfaces/cli).
        Selector/Factory mechanism generalized (not hardcoded to
        the v0.5 path). Devtools inspect tool functional.

v0.7 -- Extended content format strategies: CSV, HTML, DOCX,
        XLSX, and PDF sources added (Decode + Extract), proving the
        "new strategy = new file, not new architecture" claim.
        API Content-Type detection implemented (ApiFetchStrategy now
        reads the real Content-Type header instead of assuming JSON;
        raises explicitly if the header is missing/unrecognized).
        DB-side dialect support confirmed via SQLAlchemy's own
        abstraction — no new strategy code required, only verification
        against a non-SQLite dialect.
        Test coverage extended for each new format. Manual end-to-end
        verification via devtools.
        PipelineRunRecord is extended to include status.        

        FetchCache implemented: Fetch strategies check FetchCache 
        by content hash before hitting the source, and write to it 
        after a successful fetch.

        OCR and Attachment support considered and deliberately dropped:
        both are domain-specific business logic (image-to-text,
        file-reference tracking), not engine-level concerns. Belongs
        in downstream Transform strategies or domain frameworks
        (e.g. a QMS layer), not in Fluxus core. See DIARY.md.

v0.75 -- PostgreSQL storage backend added alongside SQLite (new
         StorageBackend implementation via SQLAlchemy): Proves
         storage layer is swappable, not just extensible on the
         strategy side. Separate, isolated practice repo
         (postgres-playground) for PL/pgSQL triggers, RPC
         functions, and RLS policies — documented, not part of
         Fluxus's core codebase.
         DB rollback safety across a run added.
        

v0.8 -- CI pipeline (GitHub Actions) set up: tests run on push.
        Optional dependency groups (sql, api, dev) verified to 
        work in isolation. Error handling audited (no bare 
        Exception/ValueError anywhere). Logging finalized across 
        all processors. 


v0.9  -- BETA release: README complete (setup, architecture,
         rationale). 
         Published to PyPI (pip install fluxus becomes real).

         Real-consumer validation: fluxus-ncr's first TransformStrategy
         (Excel source) implemented and run end-to-end against Fluxus
         as an external dependency (pip install, not copy-pasted code).
         Any friction/gaps found this way get fixed in Fluxus core,
         not worked around in fluxus-ncr.

         Consistency review, concrete checklist:
         [ ] Every public function/class has a docstring
         [ ] Every raised exception uses the custom hierarchy (grep for
           bare "raise Exception" / "raise ValueError" returns nothing)
         [ ] Every strategy file follows the same internal structure
           (same method names/order as the reference strategy)
         [ ] Error messages follow a consistent format (what failed,
           what value, what was expected)

v1.0 -- Full release: portfolio-ready. Documented, tested,
        demonstrably extensible. Public-facing polish complete.