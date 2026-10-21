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


            