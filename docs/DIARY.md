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


**19:58** | *[STATUS TRACKER]* 
### Fluxus capability matrix (source_format × target_format)

Source codes: db_json, api_json, api_xml, api_csv, api_html, file_xml, file_json, file_csv, file_html
(db_xml/db_csv/db_html don't exist — DB fetch has no format choice)

Target codes: db, api_json, api_xml, api_csv, api_html, file_json, file_xml, file_csv, file_html

| Src\Trg | db     | a_json | a_xml | a_csv | a_html | f_json | f_xml | f_csv | f_html |
|---------|--------|--------|-------|-------|--------|--------|-------|-------|--------|
| db      | [DONE] | [ ]    | [ ]   | [ ]   | [ ]    | [DONE] | LTD** | LTD** | LTD**  |
| a_json  | LTD**  | [ ]    | [ ]   | [ ]   | [ ]    | [DONE] | LTD** | LTD** | LTD**  |
| a_xml   | [DONE] | LTD**  | LTD** | LTD** | LTD**  | LTD**  | LTD** | LTD** | LTD**  |
| a_csv   | LTD**  | LTD**  | LTD** | LTD** | LTD**  | LTD**  | LTD** | LTD** | LTD**  |
| a_html  | LTD**  | LTD**  | LTD** | LTD** | LTD**  | LTD**  | LTD** | LTD** | LTD**  |
| f_xml   | [ ]    | [ ]    | [ ]   | [ ]   | [ ]    | [ ]    | [ ]   | [ ]   | [ ]    |
| f_json  | TODO*  | TODO*  | TODO* | TODO* | TODO*  | TODO*  | TODO* | TODO* | TODO*  |
| f_csv   | TODO*  | TODO*  | TODO* | TODO* | TODO*  | TODO*  | TODO* | TODO* | TODO*  |
| f_html  | TODO*  | TODO*  | TODO* | TODO* | TODO*  | TODO*  | TODO* | TODO* | TODO*  |

TODO: CsvDecodeStrategy, JsonDecodeStrategy, HtmlDecodeStrategy are
stubbed, not implemented (planned v0.7). file_json specifically needs
a DecodeStrategy for JSON files (distinct from JsonExtractStrategy,
which handles already-decoded JSON content, not raw file reading).

LTD: ApiFetchStrategy always labels source_format as JSON regardless
of actual Content-Type. Real XML/CSV/HTML API responses will fail at
Extract (JsonExtractStrategy chokes on non-JSON content) unless/until
Content-Type-based detection is implemented (see earlier diary note).

Note: db_xml / db_csv / db_html do not exist as source combinations —
DBFetchStrategy has no format selection; it always produces real JSON
from table rows (not a limitation, just a different mechanism).

**Note on Transform testing:** All LTD results above used
`SamplePassthroughTransformStrategy`, which does not perform real
format conversion — content passes through unchanged regardless of
`target_format`. This means only target_format=JSON combinations
represent a true end-to-end validation; XML/CSV/HTML targets marked
OK only confirm the pipeline *mechanism* works, not that real format
conversion happens (no Transform strategy implements that yet).

Extract side: JsonExtractStrategy and XmlExtractStrategy are implemented.
CsvExtractStrategy and HtmlExtractStrategy remain stubbed (v0.7).


### 📅 2026-07-29, Wednesday (v0.4 → v0.5)
**07:51** | *[FUTURE IDEA - for Beta version]*
**Input/output consistency checks (file extension vs. target_format)**

Currently, Fluxus does not validate that a user-provided `target_address`
file extension matches the chosen `target_format`. For example, a user
can set `target_format=JSON` while `target_address` ends in `.xml` —
the file will be written with the correct (JSON) content, but a
misleading extension. This is a deliberate v1 choice (the user is
expected to provide the full, correct path — no auto-inference), but
it's a real usability gap: nothing warns the user their file naming
doesn't match the actual content.

Similarly worth revisiting together: broader input/output sanity checks
in general — e.g. confirming `source_address` actually points to
something reachable before running the full pipeline, or surfacing a
clear warning (not necessarily an error) when address/format mismatches
like this are detected.

Deferred to Beta: this is a UX/safety-net improvement, not a core
pipeline correctness issue — the pipeline itself works correctly
regardless of the misleading filename.

**14:48** | *[MILESTONE]*
**v0.5 complete: full pipeline, Fetch through Export/Load, tested end-to-end**

**New implementations**
- `JsonExtractStrategy`, `JsonDecodeStrategy` — completed the JSON leg
  of the pipeline (validation-only, content passed through unchanged,
  consistent with the "Extract stays lossless" principle)
- `TransformStrategyProtocol` — deliberately broken from the static-method
  pattern used everywhere else: takes `__init__(target_format, data)`,
  parameterless `transform()`. Rationale: Transform carries business logic
  (target-format-aware conversion, injected by the user via
  `transform_strategy_name`), unlike Fetch/Decode/Extract/Load/Export,
  which are pure format/protocol handlers with no default implementation
  needed. Documented as an intentional protocol asymmetry.
- `SamplePassthroughTransformStrategy` — a demo strategy proving the
  mechanism works end-to-end; does not perform real format conversion.
  Included in `TRANSFORM_STRATEGY_MAP` under an explicitly named
  `sample_` key so it can never be mistaken for a production default.
- `LoadStrategyProtocol` / `ExportStrategyProtocol`, `DBLoadStrategy`,
  `ApiLoadStrategy`, `ExportStrategy` — Load is the mirror of Fetch
  (API/DB, target-aware), Export is the mirror of Decode (file-based).
  Export ended up format-independent (single strategy handles all
  formats, since it never interprets content) once `target_format`
  was scoped out of its responsibility.
- `MimeType` enum (HTTP `Content-Type` values) kept deliberately separate
  from `ContentFormat` (internal format representation) — different
  concerns, mapped via a small dict inside `ApiLoadStrategy` rather than
  merged

### 📅 2026-07-30, Thursday | *[MILESTONE / KNOWN LIMITATION]*
**Devtools CLI and manual test infrastructure built**
**06:55** | *[MILESTONE]* 
Built out the devtools CLI (`fluxus-dev`, via `python -m devtools.main`)
mirroring the production `fluxus` CLI's `run` command, plus supporting
tooling:
- `db_tools.py`: engine/session helpers, `reset_table`
- `setup-test-env` / `reset-test-env` commands to bootstrap and tear
  down dev pipeline/source/target databases
- `TestPackage` dataclass + `TEST_PACKAGES` catalog (`test_packages.py`),
  injectable via `test --test-pack <key>`, so full InputArgs
  combinations can be replayed with a single number instead of
  re-typing 8 CLI flags each time
- Real test data downloaded (jsonplaceholder.typicode.com/comments —
  500 nested records) for realistic-scale manual testing

**Test 1 (file→file, comments.json→output.json) passed.**

**Test 2 (file→db, comments.json→dev_target_data_text) surfaced a
known/expected limitation:** `DBLoadStrategy` uses source JSON keys
directly as target column names. Since `SamplePassthroughTransformStrategy`
performs no field mapping, the source's field names (`postId`, `id`,
`name`, `email`, `body`) don't match the target table's schema (`id`,
`data`) — result: `IntegrityError: NOT NULL constraint failed:
dev_target_data_text.data`.

This is not a bug — it's confirmation that Transform must own field
mapping/schema adaptation, exactly as designed. A real Transform
strategy (not passthrough) is required whenever source and target
schemas differ. Serves as a concrete demonstration of why Transform
carries business logic and has no default implementation.

**08:59** | *[MILESTONE]* 
**All 9 source × target type combinations manually verified end-to-end**

Completed the full manual test matrix (FILE/DB/API × FILE/DB/API) via
the devtools CLI's injectable TestPackage catalog. All 9 combinations
now pass.

**Real bugs found and fixed along the way:**

- `DBLoadStrategy` produced `INSERT ... DEFAULT VALUES` (and a
  resulting `IntegrityError`) when given an empty `rows` list —
  SQLAlchemy interprets an empty parameter list for `executemany` as
  "insert one row with no values" rather than "insert nothing." Fixed
  with an explicit empty check; logs a `WARNING` (not an error) since
  an empty source is a valid, if noteworthy, condition — not a failure.
- `JsonExtractStrategy` assumed all JSON sources are lists. API sources
  that return a single resource (e.g. `GET /todos/1`) return a bare
  JSON object instead. Since the internal canonical format is always
  `list[dict]`, added a wrap-into-single-element-list step for bare
  objects.
- Confirmed (again, via a fresh source/target combination) that
  `SamplePassthroughTransformStrategy` fails whenever source and target
  field names don't match — this is expected, not a bug, and is exactly
  why Transform requires real business logic per use case. Wrote a
  second devtools-only sample strategy (field mapping for the
  `comments` shape) to demonstrate a working non-passthrough Transform.

**Process note:** chose to reuse a compatible source (`/comments/1`
instead of `/todos/1`) rather than write a third mapping strategy for
a single test case — pragmatic reuse over unnecessary strategy
proliferation.

**Status:** devtools CLI, TestPackage injection, and the full
combination matrix are now a reliable foundation for regression-testing
future changes to the pipeline.