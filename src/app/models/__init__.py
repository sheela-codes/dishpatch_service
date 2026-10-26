# Import every model here, so SQLAlchemy always knows all of them
# (relationship("Cuisine") etc. only work if the class has been imported).
from src.app.models.cuisine import Cuisine
from src.app.models.restaurant import Restaurant
from src.app.models.contact import Contact
from src.app.models.profile import Profile
from src.app.models.account import Account
from src.app.models.user import User
from src.app.models.menu_item import MenuItem
from src.app.models.order import Order
from src.app.models.order_item import OrderItem
