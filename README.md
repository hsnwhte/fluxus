# Fluxus v0.7 - alpha

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

## Usage

```bash
fluxus run \
  --source-type file --source-address ./data/input.xml \
  --target-type file --target-address ./data/output.json \
  --transform-strategy 0 \
  --target-format json
```

Transform strategies are referenced by numeric id, not by name (see
below). Run `fluxus run --help` for the full list of options.

## Writing and installing a Transform strategy

Transform is the one phase with no fixed built-in implementation —
it's where your own business logic (field mapping, filtering,
reshaping data to fit your target) lives. Strategy `0` is a built-in
passthrough (copies data through unchanged) and always exists; every
other strategy is installed by you.

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
assigns it the next available numeric id (printed on install). List
installed strategies and their ids with `fluxus list-strategies`.
Uninstall with:

```bash
fluxus uninstall-strategy --id <id>
```

Strategy `0` cannot be uninstalled. Don't edit the `installed/` folder
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

## Roadmap

See `docs/ROADMAP.md` for planned milestones.
