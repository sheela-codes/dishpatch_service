"""Generates daily delivery files for the Dishpatch ingester.

Run from the project root:
    python -m provider.generator --start 2026-09-01 --days 30

The random seed comes from the start date's year and month (2026-09-01 -> 202609),
so each month gets its own repeatable dataset. --seed overrides it.

See requirements/provider.md for the file layout and formats.
"""
import argparse
import logging
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from faker import Faker

from provider.config import PARTNER
from provider.models import Driver, MenuItem, Restaurant, World
from provider.reference import create_drivers, create_menu_items, create_restaurants
from provider.writers import day_folder, reset_folder, write_csv, write_done


log = logging.getLogger("provider")


# --- command-line options -------------------------------------------------

def iso_date(text: str) -> date:
    """argparse type: turn 'YYYY-MM-DD' into a date, with a clear error otherwise."""
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{text}' is not a date in YYYY-MM-DD format")


def positive_int(text: str) -> int:
    """argparse type: a whole number of at least 1."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{text}' is not a whole number")
    if value < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return value


def read_options(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m provider.generator",
        description="Generate partner delivery files (reference + activity) for a range of days.",
    )
    parser.add_argument("--start", required=True, type=iso_date,
                        help="first day to generate, YYYY-MM-DD")
    parser.add_argument("--days", type=positive_int, default=30,
                        help="number of days to generate (default: 30)")
    parser.add_argument("--seed", type=int, default=None,
                        help="random seed; the same seed gives the same files "
                             "(default: year and month of --start, e.g. 202609)")
    parser.add_argument("--out", type=Path, default=Path("data/incoming"),
                        help="output folder (default: data/incoming)")
    parser.add_argument("--overwrite", action="store_true",
                        help="replace day folders that already exist")
    return parser.parse_args(argv)


# --- logging --------------------------------------------------------------

def setup_logging() -> None:
    """Simple console logging: one line per day plus a final summary."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# --- main -----------------------------------------------------------------

def main(argv=None) -> int:
    args = read_options(argv)
    setup_logging()

    days = [args.start + timedelta(days=i) for i in range(args.days)]

    # Refuse to start if any day already exists, so a run never stops halfway.
    if not args.overwrite:
        existing = [day_folder(args.out, d) for d in days if day_folder(args.out, d).exists()]
        if existing:
            log.error("%d day folder(s) already exist, e.g. %s. Use --overwrite to replace them.",
                      len(existing), existing[0])
            return 1

    # Default seed: year + month of the start date (2026-09-01 -> 202609).
    seed = args.seed if args.seed is not None else args.start.year * 100 + args.start.month

    # Two seeded random sources -> the same seed always produces the same files.
    rng = np.random.default_rng(seed)  # numbers and times (used by reference/activity modules)
    Faker.seed(seed)
    fake = Faker("en_US")                    # names, emails, addresses

    log.info("Generating %d day(s) from %s to %s into %s (seed %d)",
             len(days), days[0], days[-1], args.out / PARTNER, seed)

    world = World()   # everything created so far, remembered across all days

    for i, day in enumerate(days):
        folder = day_folder(args.out, day)
        reset_folder(folder)   # start empty (only matters with --overwrite)

        # --- reference/ ---
        if i == 0:   # day one: everything
            restaurants = create_restaurants(world, rng, fake)
            menu_items = create_menu_items(world, rng)
            drivers = create_drivers(world, rng, fake)
        else:        # TODO: later-day changes -> make_reference_changes(world, rng)
            restaurants, menu_items, drivers = [], [], []

        reference = folder / "reference"
        n_restaurants = write_csv(reference / "restaurants.csv", restaurants, Restaurant.CSV_COLUMNS)
        n_menu_items = write_csv(reference / "menu_items.csv", menu_items, MenuItem.CSV_COLUMNS)
        n_drivers = write_csv(reference / "drivers.csv", drivers, Driver.CSV_COLUMNS)

        # --- activity/ ---
        # TODO: activity/customers.csv -> make_new_customers(world, day, rng, fake)
        # TODO: activity/orders.jsonl  -> make_orders(world, day, rng)

        write_done(folder)     # always last: tells the ingester this day is complete

        log.info("%s: %d restaurants, %d menu items, %d drivers",
                 day, n_restaurants, n_menu_items, n_drivers)

    log.info("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
