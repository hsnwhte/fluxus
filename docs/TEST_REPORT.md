# Fluxus — Manual & Automated Test Report

This report tracks manual end-to-end verification (via devtools) and
automated test suite results for each Fluxus release. It exists
alongside `docs/ROADMAP.md` (what's planned) and `docs/DIARY.md`
(development narrative) as a focused, at-a-glance record of what has
actually been verified to work — intended for anyone evaluating the
project from the outside.

Each entry below documents a single manual test run: what was tested,
with what input, what the result was, and what that confirms. Automated
(pytest) results are summarized separately at the end of each version
section.

---

## v0.7

### Automated (pytest)
- Total: 77 tests passing
- Coverage by category: storage (11), fetch (7), decode (27), extract (19),
  transform (1), load (11), export (1)

#### Test run 1
 - Total tests: 77
 - Failed: 4
 - Passed: 73
 - Warnings: 0
 - Fluxus App Bugs: 0
 - Test Design Shortcomings: 2
   1. `html_decode_strategy.py` / `xml_decode_stratgy.py`: neither
      catches `OSError`(`FileNotFoundError does not catch the error 
      raised by dependency`), so a missing file raises a raw `lxml` 
      `OSError` instead of `DecodeSourceFileNotFoundError`.
   2. `test_decode_malformed` for CSV and HTML: the "malformed" sample
      files aren't actually malformed enough — `csv.Sniffer()` and
      `lxml.html.parse()` are too tolerant to reject them, so no
      exception is raised. Test expectation doesn't match real
      strategy behavior; needs a genuinely-malformed sample or a
      mocked failure instead.

#### Test run 2
 - Total tests: 77
 - Failed: 0
 - Passed: 77
 - Warnings: 0
 - Fluxus App Bugs: 0
 - Test Design Shortcomings: FIXED



### Manual verification
**Summary (as of 2026-08-03):** 24 manual test packages run.
19 passed as expected, 5 failed as expected (deliberate strategy/target
schema mismatch, not bugs). 2 real bugs found and fixed along the way
(`.htm` extension not recognized; `HtmlDecodeStrategy` missed catching
`OSError`). `DevTargetDataBlob` (binary DB target) not yet exercised —
no current Transform strategy produces bytes output.

#### Test 1 — file(json)→file(json)
- **Input:** `comments.json` (500 records, jsonplaceholder sample)
- **Command:** `python -m devtools.main test --test-pack 1`
- **Verifies:** Decode(JSON)→Extract(JSON)→Transform(installed strategy)→Export
- **Result:** PASS — output file matches expected structure

#### Test 2 — file(json)→db
- **Input:** `comments.json`
- **Command:** `python -m devtools.main test --test-pack 2`
- **Verifies:** Decode(JSON)→Extract(JSON)→Transform(installed strategy)→Load(DB)
- **Result:** PASS

#### Test 3 — file(json)→api
- **Input:** `comments.json`
- **Command:** `python -m devtools.main test --test-pack 3`
- **Verifies:** Decode(JSON)→Extract(JSON)→Transform(installed strategy)→Load(API)
- **Result:** PASS

#### Test 4 — db→file(json)
- **Input:** dev source DB table (`dev_source_data_text`)
- **Command:** `python -m devtools.main test --test-pack 4`
- **Verifies:** Fetch(DB)→Extract(JSON)→Transform(passthrough)→Export
- **Result:** PASS

#### Test 5 — db→db
- **Input:** dev source DB table (`dev_source_data_text`)
- **Command:** `python -m devtools.main test --test-pack 5`
- **Verifies:** Fetch(DB)→Extract(JSON)→Transform(passthrough)→Load(DB)
- **Result:** PASS

#### Test 6 — db→api
- **Input:** dev source DB table (`dev_source_data_text`)
- **Command:** `python -m devtools.main test --test-pack 6`
- **Verifies:** Fetch(DB)→Extract(JSON)→Transform(passthrough)→Load(API)
- **Result:** PASS

#### Test 7 — api→file(json)
- **Input:** dev source API endpoint
- **Command:** `python -m devtools.main test --test-pack 7`
- **Verifies:** Fetch(API, Content-Type detection)→Extract(JSON)→Transform(passthrough)→Export
- **Result:** PASS

#### Test 8 — api→db
- **Input:** dev source API endpoint
- **Command:** `python -m devtools.main test --test-pack 8`
- **Verifies:** Fetch(API)→FetchCache write→Extract(JSON)→Transform(installed strategy)→Load(DB)
- **Result:** PASS

#### Test 9 — api→api
- **Input:** dev source API endpoint
- **Command:** `python -m devtools.main test --test-pack 9`
- **Verifies:** Fetch(API)→FetchCache write→Extract(JSON)→Transform(passthrough)→Load(API)
- **Result:** PASS

#### Test 10 — file(csv)→file(json)
- **Input:** `cities.csv`
- **Command:** `python -m devtools.main test --test-pack 10`
- **Verifies:** Decode(CSV, validation + raw bytes)→Extract(CSV→list[dict])→Transform(passthrough)→Export
- **Result:** PASS
- 
#### Test 11 — file(csv)→db
- **Input:** `cities.csv`
- **Command:** `python -m devtools.main test --test-pack 11`
- **Verifies:** Decode(CSV)→Extract(CSV→list[dict])→Transform(strategy id=1, comments-shaped)→Load(DB)
- **Result:** FAIL (expected) — `KeyError: 'id'`. Strategy id=1 expects
  comment-shaped fields (`id`, `name`, `email`, `body`), but `cities.csv`
  has a different schema. Confirms Transform must match the source
  shape it's given — not a bug, expected behavior given a mismatched
  strategy. A CSV-appropriate strategy needs to be written and
  installed before retrying.

#### Test 12 — file(csv)→api
- **Input:** `cities.csv`
- **Command:** `python -m devtools.main test --test-pack 12`
- **Verifies:** Decode(CSV)→Extract(CSV→list[dict])→Transform(passthrough)→Load(API)
- **Result:** PASS

#### Test 13 — file(html)→file(json)
- **Input:** `The_World_Wide_Web_project.htm`
- **Command:** `python -m devtools.main test --test-pack 13`
- **Verifies:** Decode(HTML)→Extract(HTML)→Transform(passthrough)→Export
- **Result:** FAIL (expected) — file extension is `.htm`, not `.html`.
  Selector's decode strategy lookup keys on file suffix and doesn't
  recognize `.htm` as an alias for `.html`. Confirms Selector's
  extension-based dispatch is strict/literal, not fuzzy — a real gap
  worth deciding on (support `.htm` as an alias, or leave it and
  require users to rename).
- - **Result:** PASS (after two fixes)
- **Bugs found and fixed along the way:**
  1. `.htm` extension wasn't recognized by Selector's DECODE_STRATEGY_MAP
     (only `.html` was registered) — added `"htm"` as an alias.
  2. `HtmlDecodeStrategy` only caught `etree.ParseError`, but `lxml`
     raises `OSError` for unreadable/malformed file access — widened
     the except clause to catch both.

#### Test 14 — file(html)→db
- **Input:** `The World Wide Web project.htm`
- **Command:** `python -m devtools.main test --test-pack 14`
- **Verifies:** Decode(HTML)→Extract(HTML)→Transform(strategy id=1, comments-shaped)→Load(DB)
- **Result:** FAIL (expected) — strategy id=1 doesn't match HTML's
  extracted shape (comments-specific field mapping). Confirms the same
  "Transform must match source shape" behavior seen in Test 11. No fix
  needed — an HTML-appropriate strategy would need to be written.

#### Test 15 — file(html)→api
- **Input:** `The World Wide Web project.htm`
- **Command:** `python -m devtools.main test --test-pack 15`
- **Verifies:** Decode(HTML)→Extract(HTML)→Transform(passthrough)→Load(API)
- **Result:** PASS

#### Test 16 — file(xml)→file(json)
- **Input:** `cd_catalog.xml`
- **Command:** `python -m devtools.main test --test-pack 16`
- **Verifies:** Decode(XML)→Extract(XML via xmltodict)→Transform(passthrough)→Export
- **Result:** PASS

#### Test 17 — file(xml)→db
- **Input:** `cd_catalog.xml`
- **Command:** `python -m devtools.main test --test-pack 17`
- **Verifies:** Decode(XML)→Extract(XML)→Transform(strategy id=1, comments-shaped)→Load(DB)
- **Result:** FAIL (expected) — strategy id=1 doesn't match XML's
  extracted shape. Same expected behavior as Tests 11 and 14.

#### Test 18 — file(xml)→api
- **Input:** `cd_catalog.xml`
- **Command:** `python -m devtools.main test --test-pack 18`
- **Verifies:** Decode(XML)→Extract(XML)→Transform(passthrough)→Load(API)
- **Result:** PASS

#### Test 19 — file(docx)→file(json)
- **Input:** `sample-files.com-basic-text.docx`
- **Command:** `python -m devtools.main test --test-pack 19`
- **Verifies:** Decode(DOCX, raw bytes)→Extract(DOCX, per-XML-member zip dict via xmltodict)→Transform(passthrough)→Export
- **Result:** PASS

#### Test 20 — file(docx)→db
- **Input:** `sample-files.com-basic-text.docx`
- **Command:** `python -m devtools.main test --test-pack 20`
- **Verifies:** Decode(DOCX)→Extract(DOCX)→Transform(passthrough)→Load(DB)
- **Result:** FAIL (expected) — DOCX's raw per-file-XML shape doesn't
  match `dev_target_data_text`'s schema. Same "Transform must match
  target shape" behavior as prior DB-target tests. No fix needed.

#### Test 21 — file(docx)→api
- **Input:** `sample-files.com-basic-text.docx`
- **Command:** `python -m devtools.main test --test-pack 21`
- **Verifies:** Decode(DOCX)→Extract(DOCX)→Transform(passthrough)→Load(API)
- **Result:** PASS

#### Test 22 — file(xlsx)→file(json)
- **Input:** `Free_Test_Data_100KB_XLSX.xlsx`
- **Command:** `python -m devtools.main test --test-pack 22`
- **Verifies:** Decode(XLSX, raw bytes)→Extract(XLSX, per-XML-member zip dict)→Transform(passthrough)→Export
- **Result:** PASS

#### Test 23 — file(xlsx)→db
- **Input:** `Free_Test_Data_100KB_XLSX.xlsx`
- **Command:** `python -m devtools.main test --test-pack 23`
- **Verifies:** Decode(XLSX)→Extract(XLSX)→Transform(passthrough)→Load(DB)
- **Result:** FAIL (expected) — same schema mismatch pattern as Test 20.

#### Test 24 — file(xlsx)→api
- **Input:** `Free_Test_Data_100KB_XLSX.xlsx`
- **Command:** `python -m devtools.main test --test-pack 24`
- **Verifies:** Decode(XLSX)→Extract(XLSX)→Transform(passthrough)→Load(API)
- **Result:** PASS