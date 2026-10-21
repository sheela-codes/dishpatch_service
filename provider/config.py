"""Settings and fixed lists for the pretend partner.

Data only: no functions, no randomness. The other provider modules read from here,
so changing the size or shape of the generated data means changing this file.
"""
from datetime import date

# --- partner ----------------------------------------------------------------

PARTNER = "redmondtownservice"   # also the folder name under data/incoming/
TIMEZONE = "America/Los_Angeles" # local time for patterns; files are written in UTC

# --- refs (partner IDs) ---------------------------------------------------------
# Formats from requirements/provider.md. Use like RESTAURANT_REF.format(7) -> "R007".

RESTAURANT_REF = "R{:03d}"
MENU_ITEM_REF  = "M{:04d}"
DRIVER_REF     = "D{:03d}"
CUSTOMER_REF   = "C{:04d}"
ORDER_REF      = "O-{:%Y%m%d}-{:04d}"   # ORDER_REF.format(day, 13) -> "O-20261019-0013"

# --- cuisines ---------------------------------------------------------------------
# Names must match the cuisines table in src/data/sql/dishpatch.sql.
# Weight = relative popularity: a weight of 1.4 gets 40% more orders than 1.0.

CUISINE_WEIGHTS = {
    "American":      1.4,
    "Chinese":       1.1,
    "Indian":        1.0,
    "Italian":       1.3,
    "Japanese":      0.9,
    "Mediterranean": 0.7,
    "Mexican":       1.2,
    "Thai":          0.8,
}

# --- cities -------------------------------------------------------------------------
# A short fixed list, so "by city" charts have a few meaningful groups.

CITIES = ["Seattle", "Redmond", "Bellevue", "Kirkland"]

# --- restaurants --------------------------------------------------------------------
# Two per cuisine -> 16 restaurants. Names use only letters, spaces, ' and -.

RESTAURANT_NAMES = {
    "American":      ["Liberty Burger", "Main Street Diner"],
    "Chinese":       ["Golden Dragon", "Jade Garden"],
    "Indian":        ["Curry House", "Spice Route"],
    "Italian":       ["Bella Napoli", "Trattoria Roma"],
    "Japanese":      ["Sakura Sushi", "Ramen Hana"],
    "Mediterranean": ["Olive Tree", "Aegean Kitchen"],
    "Mexican":       ["Taco Loco", "Casa Verde"],
    "Thai":          ["Thai Basil", "Bangkok Street"],
}

OPENED_BETWEEN = (date(2012, 1, 1), date(2025, 12, 31))   # range for opened_at

# --- menus ----------------------------------------------------------------------------
# Each cuisine has a pool of dishes with a base price in dollars.
# Each restaurant picks MENU_ITEMS_PER_RESTAURANT of them and nudges the price
# by up to MENU_PRICE_JITTER (e.g. 0.10 = +/-10%), so the two restaurants differ.

MENU_ITEMS_PER_RESTAURANT = (10, 15)   # min, max (inclusive)
MENU_PRICE_JITTER = 0.10

MENUS = {
    "American": [
        ("Classic Cheeseburger", 12.50), ("Bacon Burger", 14.00), ("Veggie Burger", 12.00),
        ("Chicken Sandwich", 11.50), ("BBQ Pulled Pork", 13.50), ("Buffalo Wings", 11.00),
        ("Cobb Salad", 12.00), ("Mac and Cheese", 9.00), ("French Fries", 4.50),
        ("Onion Rings", 5.50), ("Sweet Potato Fries", 5.50), ("Clam Chowder", 7.50),
        ("Apple Pie", 6.00), ("Chocolate Milkshake", 6.50), ("Lemonade", 3.50),
    ],
    "Chinese": [
        ("Kung Pao Chicken", 14.00), ("General Tso's Chicken", 14.50), ("Beef and Broccoli", 15.50),
        ("Sweet and Sour Pork", 14.00), ("Mapo Tofu", 12.50), ("Chow Mein", 12.00),
        ("Fried Rice", 11.00), ("Hot and Sour Soup", 6.50), ("Wonton Soup", 7.00),
        ("Pork Dumplings", 9.00), ("Spring Rolls", 6.50), ("Orange Chicken", 14.00),
        ("Szechuan Green Beans", 10.50), ("Egg Drop Soup", 6.00), ("Jasmine Tea", 3.00),
    ],
    "Indian": [
        ("Chicken Tikka Masala", 16.50), ("Butter Chicken", 16.50), ("Lamb Rogan Josh", 18.50),
        ("Palak Paneer", 14.50), ("Chana Masala", 13.00), ("Vegetable Biryani", 14.00),
        ("Chicken Biryani", 16.00), ("Dal Makhani", 12.50), ("Samosas", 7.00),
        ("Garlic Naan", 4.00), ("Plain Naan", 3.50), ("Basmati Rice", 3.50),
        ("Mango Lassi", 5.00), ("Gulab Jamun", 5.50), ("Masala Chai", 3.50),
    ],
    "Italian": [
        ("Margherita Pizza", 15.00), ("Pepperoni Pizza", 16.50), ("Spaghetti Carbonara", 17.00),
        ("Fettuccine Alfredo", 16.00), ("Lasagna", 18.00), ("Penne Arrabbiata", 15.00),
        ("Chicken Parmesan", 19.00), ("Mushroom Risotto", 18.50), ("Caesar Salad", 11.00),
        ("Caprese Salad", 12.00), ("Garlic Bread", 6.00), ("Minestrone", 7.50),
        ("Tiramisu", 8.00), ("Cannoli", 6.50), ("Espresso", 3.50),
    ],
    "Japanese": [
        ("Salmon Nigiri", 9.00), ("Tuna Roll", 8.50), ("California Roll", 8.00),
        ("Spicy Tuna Roll", 9.50), ("Dragon Roll", 15.00), ("Tonkotsu Ramen", 16.00),
        ("Miso Ramen", 15.00), ("Chicken Teriyaki", 15.50), ("Beef Udon", 15.50),
        ("Vegetable Tempura", 11.00), ("Gyoza", 8.00), ("Edamame", 5.00),
        ("Miso Soup", 3.50), ("Seaweed Salad", 6.00), ("Green Tea", 3.00),
    ],
    "Mediterranean": [
        ("Chicken Shawarma Plate", 16.00), ("Lamb Gyro", 13.50), ("Falafel Wrap", 11.50),
        ("Beef Kofta", 17.00), ("Chicken Souvlaki", 15.50), ("Moussaka", 17.50),
        ("Spanakopita", 10.00), ("Greek Salad", 11.50), ("Hummus and Pita", 8.00),
        ("Baba Ganoush", 8.50), ("Tabbouleh", 7.50), ("Lentil Soup", 7.00),
        ("Stuffed Grape Leaves", 8.50), ("Baklava", 6.00), ("Mint Lemonade", 4.50),
    ],
    "Mexican": [
        ("Carne Asada Tacos", 13.50), ("Chicken Tacos", 12.00), ("Fish Tacos", 13.00),
        ("Carnitas Burrito", 13.50), ("Bean and Cheese Burrito", 10.50), ("Chicken Quesadilla", 12.00),
        ("Beef Enchiladas", 14.50), ("Chicken Fajitas", 17.00), ("Tamales", 11.00),
        ("Pozole", 13.00), ("Chips and Guacamole", 8.00), ("Chips and Salsa", 5.00),
        ("Elote", 5.50), ("Churros", 6.00), ("Horchata", 4.00),
    ],
    "Thai": [
        ("Pad Thai", 14.50), ("Pad See Ew", 14.50), ("Drunken Noodles", 15.00),
        ("Green Curry", 15.50), ("Red Curry", 15.50), ("Massaman Curry", 16.00),
        ("Panang Curry", 15.50), ("Thai Basil Chicken", 14.00), ("Pineapple Fried Rice", 14.50),
        ("Tom Yum Soup", 8.50), ("Tom Kha Soup", 8.50), ("Fresh Spring Rolls", 7.50),
        ("Papaya Salad", 9.50), ("Mango Sticky Rice", 8.00), ("Thai Iced Tea", 4.50),
    ],
}

# --- people -------------------------------------------------------------------------------

NUM_DRIVERS = 15
INITIAL_CUSTOMERS = 100              # on day one
NEW_CUSTOMERS_PER_DAY = (0, 5)       # min, max new signups on later days

# --- orders: volume ----------------------------------------------------------------------

ORDERS_PER_DAY = (25, 45)            # typical weekday range
DAY_OF_WEEK_MULTIPLIER = {           # Monday = 0 ... Sunday = 6
    0: 0.9, 1: 0.9, 2: 1.0, 3: 1.0, 4: 1.3, 5: 1.4, 6: 1.1,
}

# Share of a day's orders placed in each local hour (10:00 to 21:59).
# Peaks at lunch (11-13) and dinner (18-21). Values are relative, not percentages.
HOURLY_WEIGHTS = {
    10: 2, 11: 8, 12: 12, 13: 7, 14: 3, 15: 2,
    16: 3, 17: 7, 18: 12, 19: 13, 20: 9, 21: 4,
}

# --- orders: contents --------------------------------------------------------------------

LINES_PER_ORDER = (1, 4)             # different dishes in one order
QUANTITY_WEIGHTS = {1: 75, 2: 20, 3: 5}  # how many of each dish
MAX_TOTAL_QUANTITY = 12              # all quantities in one order added up
ORDER_TOTAL_RANGE = (1.00, 1000.00)  # dollars
MENU_PRICE_RANGE = (0.10, 100.00)    # dollars

# --- orders: timing (minutes) --------------------------------------------------------------
# Each restaurant gets its own typical prep time when it's created, picked from
# PREP_MINUTES_MEAN_RANGE; some restaurants end up consistently slow.

ACCEPT_MINUTES = (1, 6)                  # placed -> accepted
PREP_MINUTES_MEAN_RANGE = (10, 28)       # per-restaurant average, accepted -> picked up
PREP_MINUTES_STD = 4                     # day-to-day variation around that average
DELIVERY_MINUTES_MEAN = 18               # picked up -> delivered
DELIVERY_MINUTES_STD = 6
MIN_MINUTES = 1                          # durations are never shorter than this

# --- orders: cancellations -------------------------------------------------------------------

CANCEL_RATE_BASE = 0.03                  # 3% for a fast restaurant
CANCEL_RATE_SLOW_EXTRA = 0.03            # up to +3% more for the slowest restaurants

# --- reference changes on later days ---------------------------------------------------------
# Chance per day that each kind of change happens.

CHANGE_PROBABILITY = {
    "menu_price_change": 0.15,   # one dish gets a new price
    "menu_item_removed": 0.05,   # one dish is switched off
    "menu_item_added":   0.05,   # one new dish from the cuisine's pool
    "driver_joins":      0.05,
    "driver_leaves":     0.03,
}
