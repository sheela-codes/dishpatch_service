"""The file_loads table: which partner files are already loaded (requirements/ingester.md, section 6).

Each loaded file gets one row: its folder, its name and a checksum (a fingerprint of its contents).
Before loading, the ingester compares:
  - not in the table            -> NEW:     load it
  - in the table, same checksum -> LOADED:  skip it
  - in the table, new checksum  -> CHANGED: the partner edited a delivered file; stop
"""
import hashlib
from pathlib import Path

NEW = "new"
LOADED = "loaded"
CHANGED = "changed"


class ChangedFile(Exception):
    """Raised when a file that was already loaded has different contents now."""


def checksum(path: Path) -> str:
    """A SHA-256 fingerprint of the file. If even one character changes, so does this."""
    contents = path.read_bytes()
    return hashlib.sha256(contents).hexdigest()


def recorded(conn, folder: str) -> dict:
    """Files already loaded from this folder: {file name: checksum}. One query."""
    already = {}
    rows = conn.execute("SELECT file_name, checksum FROM public.file_loads WHERE folder = %s", [folder])
    for file_name, file_checksum in rows:
        already[file_name] = file_checksum
    return already


def status(path: Path, name: str, already: dict) -> str:
    """NEW, LOADED or CHANGED for one file (see the top of this file)."""
    if name not in already:
        return NEW
    if already[name] == checksum(path):
        return LOADED
    return CHANGED


def record(conn, folder: str, name: str, path: Path, loaded: int, rejected: int) -> None:
    """Add the file to file_loads. Call this inside the folder's transaction,
    so the load-log row and the data are saved (or undone) together."""
    conn.execute(
        "INSERT INTO public.file_loads (folder, file_name, checksum, rows_loaded, rows_rejected) "
        "VALUES (%s, %s, %s, %s, %s)",
        [folder, name, checksum(path), loaded, rejected],
    )
