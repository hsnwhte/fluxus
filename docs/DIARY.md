### 📅 2026-07-26, Sunday (v0.1.0 → v0.2.0)
**17:00** | *[IMPORTANT REMINDER]* 
In v1, `ApiFetchStrategy` hardcodes the returned data's format as
`ExtractableFormat.JSON`. In reality, the source may return
JSON/XML/text/CSV depending on its `Content-Type` header. We're not
solving this now because v1's vertical slice connects to a single,
known test API (which always returns JSON).

Future work: read `response.headers.get("content-type")` and map it
to the appropriate `ExtractableFormat`. An unknown/unsupported
Content-Type will likely require a new exception
(e.g. `FetchUnsupportedFormatError`).


### 📅 2026-07-27, Monday (v0.1.0 → v0.2.0) 
**17:30** | *[MILESTONE]* 
Completed the v0.2 vertical slice: Fetch and Decode phases working
end-to-end, plus full unit test coverage for the storage layer.

**Fetch & Decode implementation**
- Implemented `ApiFetchStrategy` (httpx) and `DBFetchStrategy` (SQLAlchemy,
  table autoload) — both static methods, normalized output to
  `ExtractableData` (bytes + format enum), keeping Extract phase blind
  to data origin.
- Implemented `XmlDecodeStrategy` (lxml), MVP scope: XML only. CSV/JSON/HTML
  stubbed with TODO, deferred to v0.7.

**Dependency injection cleanup**
- Removed direct instantiation of SQLite backends from `Orchestrator`
  and all `*SQLite` storage classes (`PayloadStoreSQLite`,
  `RegistryStoreSQLite`, `PipelineRunRecordsSQLite`) — these now receive
  a `Session` via constructor injection instead of creating their own.
  Orchestrator remains fully blind to which backend is in use.

**Manual end-to-end verification (devtools)**
- Built `devtools/db_managers/` (init_pipeline_db.py, init_test_dbs.py,
  db_tools.py) to bootstrap and reset local SQLite databases for testing.
- Verified all three working paths manually via `run_orchestrator.py`:
  file→XML decode, API fetch (legislation.gov.uk XML feed, mislabeled as
  JSON — known limitation, see Content-Type detection note), DB fetch
  (SQLite source with a hand-seeded test_table). All three wrote correct
  Registry + Payload entries with correct run_id/phase/strategy_name/
  content_hash/address.

**Unit tests (first real pytest suite)**
- Wrote full coverage for `PipelineRunRecordsSQLite`, `RegistryStoreSQLite`
  (save_entry + all three get_entry_by_* methods), and `PayloadStoreSQLite`
  (save + load).
- Tests caught a real bug: `RegistryEntry.run_id` was defined as
  `mapped_column` (missing `()`) instead of `mapped_column(index=True)` —
  SQLAlchemy silently stored a bound method reference instead of an int,
  which only surfaced as a Pydantic ValidationError when converting to
  `RegistryRecord`. 

**Process notes**
- Adopted feature-branch + PR workflow starting this session (previously
  committed directly to main). PR descriptions carry the detailed
  breakdown; commit messages stay short.
- Confirmed roadmap definition for v0.2 ("Storage layer works... Registry
  functional and tested") is now fully met.