"""Reading a partner CSV file safely (requirements/ingester.md, sections 7.1 and 7.5).

Two functions:
  read_csv()      read the file, check the header, skip rows with the wrong number of columns
  last_one_wins() if the same ref appears twice, keep the last row
"""
import csv
from pathlib import Path

from src.ingester import logs


class FileRejected(Exception):
    """Raised when the whole file can't be used (unreadable, or the header is wrong)."""


def read_csv(path: Path, columns, folder: str, name: str):
    """Read a CSV file.

    Returns two things:
      rows      a list of (line number, row) pairs; each row is a dictionary {column: value}
      rejected  how many rows were skipped because they had the wrong number of columns

    Line numbers count the header as line 1, the way a text editor does.
    Raises FileRejected if the file can't be read or its header doesn't match `columns`.
    """
    # Read every line of the file into a list of lists: [['R001', 'Liberty Burger', ...], ...]
    try:
        with path.open(newline="", encoding="utf-8") as f:
            all_lines = list(csv.reader(f))
    except (OSError, csv.Error, UnicodeDecodeError) as problem:
        raise FileRejected(f"cannot read file: {problem}")

    if len(all_lines) == 0:
        raise FileRejected("file is empty (no header row)")

    # The first line must be exactly the expected column names.
    header = []
    for column_name in all_lines[0]:
        header.append(column_name.strip())
    if header != list(columns):
        raise FileRejected(f"header {header} does not match expected {list(columns)}")

    rows = []
    rejected = 0
    line_no = 1                              # the header was line 1

    for values in all_lines[1:]:             # every line after the header
        line_no = line_no + 1

        if len(values) != len(columns):
            logs.reject(f"expected {len(columns)} columns, found {len(values)}",
                        folder=folder, file=name, line=line_no)
            rejected = rejected + 1
            continue

        # Pair each column name with its value: {'restaurant_ref': 'R001', 'name': 'Liberty Burger', ...}
        row = {}
        for position in range(len(columns)):
            row[columns[position]] = values[position].strip()

        rows.append((line_no, row))

    return rows, rejected


def last_one_wins(rows: list, key: str, folder: str, name: str) -> list:
    """If the same ref (the value in column `key`) appears more than once, keep only the last row.

    Each earlier row is skipped with a WARNING that says which line replaced it.
    """
    kept = {}                                # {ref: (line number, row)}

    for line_no, row in rows:
        ref = row[key]
        if ref in kept:
            earlier_line = kept[ref][0]
            logs.warning(f"duplicate, replaced by line {line_no}",
                         folder=folder, file=name, line=earlier_line, ref=ref)
        kept[ref] = (line_no, row)

    return list(kept.values())
