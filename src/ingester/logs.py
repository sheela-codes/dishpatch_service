"""Log messages in the format from requirements/ingester.md, section 8:

    <timestamp UTC> <LEVEL> <folder> <file>:<line> <ref> <message>

For example:

    2026-10-22T03:30:01Z ERROR   2026/10/19 activity/orders.jsonl:31   O-20261019-0030  rejected: ...

Every message goes to the screen and to a log file: logs/ingest_<run start time>.log.

Use the four helpers at the bottom:
    info(...)     progress: a folder started, was skipped, its summary
    warning(...)  something odd, but the data was kept (e.g. a duplicate was replaced)
    reject(...)   a row or file was refused, with the reason
    error(...)    something that stops a folder or the run
"""
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("ingester")


def setup_logging(log_dir: Path = Path("logs")) -> Path:
    """Send log messages to the screen and to a new file for this run. Returns the file's path."""
    log_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    log_file = log_dir / f"ingest_{started}.log"

    # Each line starts with the time (in UTC) and the level; the rest of the line is built by write().
    formatter = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ")
    formatter.converter = time.gmtime

    screen = logging.StreamHandler()
    screen.setFormatter(formatter)
    file = logging.FileHandler(log_file, encoding="utf-8")
    file.setFormatter(formatter)

    log.addHandler(screen)
    log.addHandler(file)
    log.setLevel(logging.INFO)
    return log_file


def write(level, message, folder, file, line, ref):
    """Build '<folder> <file>:<line> <ref> <message>' with fixed-width columns, and log it."""
    if line is None:
        where = file
    else:
        where = f"{file}:{line}"
    text = f"{folder:<10} {where:<24} {ref:<16} {message}"
    log.log(level, text)


def info(message, folder="-", file="-", line=None, ref="-"):
    write(logging.INFO, message, folder, file, line, ref)


def warning(message, folder="-", file="-", line=None, ref="-"):
    write(logging.WARNING, message, folder, file, line, ref)


def reject(reason, folder="-", file="-", line=None, ref="-"):
    write(logging.ERROR, f"rejected: {reason}", folder, file, line, ref)


def error(message, folder="-", file="-", line=None, ref="-"):
    write(logging.ERROR, message, folder, file, line, ref)
