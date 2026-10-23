"""Checks for single fields (requirements/ingester.md, section 7.2).

Every check takes the text from the file and returns TWO things:

    value, error = validate.email("ann@example.com", "owner_email")

  - if the text is fine:   value = the cleaned value,  error = None
  - if it isn't:           value = None,               error = a message saying why
"""
import re
from datetime import date, datetime, timezone

# --- patterns ("regular expressions") ------------------------------------------------
# ^ means "start of the text" and $ means "end of the text", so the WHOLE value must match.

NAME = re.compile(r"^[A-Za-z][A-Za-z '\-]*$")        # a letter, then letters, spaces, ' or -
ADDRESS = re.compile(r"^[A-Za-z0-9 ,.#'\-]+$")       # letters, digits, spaces and , . # ' -
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")     # something@something.something
PHONE = re.compile(r"^\d{10}$")                       # exactly 10 digits
TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")   # 2026-10-19T19:05:00.000Z
PRICE = re.compile(r"^\d+(\.\d{1,2})?$")              # 9, 9.5 or 9.50

REF_PATTERNS = {
    "restaurant": re.compile(r"^R\d{3}$"),             # R007
    "menu_item": re.compile(r"^M\d{4}$"),              # M0071
    "driver": re.compile(r"^D\d{3}$"),                 # D003
    "customer": re.compile(r"^C\d{4}$"),               # C0042
    "order": re.compile(r"^O-\d{8}-\d{4}$"),           # O-20261019-0013
}


def required(text, field):
    """Returns an error message if the field is missing or empty, otherwise None."""
    if text is None or text.strip() == "":
        return f"{field} is required"
    return None


def ref(text, kind, field):
    """A partner ref of the given kind, e.g. kind='restaurant' for 'R007'."""
    if not REF_PATTERNS[kind].match(text):
        return None, f"{field} '{text}' is not a valid {kind} ref"
    return text, None


def pattern(text, rule, field):
    """Text that must match one of the patterns above, e.g. NAME or ADDRESS."""
    if not rule.match(text):
        return None, f"{field} '{text}' has characters that aren't allowed"
    return text, None


def email(text, field):
    if not EMAIL.match(text):
        return None, f"{field} '{text}' is not a valid email"
    return text.lower(), None            # store emails in lowercase, so matching is easy


def phone(text, field):
    if not PHONE.match(text):
        return None, f"{field} '{text}' must be exactly 10 digits"
    return text, None


def iso_date(text, field):
    """'2021-05-14' -> date(2021, 5, 14)"""
    try:
        return date.fromisoformat(text), None
    except ValueError:
        return None, f"{field} '{text}' is not a date (YYYY-MM-DD)"


def timestamp(text, field):
    """'2026-10-19T19:05:00.000Z' -> a timezone-aware datetime in UTC"""
    if not TIMESTAMP.match(text):
        return None, f"{field} '{text}' is not in the format YYYY-MM-DDTHH:MM:SS.sssZ"
    try:
        moment = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return None, f"{field} '{text}' is not a real date and time"
    return moment.replace(tzinfo=timezone.utc), None


def boolean(text, field):
    """'true' -> True, 'false' -> False"""
    if text == "true":
        return True, None
    if text == "false":
        return False, None
    return None, f"{field} '{text}' must be true or false"


def price(text, field, low=0.10, high=100.00):
    """A dollar amount with up to 2 decimals, between low and high."""
    if not PRICE.match(text):
        return None, f"{field} '{text}' is not a number with up to 2 decimals"
    value = float(text)
    if value < low or value > high:
        return None, f"{field} {text} is outside {low:.2f}-{high:.2f}"
    return value, None
