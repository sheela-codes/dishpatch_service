"""Daily activity: new customers and orders (activity/ folder, see requirements/provider.md).

All times are built in local (Pacific) time, so the lunch and dinner peaks land at the
right hour; formats.utc_timestamp converts them to UTC when the files are written.
"""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import numpy as np

from provider import config
from provider.models import Customer, MenuItem, Order, OrderItem, Restaurant, World

LOCAL = ZoneInfo(config.TIMEZONE)


# --- time helpers -----------------------------------------------------------------

def start_of_day(day: date) -> datetime:
    """Local midnight at the start of a day, e.g. 2026-09-01 00:00 Pacific."""
    return datetime.combine(day, time(0, 0), tzinfo=LOCAL)


def random_moment(start: datetime, end: datetime, rng) -> datetime:
    """A random moment between start and end, rounded to whole milliseconds."""
    seconds = (end - start).total_seconds()
    moment = start + timedelta(seconds=float(rng.uniform(0, seconds)))
    return moment.replace(microsecond=moment.microsecond // 1000 * 1000)


def minutes(value: float) -> timedelta:
    return timedelta(minutes=float(value))


def weighted_choice(options: list, weights: list[float], rng):
    """Pick one option; an option with weight 2 is twice as likely as one with weight 1."""
    p = np.array(weights, dtype=float)
    return options[int(rng.choice(len(options), p=p / p.sum()))]


# --- customers --------------------------------------------------------------------

def create_customers(world: World, count: int, rng, fake,
                     signed_up_from: datetime, signed_up_to: datetime) -> list[Customer]:
    """Create `count` customers who signed up between the two times, and add them to the world.

    Signup times are generated first and sorted, so refs follow signup order
    (C0001 is the earliest customer).
    """
    signup_times = sorted(random_moment(signed_up_from, signed_up_to, rng) for _ in range(count))

    created = []
    for signed_up_at in signup_times:
        ref = world.new_customer_ref()
        customer = Customer(
            ref=ref,
            name=f"{fake.first_name()} {fake.last_name()}",
            email=fake.unique.safe_email(),
            phone=fake.numerify("##########"),
            address=fake.street_address(),
            city=str(rng.choice(config.CITIES)),
            signed_up_at=signed_up_at,
        )
        world.customers[ref] = customer
        created.append(customer)
    return created


def create_customers_for_day(world: World, day: date, is_first_day: bool, rng, fake) -> list[Customer]:
    """Day one: the partner's existing customers, who signed up during the previous year.
    Later days: 0-5 people who signed up that day."""
    if is_first_day:
        end = start_of_day(day)
        return create_customers(world, config.INITIAL_CUSTOMERS, rng, fake,
                                end - timedelta(days=365), end)
    lo, hi = config.NEW_CUSTOMERS_PER_DAY
    count = int(rng.integers(lo, hi + 1))
    return create_customers(world, count, rng, fake,
                            start_of_day(day), start_of_day(day + timedelta(days=1)))


# --- orders -----------------------------------------------------------------------

def orders_today(day: date, rng) -> int:
    """Base range from config, scaled up on busy days (Friday, Saturday)."""
    lo, hi = config.ORDERS_PER_DAY
    base = int(rng.integers(lo, hi + 1))
    return round(base * config.DAY_OF_WEEK_MULTIPLIER[day.weekday()])


def order_placed_at(day: date, rng) -> datetime:
    """An hour picked by HOURLY_WEIGHTS (lunch and dinner peaks), then a random moment in it."""
    hour = weighted_choice(list(config.HOURLY_WEIGHTS), list(config.HOURLY_WEIGHTS.values()), rng)
    start = start_of_day(day) + timedelta(hours=hour)
    return random_moment(start, start + timedelta(hours=1), rng)


def pick_restaurant(world: World, rng) -> Restaurant:
    """Cuisine first (by popularity), then one of that cuisine's open restaurants."""
    by_cuisine: dict[str, list[Restaurant]] = {}
    for restaurant in world.restaurants.values():
        if restaurant.active:
            by_cuisine.setdefault(restaurant.cuisine, []).append(restaurant)
    cuisines = list(by_cuisine)
    cuisine = weighted_choice(cuisines, [config.CUISINE_WEIGHTS[c] for c in cuisines], rng)
    options = by_cuisine[cuisine]
    return options[int(rng.integers(0, len(options)))]


def pick_items(world: World, restaurant: Restaurant, rng) -> list[OrderItem]:
    """1-4 different active dishes from this restaurant, with quantities by QUANTITY_WEIGHTS."""
    menu: list[MenuItem] = [m for m in world.menu_items.values()
                            if m.restaurant_ref == restaurant.ref and m.active]
    lo, hi = config.LINES_PER_ORDER
    lines = min(int(rng.integers(lo, hi + 1)), len(menu))
    picks = rng.choice(len(menu), size=lines, replace=False)

    quantities = list(config.QUANTITY_WEIGHTS)
    weights = list(config.QUANTITY_WEIGHTS.values())
    items = [OrderItem(item_ref=menu[int(i)].ref,
                       quantity=int(weighted_choice(quantities, weights, rng)),
                       unit_price=menu[int(i)].price)
             for i in picks]

    # Keep within the spec: at most MAX_TOTAL_QUANTITY items in total.
    while sum(item.quantity for item in items) > config.MAX_TOTAL_QUANTITY:
        biggest = max(items, key=lambda item: item.quantity)
        biggest.quantity -= 1
    return items


def cancel_probability(restaurant: Restaurant) -> float:
    """3% for the fastest restaurants, rising to 6% for the slowest."""
    lo, hi = config.PREP_MINUTES_MEAN_RANGE
    slowness = (restaurant.prep_minutes_mean - lo) / (hi - lo)        # 0 = fastest, 1 = slowest
    return config.CANCEL_RATE_BASE + config.CANCEL_RATE_SLOW_EXTRA * slowness


def build_order(world: World, ref: str, placed_at: datetime, rng) -> Order:
    """One order: who, from where, what, and its timeline (delivered or cancelled)."""
    restaurant = pick_restaurant(world, rng)

    # Only customers who had already signed up when the order was placed.
    customers = [c for c in world.customers.values() if c.signed_up_at <= placed_at]
    customer = customers[int(rng.integers(0, len(customers)))]

    order = Order(
        ref=ref,
        customer_ref=customer.ref,
        restaurant_ref=restaurant.ref,
        status="delivered",
        placed_at=placed_at,
        items=pick_items(world, restaurant, rng),
    )

    # Durations, never shorter than MIN_MINUTES.
    accept = float(rng.uniform(*config.ACCEPT_MINUTES))
    prep = max(config.MIN_MINUTES, float(rng.normal(restaurant.prep_minutes_mean, config.PREP_MINUTES_STD)))
    delivery = max(config.MIN_MINUTES, float(rng.normal(config.DELIVERY_MINUTES_MEAN, config.DELIVERY_MINUTES_STD)))

    if rng.random() < cancel_probability(restaurant):
        # Cancelled either before the restaurant accepted, or while it was preparing.
        # No driver had picked it up yet, so there's no driver and no later timestamps.
        order.status = "cancelled"
        if rng.random() < 0.5:
            order.cancelled_at = placed_at + minutes(rng.uniform(config.MIN_MINUTES, 10))
        else:
            order.accepted_at = placed_at + minutes(accept)
            order.cancelled_at = order.accepted_at + minutes(rng.uniform(config.MIN_MINUTES, prep))
        return order

    drivers = [d for d in world.drivers.values() if d.active]
    order.driver_ref = drivers[int(rng.integers(0, len(drivers)))].ref
    order.accepted_at = placed_at + minutes(accept)
    order.picked_up_at = order.accepted_at + minutes(prep)
    order.delivered_at = order.picked_up_at + minutes(delivery)
    return order


def create_orders(world: World, day: date, rng) -> list[Order]:
    """All orders placed on one (local) day, numbered in the order they were placed."""
    count = orders_today(day, rng)
    placed_times = sorted(order_placed_at(day, rng) for _ in range(count))
    return [build_order(world, config.ORDER_REF.format(day, n), placed_at, rng)
            for n, placed_at in enumerate(placed_times, start=1)]
