from datetime import timedelta

from provider import config
from provider.models import Restaurant, World, MenuItem, Driver


def create_restaurants(world: World, rng, fake) -> list[Restaurant]:
    """Day one: create every restaurant in config.RESTAURANT_NAMES and add it to the world."""
    start, end = config.OPENED_BETWEEN
    range_days = (end - start).days  
    created = []
    for cuisine, names in config.RESTAURANT_NAMES.items():
        for name in names:
            ref = world.new_restaurant_ref()
            # build the Restaurant
            restaurant = Restaurant(
                ref = ref,
                name = name,
                city = str(rng.choice(config.CITIES)),
                owner_name = f"{fake.first_name()} {fake.last_name()}",
                owner_email = fake.unique.safe_email(),
                owner_phone = fake.numerify("##########"),
                prep_minutes_mean = round(float(rng.uniform(*config.PREP_MINUTES_MEAN_RANGE)), 1),
                cuisine = cuisine,
                opened_at = start + timedelta(days=int(rng.integers(0, (end - start).days + 1))),
            )
            world.restaurants[ref] = restaurant
            created.append(restaurant)
    return created


def create_menu_items(world: World, rng) -> list[MenuItem]:
    jitter = config.MENU_PRICE_JITTER
    lo, hi = config.MENU_ITEMS_PER_RESTAURANT
    created_mi = []
    for restaurant in world.restaurants.values():
        count = int(rng.integers(lo, hi + 1))
        all_menu_items = config.MENUS[restaurant.cuisine]
        indexes_menu_items_chosen = rng.choice(len(all_menu_items), size=count, replace=False) #holds positions [7, 0, 12, …]
        
        for index in indexes_menu_items_chosen:
            
            dish_name, base_price = all_menu_items[int(index)]
            ref = world.new_menu_item_ref()
            menu_item = MenuItem(
                ref = ref,
                restaurant_ref= restaurant.ref,      
                name = dish_name,
                price = round(base_price * float(rng.uniform(1 - jitter, 1 + jitter)), 2),
            )
            world.menu_items[ref] = menu_item
            created_mi.append(menu_item)
    return created_mi  

def create_drivers(world: World, rng, fake) -> list[Driver]:
    num_drivers = config.NUM_DRIVERS
    drivers_created = []
    for _ in range(num_drivers):
        ref = world.new_driver_ref()
        driver = Driver(
            ref = ref,
            name = f"{fake.first_name()} {fake.last_name()}",
            email = fake.unique.safe_email(),
            city = str(rng.choice(config.CITIES)),
            phone = fake.numerify("##########"),
        )
        world.drivers[ref] = driver
        drivers_created.append(driver)
    return drivers_created    


            

# --- later days: changes ---------------------------------------------------------

MIN_ACTIVE_DISHES_PER_RESTAURANT = 8   # never remove dishes below this
MIN_ACTIVE_DRIVERS = 10                # never let drivers leave below this


def _happens(kind: str, rng) -> bool:
    """True with the daily chance in config.CHANGE_PROBABILITY, e.g. 15% for a price change."""
    return bool(rng.random() < config.CHANGE_PROBABILITY[kind])


def _pick(options: list, rng):
    return options[int(rng.integers(0, len(options)))]


def _unique(records: list) -> list:
    """Each changed record once, even if it changed twice today (its current state is what's written)."""
    seen = {}
    for record in records:
        seen[record.ref] = record
    return list(seen.values())


def change_menu_price(world: World, rng) -> list[MenuItem]:
    """One active dish gets a new price: mostly increases (-5% to +15%), kept within the allowed range."""
    active = [m for m in world.menu_items.values() if m.active]
    item = _pick(active, rng)
    lo, hi = config.MENU_PRICE_RANGE
    new_price = round(min(hi, max(lo, item.price * float(rng.uniform(0.95, 1.15)))), 2)
    if new_price == item.price:
        return []
    item.price = new_price
    return [item]


def remove_menu_item(world: World, rng) -> list[MenuItem]:
    """Switch one dish off, but only at a restaurant that still has plenty of dishes left."""
    candidates = []
    for restaurant in world.restaurants.values():
        menu = [m for m in world.menu_items.values() if m.restaurant_ref == restaurant.ref and m.active]
        if len(menu) > MIN_ACTIVE_DISHES_PER_RESTAURANT:
            candidates.extend(menu)
    if not candidates:
        return []
    item = _pick(candidates, rng)
    item.active = False
    return [item]


def add_menu_item(world: World, rng) -> list[MenuItem]:
    """A restaurant adds a dish from its cuisine's pool that it has never had on its menu."""
    restaurant = _pick([r for r in world.restaurants.values() if r.active], rng)
    on_menu = {m.name for m in world.menu_items.values() if m.restaurant_ref == restaurant.ref}
    new_dishes = [(name, price) for name, price in config.MENUS[restaurant.cuisine] if name not in on_menu]
    if not new_dishes:
        return []
    dish_name, base_price = _pick(new_dishes, rng)
    jitter = config.MENU_PRICE_JITTER
    ref = world.new_menu_item_ref()
    item = MenuItem(
        ref=ref,
        restaurant_ref=restaurant.ref,
        name=dish_name,
        price=round(base_price * float(rng.uniform(1 - jitter, 1 + jitter)), 2),
    )
    world.menu_items[ref] = item
    return [item]


def driver_joins(world: World, rng, fake) -> list[Driver]:
    """A new driver starts."""
    ref = world.new_driver_ref()
    driver = Driver(
        ref=ref,
        name=f"{fake.first_name()} {fake.last_name()}",
        email=fake.unique.safe_email(),
        phone=fake.numerify("##########"),
        city=str(rng.choice(config.CITIES)),
    )
    world.drivers[ref] = driver
    return [driver]


def driver_leaves(world: World, rng) -> list[Driver]:
    """An active driver leaves (switched off, never deleted), unless too few would remain."""
    active = [d for d in world.drivers.values() if d.active]
    if len(active) <= MIN_ACTIVE_DRIVERS:
        return []
    driver = _pick(active, rng)
    driver.active = False
    return [driver]


def make_reference_changes(world: World, rng, fake):
    """Later days: maybe change some reference data. Returns (restaurants, menu_items, drivers),
    each a list of the records that changed today; usually all three are empty.

    The records are changed in the world itself, so today's orders already use the new prices
    and skip removed dishes and departed drivers.
    """
    menu_items: list[MenuItem] = []
    drivers: list[Driver] = []

    if _happens("menu_price_change", rng):
        menu_items += change_menu_price(world, rng)
    if _happens("menu_item_removed", rng):
        menu_items += remove_menu_item(world, rng)
    if _happens("menu_item_added", rng):
        menu_items += add_menu_item(world, rng)
    if _happens("driver_joins", rng):
        drivers += driver_joins(world, rng, fake)
    if _happens("driver_leaves", rng):
        drivers += driver_leaves(world, rng)

    restaurants: list[Restaurant] = []   # restaurants don't change in this version
    return restaurants, _unique(menu_items), _unique(drivers)
