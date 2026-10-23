"""The ingester's starting point. Run from the project root, inside the api container:

    docker compose exec api python -m src.ingester --in data/incoming/redmondtownservice

What it does (requirements/ingester.md):
  1. find the delivery folders, oldest first
  2. skip a folder that has no _DONE file yet
  3. load each folder in its own transaction: everything is saved, or nothing is
  4. record every loaded file in file_loads, so a second run skips it
"""
import argparse
from pathlib import Path

from src.ingester import load_log, logs
from src.ingester.csvfile import FileRejected
from src.ingester.db import connect
from src.ingester.folders import DONE_MARKER, find_day_folders
from src.ingester import load_customers, load_drivers, load_menu_items, load_orders, load_restaurants

# Each file that has a loader, in the order they must run (restaurants before menu items, ...).
# Files without a loader yet are reported as "not loaded" and not recorded,
# so they'll be picked up once their loader exists.
LOADERS = [
    (load_restaurants.FILE, load_restaurants.load_restaurants),
    (load_menu_items.FILE, load_menu_items.load_menu_items),      # needs restaurants
    (load_drivers.FILE, load_drivers.load_drivers),
    (load_customers.FILE, load_customers.load_customers),
    (load_orders.FILE, load_orders.load_orders),                  # needs all of the above
]


def read_options(argv=None):
    parser = argparse.ArgumentParser(prog="python -m src.ingester",
                                     description="Load partner delivery folders into Postgres.")
    parser.add_argument("--in", dest="partner_dir", type=Path, required=True,
                        help="the partner's folder, e.g. data/incoming/redmondtownservice")
    return parser.parse_args(argv)


def delivery_files(folder) -> list:
    """The data files in a day folder, as names like 'reference/restaurants.csv' (without _DONE)."""
    names = []
    for path in folder.path.rglob("*"):
        if path.is_file() and path.name != DONE_MARKER:
            relative_name = str(path.relative_to(folder.path))
            names.append(relative_name)
    names.sort()
    return names


def load_folder(conn, folder) -> None:
    """Load one day folder. Runs inside the transaction that main() opens for it."""
    already = load_log.recorded(conn, folder.label)
    files = delivery_files(folder)

    # 1. Stop if the partner changed a file we already loaded.
    for name in files:
        if load_log.status(folder.path / name, name, already) == load_log.CHANGED:
            raise load_log.ChangedFile(f"{name} changed after it was loaded")

    # 2. Which files haven't been loaded yet?
    to_load = []
    for name in files:
        if name not in already:
            to_load.append(name)
    if len(to_load) == 0:
        logs.info("skipped: already loaded", folder=folder.label)
        return

    # 3. Run each loader whose file is waiting, in LOADERS order.
    summary = []
    for name, loader in LOADERS:
        if name not in to_load:
            continue
        try:
            result = loader(conn, folder.path, folder.label)
        except FileRejected as problem:
            logs.reject(str(problem), folder=folder.label, file=name)    # whole file refused, not recorded
            summary.append(f"{name} rejected")
            continue
        load_log.record(conn, folder.label, name, folder.path / name, result.loaded, result.rejected)
        summary.append(f"{name} loaded: {result.inserted} new, {result.updated} updated, "
                       f"{result.rejected} rejected")

    # 4. Mention files that have no loader yet.
    names_with_loader = []
    for name, loader in LOADERS:
        names_with_loader.append(name)
    waiting = []
    for name in to_load:
        if name not in names_with_loader:
            waiting.append(name)
    if len(waiting) > 0:
        summary.append("not loaded (no loader yet): " + ", ".join(waiting))

    logs.info(" | ".join(summary), folder=folder.label)


def main(argv=None) -> int:
    options = read_options(argv)
    log_file = logs.setup_logging()

    if not options.partner_dir.is_dir():
        logs.error(f"partner folder not found: {options.partner_dir}")
        return 1

    folders = find_day_folders(options.partner_dir)
    logs.info(f"found {len(folders)} day folder(s) in {options.partner_dir}; log file {log_file}")

    processed = 0
    skipped = 0
    with connect() as conn:
        for folder in folders:                       # oldest first
            if not folder.complete:
                logs.info("skipped: no _DONE yet (delivery not complete)", folder=folder.label)
                skipped = skipped + 1
                continue

            try:
                with conn.transaction():             # one transaction per folder: all or nothing
                    load_folder(conn, folder)
            except load_log.ChangedFile as problem:
                logs.error(f"stopped: {problem}; nothing from this folder was saved", folder=folder.label)
                return 1
            except Exception as problem:             # anything unexpected: nothing from this folder is saved
                logs.error(f"folder rolled back, run stopped: {problem!r}", folder=folder.label)
                return 1

            processed = processed + 1

    logs.info(f"done: {processed} folder(s) processed, {skipped} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
