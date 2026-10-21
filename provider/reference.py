from datetime import date, timedelta

from provider import config
from provider.models import Restaurant, World
import random


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
                opened_at = start + timedelta(days=int(rng.integers(0, (end - start).days + 1)))
            )
            world.restaurants[ref] = restaurant
            created.append(restaurant)
    return created


