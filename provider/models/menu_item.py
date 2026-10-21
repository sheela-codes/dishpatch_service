from dataclasses import dataclass

@dataclass
class MenuItem:
    ref: str # Menu Id
    restaurant_ref: str 
    name: str
    price: float
    active: bool = True 


    # Column order of menu_items.csv. Shared by the CSV header and to_row().
    CSV_COLUMNS = (
        "item_ref", "restaurant_ref",  "name", "price", "active",
    )

    def to_row(self) -> dict:

        return {
            "item_ref": self.ref,
            "restaurant_ref": self.restaurant_ref,
            "name": self.name,
            "price": f"{self.price:.2f}",
            "active": "true" if self.active else "false"   # spec: lowercase true/false
        }
