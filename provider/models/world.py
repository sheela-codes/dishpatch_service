from dataclasses import dataclass, field

from provider import config
from provider.models.customer import Customer
from provider.models.driver import Driver
from provider.models.menu_item import MenuItem
from provider.models.restaurant import Restaurant


@dataclass
class World:
    """Everything the partner has created so far, remembered across all days of one run.

    Each dictionary is keyed by ref ('R007' -> Restaurant). Records are never removed,
    only switched off (active = False), so refs are never reused.
    """

    restaurants: dict[str, Restaurant] = field(default_factory=dict)
    menu_items: dict[str, MenuItem] = field(default_factory=dict)
    drivers: dict[str, Driver] = field(default_factory=dict)
    customers: dict[str, Customer] = field(default_factory=dict)

    # --- next free ref for each kind of record ---------------------------------
    # Because nothing is ever removed, "how many exist + 1" is always unused.
    # Add the new record to its dictionary before asking for the next ref.

    def new_restaurant_ref(self) -> str:
        return config.RESTAURANT_REF.format(len(self.restaurants) + 1)   # 'R001', 'R002', ...

    def new_menu_item_ref(self) -> str:
        return config.MENU_ITEM_REF.format(len(self.menu_items) + 1)     # 'M0001', ...

    def new_driver_ref(self) -> str:
        return config.DRIVER_REF.format(len(self.drivers) + 1)           # 'D001', ...

    def new_customer_ref(self) -> str:
        return config.CUSTOMER_REF.format(len(self.customers) + 1)       # 'C0001', ...
