tooncsv
=======

This repository is archived to be a [MR](https://github.com/toon-format/toon-python/pull/39) to the official repo : https://github.com/toon-format/toon-python

Overview
--------

`tooncsv` is a small, focused Python library that converts data encoded in the "toon" line/indentation format into one or more CSV files. The library strictly parses the original toon text format (line- and indentation-based) — it does not require decoding into intermediate JSON objects.

Key behaviors
- Nested objects and arrays are exported as separate CSVs.
- Nested CSV names use the dotted full path (for example `test.test4.csv`).
- CSV files are written with an optional UTF-8 BOM for Excel compatibility and can be zipped.

Installation
------------

Install into your environment (editable/local install during development):

```powershell
cd path\to\project
pip install -e .
```

If this repository is packaged and published, install from PyPI with:

```powershell
pip install tooncsv
```

Quick Start
-----------

Basic usage example:

```python
from tooncsv import parse_to_csv, write_csvs
from toon_format import encode

# `encoded` is a string in the toon format
encoded = encode({
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
})

csv_map = parse_to_csv(encoded)
# csv_map is a dict: { 'users': 'col1,col2\nval1,val2\n', ... }

write_csvs(csv_map, out_dir='toon_csvs', zip_name='toon_csvs.zip', bom=True, flat=True)
```

API Reference
-------------

`tooncsv.parser.parse_to_csv(encoded: str) -> Dict[str, str]`
- Purpose: Parse a toon-encoded text string and return a mapping of CSV names to CSV text.
- Input: `encoded` — a multiline string following the toon line/indentation format.
- Output: A dictionary where keys are CSV base names (possibly dotted paths) and values are CSV content strings (including header row when available and a trailing newline).
- Naming rules: Nested objects become separate CSVs named by their full dotted path (e.g., `parent.child`). Arrays produce CSVs named by their declared name.
- Parsing rules: The parser operates strictly on the line and indentation structure; it recognizes three patterns — primitive key/value pairs, object headers (`name:` with indented block), and array headers (`name[N]{col1,col2}:`). Primitive fields found inside an object become that object's CSV row.

`tooncsv.writer.write_csvs(csvs: Dict[str,str], out_dir: str='toon_csvs', zip_name: str='toon_csvs.zip', bom: bool=True, flat: bool=True) -> (Path, Path)`
- Purpose: Write CSV content from the `csvs` mapping to disk and create a zip archive.
- Parameters:
  - `csvs`: mapping produced by `parse_to_csv`.
  - `out_dir`: output folder where CSVs are written.
  - `zip_name`: path/name of the resulting zip archive.
  - `bom`: when `True` writes files with `utf-8-sig` (UTF-8 with BOM) for Excel compatibility.
  - `flat`: when `True` writes flat filenames that preserve dots (e.g., `test.test4.csv`); when `False` creates subfolders for each dot-separated path component.
- Returns: a tuple `(out_dir_path, zip_path)` as `pathlib.Path` objects.

CSV conventions
---------------
- Header row: For arrays, columns declared in the header (e.g. `items[2]{a,b}:`) are used as the CSV's header row.
- Primitive objects: For object blocks that contain primitive key/value lines, those primitive fields are exported as a single-row CSV with the primitive keys as columns.
- Trailing newline: Exported CSV strings include a trailing newline.

Filename rules
--------------
- When `flat=True`, CSV filenames are created by taking the CSV key, removing unsafe characters, and appending `.csv`. Dots are preserved (e.g. `test.test4.csv`).
- When `flat=False`, dotted names create nested directories, and the final segment becomes the CSV filename.

Limitations & Notes
-------------------
- The parser intentionally follows the line/indentation "toon" format — it does not attempt to parse arbitrary JSON-like content.
- Complex or malformed toon inputs may not produce expected CSVs; the parser assumes well-formed indentation and array counts.
- No CLI, tests, or PyPI releases are included by default. See "Next steps" for recommendations.

Examples
--------

Minimal example — parse and write CSVs locally:

```python
from tooncsv import parse_to_csv, write_csvs
from toon_format import encode

data = {
    "test": {
        "count": 2,
        "test4": {
            "test5": 42,
            "items": [
                {"a": 1, "b": 2},
                {"a": 3, "b": 4}
            ]
        }
    }
}

encoded = encode(data)
csvs = parse_to_csv(encoded)
write_csvs(csvs, out_dir='toon_csvs', zip_name='toon_csvs.zip', bom=True, flat=True)
```