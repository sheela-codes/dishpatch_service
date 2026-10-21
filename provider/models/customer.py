from dataclasses import dataclass
from datetime import datetime

from provider.formats import utc_timestamp


@dataclass
class Customer:
    """One customer who signed up: one row of activity/customers.csv."""

    ref: str                 # partner ID, e.g. 'C0042'
    name: str                # first + last name only (no 'Dr.' or 'Jr.')
    email: str
    phone: str               # exactly 10 digits
    address: str             # street address, e.g. '1234 Pine St Apt 5'
    city: str                # one of config.CITIES
    signed_up_at: datetime   # timezone-aware; written to the file in UTC

    # Column order of customers.csv. Shared by the CSV header and to_row().
    CSV_COLUMNS = (
        "customer_ref", "name", "email", "phone", "address", "city", "signed_up_at",
    )

    def to_row(self) -> dict:
        """This customer as one CSV row, in the partner's file format."""
        return {
            "customer_ref": self.ref,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "signed_up_at": utc_timestamp(self.signed_up_at),   # 2026-10-19T16:12:00.000Z
        }
