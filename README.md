# Fluxus v0.7.5 - alpha

Generic, plugin-based ETL & data sync engine. Fetches from a source
transforms it, and loads it to a target — with the transform step designed
to carry your own business logic, not a fixed built-in one.
Source and target types can be API, database, or file.

> **Status: Alpha.** Core pipeline (Fetch → Decode → Extract →
> Transform → Load/Export) is implemented and tested. See
> [Known Limitations](#known-limitations) before relying on this in
> production.

## Installation

```bash
pip install -e ".[sql,api,xml,cli,dev,docx,xlsx,pdf]"
```

## Configuration

Fluxus reads optional settings from a `.env` file in the project root:

```
FLUXUS_STORE_ADDRESS=sqlite:///data/runtime.sqlite
LOG_DIR=logs
```

`FLUXUS_STORE_ADDRESS` accepts any SQLAlchemy connection string —
SQLite and PostgreSQL are both verified. `LOG_DIR` may be relative to
the project root or an absolute path. Both have sensible defaults, so
a `.env` file is optional.

## Usage

```bash
fluxus run \
  --source-type file --source-address ./data/input.xml \
  --target-type file --target-address ./data/output.json \
  --target-format json
```

Run `fluxus run --help` for the full list of options.

## Writing and installing a Transform strategy

Transform is the one phase with no fixed built-in implementation —
it's where your own business logic (field mapping, filtering,
reshaping data to fit your target) lives. The strategy `default` is a
built-in passthrough (copies data through unchanged) and always
exists; every other strategy is installed by you.

Every Transform strategy implements `TransformStrategyProtocol`, and
the class name must start with `TransformStrategy`:

```python
from fluxus.models.dto import TransformableData, TransformedData
from fluxus.enums import ContentFormat

class TransformStrategyMyMapping:
    def __init__(self, *, target_format: ContentFormat, data: TransformableData, **kwargs):
        self.target_format = target_format
        self.data = data

    def transform(self) -> TransformedData:
        # your logic here — data.content is canonical JSON (bytes)
        ...
        return TransformedData(content=...)
```

A file must contain exactly one class matching that naming pattern.

Install it:

```bash
fluxus install-strategy --path /path/to/my_strategy.py
```

This copies the file into Fluxus's `installed/` strategies folder and
assigns it a unique id (printed on install). List installed strategies
and their ids with `fluxus show-strategies`, then reference one in a
run:

```bash
fluxus run ... --transform-strategy <uid>
```

Uninstall with:

```bash
fluxus uninstall-strategy --uid <uid>
```

`default` cannot be uninstalled. Don't edit the `installed/` folder
by hand — use these commands so the strategy map always matches what's
actually on disk.

## Known Limitations

- **No filename/format consistency check**: nothing validates that a
  file's extension matches `--target-format` (e.g. writing JSON
  content to a `.xml`-named file goes unflagged).
- **No dependency management for installed strategies**: a Transform
  strategy installed via `install-strategy` may import third-party
  libraries not bundled with Fluxus. You are responsible for installing
  any such dependencies yourself — Fluxus does not manage them.
- **Uninstalling a strategy breaks its lineage**: registry rows from
  past runs keep the strategy's uid, but once the file is removed that
  uid no longer resolves to anything. The recorded strategy class name
  remains as partial context.

## Roadmap

See `docs/ROADMAP.md` for planned milestones.