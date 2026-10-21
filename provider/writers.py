"""Writing the partner's delivery files (layout and formats: requirements/provider.md).

Every record passed in knows its own file format:
  - CSV records have CSV_COLUMNS and to_row()
  - JSONL records have to_json()
"""
import csv
import json
import shutil
from datetime import date
from pathlib import Path

from provider.config import PARTNER


def day_folder(out: Path, day: date) -> Path:
    """data/incoming/redmondtownservice/2026/10/19"""
    return out / PARTNER / f"{day:%Y/%m/%d}"


def reset_folder(folder: Path) -> None:
    """Start a day folder empty: remove whatever an earlier run left there (only used with --overwrite)."""
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)


def write_csv(path: Path, records, columns, *, write_if_empty: bool = False) -> int:
    """Write records to a CSV file with a header row. Returns how many rows were written.

    With no records, nothing is written (no file) unless write_if_empty=True:
      - reference files only appear when something changed (default)
      - activity/customers.csv is written every day, header only on a quiet day
    """
    records = list(records)
    if not records and not write_if_empty:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="" is required by the csv module; lineterminator="\n" gives plain Unix line endings.
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_row())
    return len(records)


def write_jsonl(path: Path, records) -> int:
    """Write one JSON object per line (orders.jsonl). Returns how many lines were written.

    Unlike reference files, orders.jsonl is written every day, even if it's empty.
    """
    records = list(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record.to_json(), ensure_ascii=False) + "\n")
    return len(records)


def write_done(folder: Path) -> None:
    """Create the empty _DONE marker. Call this last: it tells the ingester the day is complete."""
    (folder / "_DONE").touch()
