"""Pydantic schemas: the shapes of the data the API receives and sends back.

Models (src/app/models/) describe database rows.
Schemas describe JSON:
  - ...In / ...Create  what a client SENDS. FastAPI checks it automatically:
                       a missing field or a wrong type gets a 422 before your code runs.
  - ...Out             what the API SENDS BACK. Built from a model object, so the
                       response only contains the fields listed here (never a password).

Layer 1 only: onboarding and reading restaurants (see requirements/api.md).
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- what the client sends ------------------------------------------------------------

class OwnerIn(BaseModel):
    """The restaurant's owner, inside POST /restaurants."""
    name: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", example="sheela@dishpatch.com")    # something@something.something
    phone: str = Field(pattern=r"^\d{10}$")                       # exactly 10 digits


class MenuItemIn(BaseModel):
    """One dish, inside POST /restaurants."""
    name: str = Field(min_length=1)
    price: Decimal = Field(ge=Decimal("0.10"), le=Decimal("100.00"), decimal_places=2)  # $0.10 - $100.00


class RestaurantCreate(BaseModel):
    """The body of POST /restaurants: the restaurant, its owner and its menu in one request."""
    name: str = Field(min_length=1)
    cuisine: str                          # a cuisine name, e.g. "Thai"; the router looks up its id
    city: str = Field(min_length=1)
    opened_at: Optional[date] = None      # optional: may be left out
    owner: OwnerIn                        # a schema inside a schema = nested JSON
    menu_items: List[MenuItemIn] = Field(min_length=1)    # at least one dish

class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    cuisine: Optional[str] = None
    city: Optional[str] = Field(default=None, min_length=1)
    opened_at: Optional[date] = None
    add_menu_items: List[MenuItemIn] = []
    remove_menu_item_ids: List[int] = []    


# --- what the API sends back ------------------------------------------------------------
# from_attributes=True: these can be built straight from a model object, by reading its
# attributes (restaurant.name, restaurant.menu_items, ...).

class CuisineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class MenuItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal          # sent as "15.50": money stays exact
    active: bool


class RestaurantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cuisine: CuisineOut                   # filled from restaurant.cuisine (the relationship)
    city: str
    opened_at: Optional[date]
    operational: bool
    user_id: int                          # the owner's users.id
    menu_items: List[MenuItemOut]         # filled from restaurant.menu_items (the relationship)


# --- customers (Layer 3) ----------------------------------------------------------------

class CustomerCreate(BaseModel):
    """The body of POST /customers."""
    name: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", examples=["maya@example.com"])
    phone: str = Field(pattern=r"^\d{10}$", examples=["4255550101"])
    address: str = Field(min_length=1)
    city: str = Field(min_length=1)


class CustomerOut(BaseModel):
    """What the customer endpoints send back. The router builds it by hand from
    user -> account -> profile -> contact."""
    id: int                     # users.id
    name: str
    account_type:str
    email: str
    phone: str
    address: Optional[str]      # imported customers may have none
    city: Optional[str]


# --- orders (Layer 3) -------------------------------------------------------------------

class OrderItemIn(BaseModel):
    """One line of an order: which dish and how many."""
    menu_item_id: int
    quantity: int = Field(ge=1)              # at least 1


class OrderCreate(BaseModel):
    """The body of POST /orders. No prices here: the router takes them from the database."""
    customer_id: int
    restaurant_id: int
    items: List[OrderItemIn] = Field(min_length=1)


class OrderItemOut(BaseModel):
    menu_item_id: int
    name: str                    # the dish's name, so the response is readable
    quantity: int
    unit_price: Decimal          # the price when the order was placed


class OrderOut(BaseModel):
    """What the order endpoints send back. The router builds it by hand
    (total is not a column, it is computed)."""
    id: int
    customer_id: int
    restaurant_id: int
    status: str                  # "placed" for a new order
    placed_at: datetime
    items: List[OrderItemOut]
    total: Decimal               # sum of quantity x unit_price
