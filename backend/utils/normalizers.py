import re


def normalize_phone(phone: str) -> str:
    """Strip non-digits and keep last 10 digits (Indian mobile number format)."""
    digits = re.sub(r"\D", "", phone)
    return digits[-10:] if len(digits) >= 10 else digits


def normalize_amount(amount: str) -> str:
    """Strip currency symbols, commas, and whitespace. Return plain numeric string."""
    return re.sub(r"[₹$€£,\s]", "", amount)


def normalize_url(url: str) -> str:
    """Lowercase and strip trailing slashes."""
    return url.lower().rstrip("/")


def normalize_upi(upi: str) -> str:
    """Lowercase UPI IDs for consistent matching."""
    return upi.lower().strip()


def normalize_email(email: str) -> str:
    """Lowercase emails for consistent matching."""
    return email.lower().strip()


def normalize_entities(entities: dict) -> dict:
    """
    Apply normalization to every entity list in-place.
    After normalization, re-deduplicate since different formats
    may collapse to the same value (e.g. +91 9876543210 == 9876543210).
    """
    normalizers = {
        "phone_numbers":          normalize_phone,
        "amounts":                normalize_amount,
        "urls":                   normalize_url,
        "upi_ids":                normalize_upi,
        "emails":                 normalize_email,
    }

    for field, fn in normalizers.items():
        if field in entities and isinstance(entities[field], list):
            normalized = [fn(v) for v in entities[field] if v]
            # Deduplicate after normalization — order-preserving
            entities[field] = list(dict.fromkeys(v for v in normalized if v))

    return entities
