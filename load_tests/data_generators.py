"""
Data generators for Locust load tests.
Produces unique emails, usernames, passwords, image payloads,
and description text for each simulated user.
"""

import random
import string
import time
from io import BytesIO

from PIL import Image


def _random_alphanumeric(length: int) -> str:
    """Generate a random alphanumeric string of the requested length."""
    if length < 1:
        raise ValueError("length must be greater than 0")

    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))


def generate_username(length: int = 12) -> str:
    """Generate an alphanumeric username."""
    return _random_alphanumeric(length)


def generate_password(length: int = 16) -> str:
    """Generate an alphanumeric password."""
    return _random_alphanumeric(length)


def generate_email(domain: str = "loadtest.local") -> str:
    """Generate a likely-unique email using a timestamp and random suffix."""
    timestamp = int(time.time() * 1000)
    local_part = f"u{timestamp}{_random_alphanumeric(6)}"
    return f"{local_part}@{domain}"


def generate_description(length: int = 200) -> str:
    """Generate a realistic-length description string."""
    words = [_random_alphanumeric(random.randint(3, 10)) for _ in range(length // 5)]
    return " ".join(words)[:length]


# ---------------------------------------------------------------------------
# Image generators
# ---------------------------------------------------------------------------

def random_png_bytes(width: int = 512, height: int = 512) -> bytes:
    """
    Generate random-pixel PNG bytes (~500-700 KB).
    Used for large data-size mode.
    """
    image = Image.new("RGB", (width, height))
    pixels = [
        (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        for _ in range(width * height)
    ]
    image.putdata(pixels)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def random_jpeg_bytes(width: int = 64, height: int = 64, quality: int = 50) -> bytes:
    """
    Generate a small random-pixel JPEG (~8-12 KB).
    Used for small data-size mode when we still want to
    exercise the profile-photo endpoint with minimal payload.
    """
    image = Image.new("RGB", (width, height))
    pixels = [
        (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        for _ in range(width * height)
    ]
    image.putdata(pixels)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()
