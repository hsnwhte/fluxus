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


**11:09** | *[FUTURE IDEA]*
**Third-party strategy dependency management**

Installed Transform strategies may import libraries not part of
Fluxus's own dependency set (e.g. `pandas`). `install_strategy()`
copies the file but does not manage its dependencies — if the
strategy's own imports aren't already installed in the environment,
loading it will fail with a standard `ImportError`/`ModuleNotFoundError`.

Deliberate v1 choice: the strategy author is responsible for
documenting and the user for installing any extra dependencies their
custom strategy needs. No `requirements.txt`-per-strategy mechanism,
no automatic pip install. Revisit only if this becomes a real friction
point once third-party strategies actually exist.

**11:50** | *[MILESTONE] (v0.5.0 → v0.6.0)* 
**v0.6 complete: CLI, logging, generalized Selector, and a real
Transform strategy installer**

**CLI (`fluxus`)**
- `run` command wired to full pipeline, Typer-based, tip-annotated
  parameters with short flags
- Callback-based shared setup (`--debug` now applies to every command,
  not duplicated per-command)
- `ValidationError`/`FluxusError` caught at the CLI boundary, clean
  user-facing messages instead of raw tracebacks

**Logging**
- `logging_config.py`: console handler (INFO+) always on, file handler
  (DEBUG+, UTF-8) added when `--debug` is passed
- Orchestrator now logs phase-level progress (start/success per phase,
  strategy used, exceptions logged before re-raising)
- Deliberately stopped at Orchestrator-level logging — deeper,
  per-strategy logging remains scoped to v0.8

**Selector/Factory generalization**
- Confirmed: all six `get_*_strategy` methods already follow the same
  map-lookup + `StrategyNotFoundError` pattern. This roadmap item was
  effectively already satisfied by consistently applying the same
  pattern each time a new phase (Transform, Load, Export) was added.

**Devtools**
- `fluxus-dev` CLI mirrors `run`, plus `setup-test-env`,
  `reset-test-env`, `inspect` (pretty-prints a payload's JSON content —
  DB Browser shows raw BLOBs, this decodes them)
- `TestPackage` catalog + `--test-pack` injection: all 9 source×target
  combinations replayable by number
- Two real edge-case bugs found and fixed: empty `rows` list caused
  `DBLoadStrategy` to attempt `INSERT ... DEFAULT VALUES` (now skipped
  with a `WARNING` log); API sources returning a bare JSON object
  instead of a list broke the `list[dict]` canonical assumption (now
  wrapped)

**Transform strategy installer (originally scoped to v1.x, completed
early)**
- Transform strategies are now referenced by **numeric id**, not name.
  Id `0` is the built-in passthrough — permanent, cannot be
  uninstalled.
- `fluxus install-strategy --path <file>`: validates the file (exactly
  one class named `TransformStrategy*`, and — via a newly
  `@runtime_checkable` `TransformStrategyProtocol` — an `isinstance`
  check that it actually implements the required methods), then copies
  it into `strategies/transform/installed/` under a standardized name
  and assigns the next available id.
- `fluxus uninstall-strategy --id <n>`: removes the file from disk.
  `TRANSFORM_STRATEGY_MAP` is rebuilt from the `installed/` folder on
  every process start, so there's no separate registry to keep in
  sync — the filesystem *is* the source of truth.
- `fluxus show-strategies`: lists all currently installed ids.
- Scoped out (see earlier diary note, still valid): no dependency
  management for what an installed strategy itself imports.

**Documentation**
- `README.md`: minimal Alpha-stage version — install, usage, how to
  write and install a Transform strategy, honest known-limitations list
- `LICENSE`: MIT

**Status**
v0.6 fully complete. Alpha release conditions (per original roadmap)
met: CLI, generalized Selector, functional devtools inspect tool — plus
a working plugin-style installer well ahead of its original v1.x
schedule.


### 📅 2026-07-31, Friday (v0.6 -> v0.7) 
**13:54** | *[RESOLVE]*
**v0.7 scope progress — new format strategies, API Content-Type
detection, Attachment/OCR dropped**

Decode + Extract implemented for CSV, HTML, DOCX, XLSX, PDF. Each
Decode strategy stays minimal (validate + carry raw bytes); each
Extract strategy converts to a canonical structure — `list[dict]` for
CSV/PDF, raw `xmltodict`-parsed nested dict for XML/HTML, and (after
reconsidering `python-docx`/`openpyxl` vs. raw-XML-via-zipfile) a full
`{filename.xml: <parsed>}` dict per internal ZIP member for DOCX/XLSX.
Deliberately chose the "lossless but raw" approach over
library-mediated output for DOCX/XLSX — reasoning: Fluxus is a young
engine, Transform strategies are still few, but each one written adds
a reference example that makes the next easier. The library-mediated
route would have been easier short-term but hides structure Transform
might need.

`ApiFetchStrategy` now reads the actual `Content-Type` response header
instead of assuming JSON. Added `content_format_to_mime` /
`mime_to_content_format` in `helpers.py`, mapping by enum member name
(both enums share member names for shared formats) rather than a
hand-maintained dict — image mime types (PNG/JPEG) intentionally have
no `ContentFormat` counterpart and raise cleanly if looked up. Missing
or unrecognized Content-Type headers raise explicitly rather than
silently defaulting to JSON — deliberate choice, may revisit if this
proves too strict in practice.

Confirmed DB-side dialect support requires no new strategy code —
SQLAlchemy's dialect abstraction already handles it, same principle
established back when SQLite was first chosen. Only verification
against a real non-SQLite dialect remains open.

**Dropped: Attachment/AttachmentRef and OCR.** Both were explored in
some depth (DTO/ORM drafts for Attachment, considered as `v0.7`/`v0.75`
scope) before recognizing they're domain-specific business logic, not
engine responsibilities — a parser/sync engine doesn't need to
"understand" attachments as a first-class concept when it can already
carry arbitrary binary content through the existing pipeline. Belongs
in a downstream Transform strategy or a domain-specific framework
(e.g. a future QMS layer), not Fluxus core. Good instance of catching
scope creep mid-design rather than after building it.

**Remaining before v0.7 is done:** devtools extension for new formats,
Selector-side fixes, pytest coverage for all new strategies, full
manual end-to-end verification. Not detailing further here — tracked
in progress, not this entry.

### 📅 2026-08-03, Monday
**15:12** | *[FUTURE IDEA — post-v1.0]*
**fluxus-llm: a lightweight LLM API tool for Transform strategies**

Idea: a separate, small companion package (not part of Fluxus core)
that gives Transform strategy authors an easy way to call LLM APIs
(OpenAI, Anthropic, etc.) from within a strategy — e.g. summarizing,
classifying, or enriching data mid-transform.

Scope stays deliberately narrow: this is a *tool* a Transform strategy
can call, not a new pipeline capability. Fetch/Decode/Extract/Load/
Export stay untouched; Transform still only talks to the runtime DB,
nothing changes architecturally. The tool would expose a small set of
convenience methods so a Transform strategy just passes kwargs and
gets a result back, without the strategy author needing to hand-roll
HTTP requests, retries, or provider-specific request shapes.

Two motivations: (1) learning how to properly manage LLM API requests
(rate limiting, retries, provider differences) in a small, isolated
scope rather than a large one; (2) keeping it a genuinely light,
optional companion — not a dependency Fluxus core ever needs.

Not scoped into any current roadmap version — revisit after v1.0.


**17:09** | *[RESOLVE]*
**Transform strategy identity — class name isn't a reliable enough
lineage record**

While manually testing v0.7, noticed `RegistryEntry.strategy_name`
stores the Transform strategy's class name. Realized this isn't a
strong enough identifier long-term: numeric strategy ids (used to
select a strategy at runtime) can shift across install/uninstall, and
class names aren't guaranteed unique between strategy authors. Neither
is a stable, unique reference for lineage purposes.

Idea: assign each installed strategy a persistent unique identifier
(UUID7 — time-sortable, so ids remain roughly ordered by install time)
at install time, store it alongside the class name in the registry.
Deferred to v0.75, not urgent for v0.7's own scope.

**17:56** | *[TODO v0.8]* 
**Transform failures need a generic hint, even without knowing the cause**

Manually testing a mismatched strategy (csv source, comments-shaped
Transform strategy) produced a bare `KeyError: 'id'` traceback — correct
behavior, but not helpful to a user seeing it for the first time.
Fluxus can't know why a Transform strategy failed (it's entirely
user-authored), but it can wrap Transform exceptions with a generic,
non-specific hint — e.g. "Transform strategy raised an error; check
that the strategy matches the shape of the data it receives" — without
pretending to diagnose the actual cause. Add during v0.8's error
handling audit.

**18:24** | *[RESOLVE]*
**DevTargetDataBlob left untested — no current strategy produces bytes**

All manual test packages so far load into `dev_target_data_text`
(TEXT column). `dev_target_data_blob` (BLOB) has never been exercised,
because every Transform strategy written so far (passthrough, and the
comments-shaped mapper) produces `str` values, not `bytes`. Not adding
a test for it now — would require writing a Transform strategy purely
to exercise an untested table, not because of a real need. Revisit if
a real use case for binary output through DB Load ever comes up.


### 📅 2026-08-04, Tuesday
**06:34** | *[RESOLVE]*
**Canonical format definition corrected**

Found a stale comment (in JsonExtractStrategy) claiming the internal
canonical format is always `list[dict]`. That was only ever true for
CSV/JSON/PDF. XML/HTML (xmltodict-parsed) produce a nested dict; DOCX/
XLSX produce a dict keyed by internal zip member filename. The correct
definition: canonical format is any JSON-serializable `list` or
`dict` — the outer shape follows the source format's own natural
structure, not a fixed list-of-records shape. Corrected the misleading
comment.

**10:14** | *[MILESTONE v0.7 COMPLETE]*
**v0.7 complete: format strategies, FetchCache, RunStatus, dialect
verified, 102 tests passing**

**Format strategies** — Decode + Extract implemented and tested for
CSV, HTML, DOCX, XLSX, PDF (JSON and XML already existed, extended
with consistent error handling). Confirmed the "new strategy = new
file, not new architecture" claim holds across five new formats.
Canonical Extract output redefined mid-session: not always
`list[dict]` as an earlier comment claimed, but any JSON-serializable
`list` or `dict` — the outer shape follows the source format's own
structure (CSV/JSON/PDF produce lists of records, XML/HTML produce
nested dicts, DOCX/XLSX produce a dict per internal zip member).

**API Content-Type detection** — `ApiFetchStrategy` now reads the real
`Content-Type` header instead of assuming JSON; raises explicitly if
missing or unrecognized. `helpers.py` gained
`content_format_to_mime`/`mime_to_content_format`, mapped by shared
enum member names rather than a hand-maintained dict.

**FetchCache implemented** — keyed by `api_url` (not content hash,
which isn't known before a fetch happens), scoped to API sources only.
Checked before fetching, written after a successful fetch.

**RunStatus tracking** — `PipelineRunRecord` extended with `status`
(RUNNING/COMPLETE/INTERRUPTED), `interrupted_phase`,
`interrupted_after_entry_id`. `Orchestrator.run()` wrapped in try/except,
updates status on both success and failure paths.

**OCR and Attachment support dropped** — both explored in some depth
(DTO/ORM drafts for Attachment) before recognizing they're
domain-specific business logic, not engine responsibilities. A good
catch of scope creep mid-design.

**Real bugs found and fixed:**
- `RegistryStoreSQLite.get_entry_by_run_id`/`get_entry_by_hash`
  referenced a non-existent `payload_address` attribute (should be
  `address`) — would have raised AttributeError on any real call
- `.htm` extension wasn't recognized by Selector's decode map
- `HtmlDecodeStrategy`/`XmlDecodeStrategy` didn't catch `OSError`,
  so missing files raised raw lxml errors instead of
  `DecodeSourceFileNotFoundError`
- `DBLoadStrategy` empty-rows edge case (INSERT DEFAULT VALUES) —
  found during v0.7's own manual testing, fixed with an explicit
  empty check + WARNING log

**DB dialect support confirmed for real** — installed Docker Desktop,
ran a PostgreSQL container, verified `DBFetchStrategy` works completely
unmodified against it. Closes the one roadmap item that had been
sitting on a theoretical claim ("SQLAlchemy handles this") rather than
actual verification.

**Testing:** 77 automated (pytest) + 25 manual (devtools) = 102 tests
passing. New `docs/TEST_REPORT.md` created as a standalone,
externally-reviewable verification log, separate from ROADMAP/DIARY.

**Deferred to v0.75:** Transform strategy identity (UUID7 per
installed strategy), DB rollback safety across a run, Docker Compose
setup for reproducible PostgreSQL dev environment.

**Status:** v0.7 fully complete, all consistency-review checklist
items confirmed.

**10:31** | *[NOTE]* 
### Capability matrix v2 (2026-08-03) — DONE / TODO only

Superseded the earlier DONE/LTD/TODO matrix. Since API Content-Type
detection now works correctly, no source/target combination is
architecturally blocked anymore — everything remaining is either
untested or requires a Transform strategy that doesn't exist yet
(e.g. one producing XML/CSV/HTML instead of JSON). Both are TODO,
not a hard limitation.

| Src\Trg | db     | a_json | a_xml | a_csv  | a_html | f_json | f_xml | f_csv | f_html |
|---------|--------|--------|-------|--------|--------|--------|-------|-------|--------|
| db      | DONE   | DONE   | TODO* | TODO*  | TODO*  | DONE   | TODO* | TODO* | TODO*  |
| a_json  | DONE   | DONE   | TODO* | TODO*  | TODO*  | DONE   | TODO* | TODO* | TODO*  |
| a_xml   | DONE*  | DONE   | TODO* | TODO*  | TODO*  | TODO   | TODO* | TODO* | TODO*  |
| a_csv   | DONE*  | DONE   | TODO* | TODO*  | TODO*  | DONE   | TODO* | TODO* | TODO*  |
| a_html  | DONE*  | DONE   | TODO* | TODO*  | TODO*  | TODO   | TODO* | TODO* | TODO*  |
| f_xml   | DONE*  | DONE   | TODO* | TODO*  | TODO*  | DONE   | TODO* | TODO* | TODO*  |
| f_json  | DONE   | DONE   | TODO* | TODO*  | TODO*  | DONE   | TODO* | TODO* | TODO*  |
| f_csv   | DONE*  | DONE   | TODO* | TODO*  | TODO*  | DONE   | TODO* | TODO* | TODO*  |
| f_html  | DONE*  | DONE   | TODO* | TODO*  | TODO*  | DONE   | TODO* | TODO* | TODO*  |

\* DONE means the combination was tested and its behavior was
confirmed as expected. This includes cases where the pipeline
correctly failed due to a known Transform/target schema mismatch
(see Tests 11/14/17/20/23), not just cases where data successfully
reached the target. TODO means not yet tested.

\* TODO All non-JSON target format columns (a_xml, a_csv, a_html, f_xml,
f_csv, f_html) remain TODO, not because of any architectural
limitation — `target_format` and `Content-Type` header handling are
already fully implemented on the Load/Export side. What's missing is
a concrete Transform strategy that actually converts canonical JSON
into XML/CSV/HTML output; every strategy written so far (passthrough,
comments-mapper) only produces JSON. Writing and validating a
non-JSON-producing Transform strategy is deferred to v0.9's
real-consumer validation phase (fluxus-ncr), where a genuine use case
will drive what gets built, rather than writing one now just to
close a matrix cell.

### 📅 2026-08-05, Wednesday
**06:48** | *[RESOLVE — v0.75]*
**PostgreSQL storage backend confirmed via full manual test suite**

Added `.env`-based configuration (`FLUXUS_STORE_ADDRESS`, `LOG_DIR`)
to `settings.py`, replacing hardcoded storage addresses — settings now
follow an "override via environment, sensible default otherwise"
pattern throughout. Same pattern applied to `devtools/settings.py`.

Pointed `FLUXUS_STORE_ADDRESS` at the Docker-hosted PostgreSQL
container and re-ran all 31 manual test packages. All 31 produced the
expected result (26 PASS/expected-FAIL matching prior SQLite runs) —
no code changes were needed to `PayloadStoreSQLite`/
`RegistryStoreSQLite`/`PipelineRunRecordsSQLite`/`FetchCacheStoreSQLite`,
confirming the SQLAlchemy Session-based implementation was already
dialect-agnostic. Test 26 (the standalone dialect_check table) was
excluded after the table was manually dropped — kept as a one-off
manual verification rather than folded into `setup-test-env`, since
devtools is a personal tool and doesn't need every path automated.

**Open question surfaced but not yet resolved:** whether Fluxus should
eventually take advantage of PostgreSQL-specific features (JSONB
columns, real concurrent-write support) rather than just being
dialect-portable. Concluded this is a separate, larger concern (would
require an async-capable Orchestrator to actually benefit from
concurrent writes) — not in scope for v0.75, noted for a possible
future milestone.

**Status:** v0.75's "PostgreSQL storage backend added... proves
storage layer is swappable" requirement is effectively satisfied —
the existing SQL-based storage classes already work correctly against
PostgreSQL without modification, no new backend-specific class was
needed as originally assumed in the roadmap wording.

**07:45** | *[RESOLVE]*

- Tested postgres_bakcend.py with 11 tests, all passing.
- Developed over the SQLite storage test suite, and runned against a
  Docker-hosted PostgreSQL instance. Confirms the storage classes are
  genuinely dialect-agnostic — same code, same tests, different engine.
- Test isolation handled via transaction-rollback fixtures (each test
  runs in its own transaction, rolled back afterwards) rather than
  drop/create per test, since PostgreSQL doesn't reset sequence
  counters on rollback and repeated schema teardown proved slow and
  unreliable.