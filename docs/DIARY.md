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


### 📅 2026-07-28, Tuesday (v0.2.0 → v0.3.0)
**09:12** | *[MILESTONE]* 
Completed v0.3: Fetch phase vertical slice, with full strategy-level
unit test coverage for both source types (API and DB).

**Fetch strategy tests**
- `DBFetchStrategy`: covered successful multi-row fetch, table-not-found,
  invalid connection URL, and missing table name. Testing surfaced a real
  gap — `NoSuchTableError` was not being caught alongside
  `OperationalError`, allowing a raw SQLAlchemy exception to leak past
  the strategy's error boundary. Fixed by catching both.
- `ApiFetchStrategy`: covered success plus all mapped HTTP status codes
  (400/401/403/404/429/5xx) using `unittest.mock` to simulate `httpx`
  responses without making real network calls.

**Testing infrastructure**
- Adopted fixture composition as the standard pattern for storage and
  strategy tests: shared setup (engine, session, mock responses) is
  defined once per fixture and requested by name where needed.
- Introduced `tmp_path` (file-backed SQLite) for `DBFetchStrategy` tests,
  since the strategy creates its own engine internally and cannot share
  an in-memory (`:memory:`) database with the test's own connection.
- Introduced `unittest.mock` (`patch`, `MagicMock`, `side_effect`) for
  isolating `ApiFetchStrategy` from real HTTP calls.

**Process**
- Continued the feature-branch + PR workflow. DBFetchStrategy and
  ApiFetchStrategy tests were committed separately to keep history
  readable.

**Status**
Both Fetch strategies are now implemented and verified at the unit
level. Decode strategy tests (XmlDecodeStrategy) remain for a future
iteration before the Extract phase begins.


**12:21** | *[FUTURE IDEA]* 
**Configurable canonical/normalized format for Extract phase**
Currently `Extract` strategies hardcode their output to JSON
(`json.dumps(...)`). A `settings.NORMALIZED_FORMAT` constant could
name this choice explicitly, but doesn't yet decouple the actual
serialization logic — every Extract strategy still calls `json.dumps`
directly. Making the format genuinely swappable (e.g. to support a
different canonical structure) would require a serializer injection
layer: something like `settings.NORMALIZED_SERIALIZER` mapping to a
callable (`json.dumps`, or an alternative), which each Extract
strategy would call instead of hardcoding `json`. Not needed now —
noting it as a deferred architectural idea, not a current requirement.


**13:07** | *[MILESTONE]*
Completed v0.4: Decode and Extract phases implemented and fully unit
tested, completing the XML vertical slice from raw source through to
canonical (JSON) transform-ready data.

**Decode phase**
- `XmlDecodeStrategy` (lxml-based) tested: successful parse, and
  malformed XML correctly raising `DecodeMalformedError`.

**Extract phase**
- Clarified the architectural boundary between Extract and Transform:
  Extract performs structural, domain-agnostic conversion only (source
  format → canonical dict, no field selection or business logic).
  Target-format awareness and BLL injection are reserved for Transform,
  which will require an explicit `transform_strategy` with no default
  implementation.
- `XmlExtractStrategy` built on `xmltodict`, converting parsed XML into
  a canonical JSON structure (`TransformableData`). Chose to keep
  `lxml` (syntax validation in Decode) and add `xmltodict` (structural
  conversion in Extract) as separate, purpose-fit dependencies rather
  than forcing one library to do both jobs.
- Renamed `ExtractableFormat` to `ContentFormat` (now shared across
  Decode/Extract/Fetch/Transform, no longer scoped to one phase) and
  added `RegistryEntry.content_format` so Selector and Registry never
  need to infer format by inspecting payload content.
- `ExtractableData.format` renamed to `source_format`; new
  `TransformableData.origin_format` tracks what the canonical JSON was
  originally converted from.
- `XmlExtractStrategy` tested: successful conversion against a real
  sample file. Testing caught a real bug — `xmltodict.parse()` requires
  `str` input, not `bytes`; the strategy was passing raw bytes directly.

**Process**
- `settings.NORMALIZED_FORMAT` introduced as the single source of truth
  for Extract's canonical output format (currently JSON). Noted as a
  deferred idea: true format flexibility would need a serializer
  injection layer, not just a named constant — not needed yet.

**Status**
Fetch, Decode, and Extract phases are now implemented and tested.
Transform and Load remain before the full pipeline (v0.5) is complete.


**14:34** | *[FUTURE IDEA]* 
**Transform strategy installer & registry system**

Currently (and for the rest of v1), Transform strategies follow the
same pattern as all other strategies: a simple `TRANSFORM_STRATEGY_MAP`
dict in `strategies/transform/__init__.py`, selected explicitly via a
`transform_strategy` argument (no auto-detection, since Transform
strategies encode business logic, not just format handling).

This works fine for a single or small number of hand-written
strategies. It won't scale once Transform strategies start being
authored by third parties and "installed" into the project, because:

- Name collisions become possible once strategies aren't all written
  by the same person in the same session
- There's no way to distinguish "built-in" (shipped with Fluxus) from
  "installed" (added later, possibly by someone else) strategies
- There's no tracking of what's actually installed, so `RegistryEntry`
  can't reliably reference *which* strategy (beyond its name string)
  produced a given payload

Deferred design sketch, to revisit in v1.x:
- A `strategy_installer.py` devtool that registers a strategy (name,
  source — built-in vs. installed, maybe file path or package origin)
  into a small catalog (a dedicated table or a structured config file)
- A `settings`/`.env` distinction between built-in and installed
  strategy locations
- Only becomes necessary once there's a real second author of Transform
  strategies — not needed for the v1 single-author, single-strategy
  case.

Deliberately not building this now — v1's priority is a complete,
working pipeline (see ROADMAP.md v0.5) over anticipatory infrastructure
for a scenario that doesn't exist yet.