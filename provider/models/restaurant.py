from dataclasses import dataclass
from datetime import date


@dataclass
class Restaurant:
    """One restaurant as the partner knows it: one row of reference/restaurants.csv."""

    # --- written to restaurants.csv ---
    ref: str               # partner ID, e.g. 'R007'; never changes, never reused
    name: str              # 'Taco Loco'
    cuisine: str           # one of config.CUISINE_WEIGHTS, e.g. 'Mexican'
    city: str              # one of config.CITIES
    opened_at: date
    owner_name: str        # the owner travels with the restaurant in the file;
    owner_email: str       # the ingester turns these three into a user account
    owner_phone: str       # exactly 10 digits

    # --- hidden: used by the generator, never written to a file ---
    prep_minutes_mean: float   # this restaurant's typical prep time (its "speed")

    # --- written to restaurants.csv ---
    active: bool = True    # False = closed; fields with defaults must come last

    # Column order of restaurants.csv. Shared by the CSV header and to_row().
    CSV_COLUMNS = (
        "restaurant_ref", "name", "cuisine", "city", "opened_at",
        "owner_name", "owner_email", "owner_phone", "active",
    )

    def to_row(self) -> dict:
        """This restaurant as one CSV row, in the partner's file format."""
        return {
            "restaurant_ref": self.ref,
            "name": self.name,
            "cuisine": self.cuisine,
            "city": self.city,
            "opened_at": self.opened_at.isoformat(),        # 2021-05-14
            "owner_name": self.owner_name,
            "owner_email": self.owner_email,
            "owner_phone": self.owner_phone,
            "active": "true" if self.active else "false",   # spec: lowercase true/false
        }
