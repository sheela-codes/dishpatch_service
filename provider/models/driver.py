from dataclasses import dataclass

@dataclass
class Driver:
    ref: str 
    name: str
    email: str
    phone: str
    city: str
    active: bool = True 


    # Column order of drivers.csv. Shared by the CSV header and to_row().
    CSV_COLUMNS = (
        "driver_ref", "name", "email", "phone", "city", "active",
    )

    def to_row(self) -> dict:

        return {
            "driver_ref": self.ref,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "active": "true" if self.active else "false"   # spec: lowercase true/false
        }
