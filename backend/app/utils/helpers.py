"""Small shared helpers used across the backend."""

import re
import uuid


def slugify(value: str) -> str:
    """Turns a display name into a URL/DB-safe slug, e.g. 'Technify HQ' -> 'technify-hq'."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or f"org-{uuid.uuid4().hex[:8]}"