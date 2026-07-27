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